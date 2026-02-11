"""
Admin API — MapaGov

Endpoints para aprovação/rejeição de cadastros externos,
listagem de pendentes e auditoria.
"""

import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from processos.api.auth_serializers import PendingUserSerializer, VoteSerializer
from processos.models_auth import (
    UserProfile,
    AccessApproval,
    is_approver,
    process_vote,
)
from processos.infra.rate_limiting import get_client_ip

logger = logging.getLogger('processos')


# ============================================================================
# PERMISSION CHECK
# ============================================================================

def _check_approver(request):
    """Retorna Response de erro se usuario nao e aprovador, ou None se ok."""
    if not is_approver(request.user):
        return Response(
            {'erro': 'Acesso restrito a aprovadores.'},
            status=status.HTTP_403_FORBIDDEN,
        )
    return None


def _log_audit(user, action, description, request=None):
    try:
        from processos.models_new.audit_log import AuditLog
        AuditLog.log_action(
            user=user,
            action=action,
            resource='auth',
            description=description,
            ip_address=get_client_ip(request) if request else '0.0.0.0',
            user_agent=request.META.get('HTTP_USER_AGENT', '') if request else '',
        )
    except Exception as e:
        logger.error(f"Erro ao registrar audit log: {e}")


def _get_frontend_url():
    if settings.DEBUG:
        return 'http://localhost:5173'
    return settings.CSRF_TRUSTED_ORIGINS[0] if settings.CSRF_TRUSTED_ORIGINS else ''


# ============================================================================
# ENDPOINTS
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_pending(request):
    """Lista cadastros pendentes de aprovação."""
    denied = _check_approver(request)
    if denied:
        return denied

    qs = UserProfile.objects.filter(
        access_status='pending',
        profile_type='externo',
    ).select_related('user', 'area', 'orgao').prefetch_related('approvals__admin')

    # Filtros opcionais
    domain = request.GET.get('domain')
    if domain:
        qs = qs.filter(user__email__icontains=domain)

    area = request.GET.get('area')
    if area:
        qs = qs.filter(area__codigo=area)

    qs = qs.order_by('-created_at')
    serializer = PendingUserSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cast_vote(request, user_id):
    """Registra voto de aprovação/rejeição para um cadastro pendente."""
    denied = _check_approver(request)
    if denied:
        return denied

    serializer = VoteSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    try:
        profile = UserProfile.objects.select_related('user').get(
            id=user_id,
            profile_type='externo',
        )
    except UserProfile.DoesNotExist:
        return Response({'erro': 'Usuario nao encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    if profile.access_status != 'pending':
        return Response(
            {'erro': f'Usuario ja foi {profile.get_access_status_display().lower()}.'},
            status=status.HTTP_409_CONFLICT,
        )

    # Verificar se ja votou
    if AccessApproval.objects.filter(user_profile=profile, admin=request.user).exists():
        return Response(
            {'erro': 'Voce ja votou para este usuario.'},
            status=status.HTTP_409_CONFLICT,
        )

    # Registrar voto
    vote_value = serializer.validated_data['vote']
    AccessApproval.objects.create(
        user_profile=profile,
        admin=request.user,
        vote=vote_value,
        justificativa=serializer.validated_data.get('justificativa', ''),
    )

    action = 'access_approve' if vote_value == 'approve' else 'access_reject'
    _log_audit(
        request.user, action,
        f'{request.user.email} votou {vote_value} para {profile.user.email}',
        request,
    )

    # Processar votação (pode aprovar/rejeitar automaticamente)
    result = process_vote(profile)

    if result == 'approved':
        _send_access_approved_email(profile.user)
        _log_audit(
            profile.user, 'access_approve',
            f'Acesso aprovado para {profile.user.email} (3 votos)',
            request,
        )
    elif result == 'rejected':
        _send_access_rejected_email(profile.user)
        _log_audit(
            profile.user, 'access_reject',
            f'Acesso rejeitado para {profile.user.email} (2 rejeicoes)',
            request,
        )

    # Reload para retornar status atualizado
    profile.refresh_from_db()

    return Response({
        'mensagem': f'Voto registrado: {vote_value}.',
        'access_status': profile.access_status,
        'result': result,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail(request, user_id):
    """Detalhe de um usuario com historico de votos."""
    denied = _check_approver(request)
    if denied:
        return denied

    try:
        profile = UserProfile.objects.select_related('user', 'area', 'orgao').get(id=user_id)
    except UserProfile.DoesNotExist:
        return Response({'erro': 'Usuario nao encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = PendingUserSerializer(profile)
    data = serializer.data
    data['can_access'] = profile.can_access
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audit_log(request):
    """Lista eventos de auditoria de auth (somente superusers)."""
    if not request.user.is_superuser:
        return Response(
            {'erro': 'Acesso restrito a superusers.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        from processos.models_new.audit_log import AuditLog
        logs = AuditLog.objects.filter(
            resource='auth',
        ).order_by('-timestamp')[:100]

        data = [
            {
                'id': log.id,
                'username': log.username,
                'action': log.action,
                'description': log.description,
                'ip_address': log.ip_address,
                'timestamp': log.timestamp.isoformat(),
                'success': log.success,
            }
            for log in logs
        ]
        return Response(data)
    except Exception as e:
        logger.error(f"Erro ao buscar audit log: {e}")
        return Response({'erro': 'Erro ao buscar logs.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# EMAIL NOTIFICATIONS
# ============================================================================

def _send_access_approved_email(user):
    """Notifica usuario que seu acesso foi aprovado."""
    frontend_url = _get_frontend_url()
    try:
        send_mail(
            subject='MapaGov — Acesso aprovado',
            message=render_to_string('email/access_approved.txt', {
                'user': user,
                'login_url': f"{frontend_url}/login",
            }),
            html_message=render_to_string('email/access_approved.html', {
                'user': user,
                'login_url': f"{frontend_url}/login",
            }),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
    except Exception as e:
        logger.error(f"Erro ao enviar email de aprovacao: {e}")


def _send_access_rejected_email(user):
    """Notifica usuario que seu acesso foi rejeitado."""
    try:
        send_mail(
            subject='MapaGov — Cadastro não aprovado',
            message=render_to_string('email/access_rejected.txt', {
                'user': user,
            }),
            html_message=render_to_string('email/access_rejected.html', {
                'user': user,
            }),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
    except Exception as e:
        logger.error(f"Erro ao enviar email de rejeicao: {e}")
