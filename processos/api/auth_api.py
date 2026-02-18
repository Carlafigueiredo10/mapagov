"""
Auth API — MapaGov

Endpoints de registro, login, logout, verificação de email,
recuperação de senha e consulta de perfil.

Proteção real no backend: DRF permissions + rate limiting.
"""

import logging

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.middleware.csrf import get_token
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from processos.api.auth_serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserProfileSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
)
from processos.models_auth import (
    UserProfile,
    is_mgi_email,
    is_approver,
    get_or_create_profile,
)
from processos.infra.rate_limiting import rate_limit_ip, get_client_ip

logger = logging.getLogger('processos')


# ============================================================================
# HELPERS
# ============================================================================

def _get_frontend_url():
    """URL base do frontend para links em emails."""
    if settings.DEBUG:
        return 'http://localhost:5173'
    return settings.CSRF_TRUSTED_ORIGINS[0] if settings.CSRF_TRUSTED_ORIGINS else ''


def _send_verification_email(user):
    """Envia email de verificação com link tokenizado."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    frontend_url = _get_frontend_url()
    verify_url = f"{frontend_url}/verificar-email/{uid}/{token}"

    try:
        send_mail(
            subject='MapaGov — Verifique seu email',
            message=render_to_string('email/email_verification.txt', {
                'user': user,
                'verify_url': verify_url,
            }),
            html_message=render_to_string('email/email_verification.html', {
                'user': user,
                'verify_url': verify_url,
            }),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Erro ao enviar email de verificacao para {user.email}: {e}")


def _notify_approvers_new_registration(user):
    """Notifica aprovadores sobre novo cadastro externo."""
    approvers = User.objects.filter(
        is_active=True,
    ).filter(
        models_Q_superuser_or_group()
    ).distinct()

    if not approvers.exists():
        logger.warning("Nenhum aprovador ativo encontrado para notificar.")
        return

    frontend_url = _get_frontend_url()
    admin_url = f"{frontend_url}/admin/usuarios"

    for approver in approvers:
        try:
            send_mail(
                subject='MapaGov — Novo cadastro pendente de aprovação',
                message=render_to_string('email/admin_new_registration.txt', {
                    'approver': approver,
                    'new_user': user,
                    'admin_url': admin_url,
                }),
                html_message=render_to_string('email/admin_new_registration.html', {
                    'approver': approver,
                    'new_user': user,
                    'admin_url': admin_url,
                }),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[approver.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Erro ao notificar aprovador {approver.email}: {e}")


def _notify_authorization_email(user, profile):
    """Envia solicitacao de autorizacao para mapagov.gestao@gmail.com."""
    from django.core.mail import EmailMessage

    setor = profile.setor_trabalho or '(nao informado)'
    area_nome = profile.area.nome_curto if profile.area else '(nao informada)'
    vinculacao = 'Decipex' if profile.is_decipex else 'Externo'

    frontend_url = _get_frontend_url()
    admin_url = f"{frontend_url}/admin/usuarios"

    try:
        msg = EmailMessage(
            subject='[MapaGov] Solicitacao de acesso externo',
            body=(
                f'Nova solicitacao de cadastro no MapaGov.\n\n'
                f'Nome: {profile.nome_completo}\n'
                f'Email: {user.email}\n'
                f'Vinculacao: {vinculacao}\n'
                f'Area/Setor: {area_nome if profile.is_decipex else setor}\n'
                f'Data: {profile.created_at.strftime("%d/%m/%Y %H:%M") if profile.created_at else "—"}\n\n'
                f'Acesse o painel para aprovar ou rejeitar:\n{admin_url}'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=['mapagov.gestao@gmail.com'],
            reply_to=[user.email],
        )
        msg.send(fail_silently=False)
        logger.info(f"Email de autorizacao enviado para mapagov.gestao@gmail.com (usuario: {user.email})")
    except Exception as e:
        logger.error(f"Erro ao enviar email de autorizacao para mapagov.gestao: {e}")


def models_Q_superuser_or_group():
    """Retorna Q filter para usuarios que sao superuser OU membros do grupo ACCESS_APPROVER."""
    from django.db.models import Q
    from processos.models_auth import ACCESS_APPROVER_GROUP
    return Q(is_superuser=True) | Q(groups__name=ACCESS_APPROVER_GROUP)


def _log_audit(user, action, description, request=None):
    """Registra evento no AuditLog se disponivel."""
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


# ============================================================================
# ENDPOINTS
# ============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_csrf(request):
    """Retorna CSRF token no cookie. Frontend deve chamar antes do primeiro POST."""
    token = get_token(request)
    return Response({'csrfToken': token})


@api_view(['POST'])
@permission_classes([AllowAny])
@rate_limit_ip(limit=3, window=600)
def register(request):
    """
    Registra novo usuario.

    MGI (@gestao.gov.br): access_status='approved' (ainda exige email_verified)
    Externo: access_status='pending' (precisa de 3 aprovacoes)
    """
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    email = data['email']

    # Criar User (username = parte do email antes do @)
    username = email.split('@')[0]
    # Garantir unicidade do username
    base_username = username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1

    user = User.objects.create_user(
        username=username,
        email=email,
        password=data['password'],
        first_name=data['nome_completo'].split()[0] if data['nome_completo'] else '',
        last_name=' '.join(data['nome_completo'].split()[1:]) if data['nome_completo'] else '',
    )

    # Profile ja criado pelo signal post_save, atualizar campos extras
    profile = user.profile
    profile.nome_completo = data['nome_completo']
    profile.cargo = data.get('cargo', '')
    profile.is_decipex = data.get('is_decipex', False)
    profile.setor_trabalho = data.get('setor_trabalho', '')

    # Vincular area se fornecida (Decipex)
    if data.get('area_codigo'):
        from processos.models import Area
        area = Area.objects.filter(codigo=data['area_codigo'], ativo=True).first()
        if area:
            profile.area = area

    profile.save()

    # Enviar email de verificacao
    _send_verification_email(user)

    # Se externo, notificar aprovadores + enviar para mapagov.gestao@gmail.com
    if not is_mgi_email(email):
        _notify_approvers_new_registration(user)
        _notify_authorization_email(user, profile)

    _log_audit(user, 'register', f'Novo cadastro: {email} ({profile.profile_type})', request)

    return Response({
        'mensagem': 'Cadastro realizado. Verifique seu email para continuar.',
        'profile_type': profile.profile_type,
        'access_status': profile.access_status,
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request, uidb64, token):
    """Verifica email via link tokenizado."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({'erro': 'Link invalido.'}, status=status.HTTP_400_BAD_REQUEST)

    if not default_token_generator.check_token(user, token):
        return Response({'erro': 'Link expirado ou invalido.'}, status=status.HTTP_400_BAD_REQUEST)

    profile = user.profile
    if profile.email_verified:
        return Response({'mensagem': 'Email ja verificado.', 'access_status': profile.access_status})

    profile.verify_email()
    _log_audit(user, 'email_verify', f'Email verificado: {user.email}', request)

    return Response({
        'mensagem': 'Email verificado com sucesso.',
        'access_status': profile.access_status,
        'can_access': profile.can_access,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
@rate_limit_ip(limit=5, window=300)
def login_view(request):
    """Login por sessao Django."""
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email']
    password = serializer.validated_data['password']

    # Buscar user por email
    try:
        user_obj = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {'erro': 'Credenciais invalidas.'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    user = authenticate(request, username=user_obj.username, password=password)
    if user is None:
        _log_audit(user_obj, 'login', f'Tentativa de login falhou: {email}', request)
        return Response(
            {'erro': 'Credenciais invalidas.'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Verificar se pode acessar
    profile = user.profile
    if not profile.email_verified:
        return Response({
            'erro': 'Email nao verificado. Verifique sua caixa de entrada.',
            'code': 'email_not_verified',
        }, status=status.HTTP_403_FORBIDDEN)

    if profile.access_status != 'approved':
        return Response({
            'erro': 'Seu cadastro esta pendente de aprovacao.',
            'code': 'access_pending',
            'access_status': profile.access_status,
        }, status=status.HTTP_403_FORBIDDEN)

    # Login session
    login(request, user)
    _log_audit(user, 'login', f'Login bem-sucedido: {email}', request)

    return Response({
        'mensagem': 'Login realizado.',
        'user': UserProfileSerializer(profile).data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Destroi sessao."""
    _log_audit(request.user, 'logout', f'Logout: {request.user.email}', request)
    logout(request)
    return Response({'mensagem': 'Logout realizado.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """Retorna info do usuario logado + status do perfil."""
    profile = get_or_create_profile(request.user)
    data = UserProfileSerializer(profile).data
    data['can_access'] = profile.can_access
    data['is_approver'] = is_approver(request.user)
    return Response(data)


@api_view(['POST'])
@permission_classes([AllowAny])
@rate_limit_ip(limit=3, window=600)
def password_reset(request):
    """Envia email de reset de senha."""
    serializer = PasswordResetSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email']

    # Sempre retorna sucesso (nao revela se email existe)
    try:
        user = User.objects.get(email=email)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        frontend_url = _get_frontend_url()
        reset_url = f"{frontend_url}/nova-senha/{uid}/{token}"

        send_mail(
            subject='MapaGov — Recuperação de senha',
            message=render_to_string('email/password_reset.txt', {
                'user': user,
                'reset_url': reset_url,
            }),
            html_message=render_to_string('email/password_reset.html', {
                'user': user,
                'reset_url': reset_url,
            }),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        _log_audit(user, 'password_reset', f'Reset de senha solicitado: {email}', request)
    except User.DoesNotExist:
        pass  # Nao revelar se email existe
    except Exception as e:
        logger.error(f"Erro ao enviar email de reset: {e}")

    return Response({'mensagem': 'Se o email estiver cadastrado, voce recebera um link de recuperacao.'})


@api_view(['GET'])
@permission_classes([AllowAny])
def public_areas(request):
    """Lista areas ativas para formulario de cadastro (publico, sem autenticacao)."""
    from processos.models import Area
    areas = Area.objects.filter(ativo=True, area_pai__isnull=True).order_by('nome_curto').values(
        'codigo', 'nome_curto',
    )
    return Response(list(areas))


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """Reseta senha com token."""
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    try:
        uid = force_str(urlsafe_base64_decode(serializer.validated_data['uid']))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({'erro': 'Link invalido.'}, status=status.HTTP_400_BAD_REQUEST)

    if not default_token_generator.check_token(user, serializer.validated_data['token']):
        return Response({'erro': 'Link expirado ou invalido.'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(serializer.validated_data['password'])
    user.save()
    _log_audit(user, 'password_reset', f'Senha alterada: {user.email}', request)

    return Response({'mensagem': 'Senha alterada com sucesso. Faca login com a nova senha.'})
