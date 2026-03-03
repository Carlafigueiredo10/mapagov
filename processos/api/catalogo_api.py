import hashlib
import json
import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Count, Q
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from processos.models import Area, POP, POPChangeLog, PopVersion
from processos.permissions import IsAreaManagerOrAbove
from .catalogo_serializers import (
    AreaSerializer,
    POPListSerializer,
    POPDetailSerializer,
    PopVersionSerializer,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Helpers — observabilidade, permissao e comparacao de snapshot
# ============================================================================

def _log_workflow(action_name, pop, user, status_from, status_to, allowed=True, extra=None):
    """Log estruturado para transicoes de workflow POP."""
    entry = {
        'action': action_name,
        'pop_uuid': str(pop.uuid),
        'user_id': user.pk if user else None,
        'status_from': status_from,
        'status_to': status_to,
        'allowed': allowed,
    }
    if extra:
        entry.update(extra)
    level = logging.INFO if allowed else logging.WARNING
    logger.log(level, f"[WORKFLOW] {json.dumps(entry, default=str)}")

def _enforce_same_area_manager(request, pop, action_name='unknown'):
    """Valida que o gestor pertence a mesma area do POP. Bypass: is_superuser."""
    if request.user.is_superuser:
        return
    up = getattr(request.user, 'profile', None)
    if not up or not up.area_id:
        _log_workflow(action_name, pop, request.user, pop.status, pop.status,
                      allowed=False, extra={'reason': 'no_profile_area'})
        raise PermissionDenied("Usuario sem perfil/setor configurado.")
    if not pop.area_id:
        _log_workflow(action_name, pop, request.user, pop.status, pop.status,
                      allowed=False, extra={'reason': 'pop_no_area'})
        raise PermissionDenied("POP sem setor vinculado.")
    if up.area_id != pop.area_id:
        _log_workflow(action_name, pop, request.user, pop.status, pop.status,
                      allowed=False, extra={'reason': 'area_mismatch',
                                            'user_area': up.area_id, 'pop_area': pop.area_id})
        raise PermissionDenied("Acao permitida apenas para o mesmo setor do POP.")


def _stable_payload_hash(payload):
    """Hash estavel para comparacao de payloads, ignorando ordem de chaves."""
    if payload is None:
        return None
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, default=str,
                   ensure_ascii=False, separators=(',', ':')).encode()
    ).hexdigest()


def _get_frontend_url():
    """URL base do frontend para links em emails."""
    if settings.DEBUG:
        return 'http://localhost:5173'
    return settings.CSRF_TRUSTED_ORIGINS[0] if settings.CSRF_TRUSTED_ORIGINS else ''


def _notify_pop_homologated(pop):
    """Notifica o autor que o POP foi homologado com alteracoes."""
    if not pop.created_by or not pop.created_by.email:
        logger.warning(f"[HOMOLOGAR] POP {pop.uuid}: autor sem email, notificacao ignorada.")
        return

    nome = pop.nome_processo or 'POP sem nome'
    try:
        send_mail(
            subject='MapaGov — Seu POP foi revisado e homologado',
            message=render_to_string('email/pop_homologated.txt', {
                'user': pop.created_by,
                'nome_processo': nome,
                'pop_uuid': str(pop.uuid),
                'frontend_url': _get_frontend_url(),
            }),
            html_message=render_to_string('email/pop_homologated.html', {
                'user': pop.created_by,
                'nome_processo': nome,
                'pop_uuid': str(pop.uuid),
                'frontend_url': _get_frontend_url(),
            }),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[pop.created_by.email],
            fail_silently=True,
        )
    except Exception as e:
        logger.warning(f"[HOMOLOGAR] Falha ao enviar email para {pop.created_by.email}: {e}")


def _notify_pop_rejected(pop, motivo):
    """Notifica o autor que o POP foi rejeitado."""
    if not pop.created_by or not pop.created_by.email:
        logger.warning(f"[REJECT] POP {pop.uuid}: autor sem email, notificacao ignorada.")
        return

    nome = pop.nome_processo or 'POP sem nome'
    try:
        send_mail(
            subject='MapaGov — Seu POP foi devolvido para revisao',
            message=render_to_string('email/pop_review_rejected.txt', {
                'user': pop.created_by,
                'nome_processo': nome,
                'motivo': motivo,
                'pop_uuid': str(pop.uuid),
                'frontend_url': _get_frontend_url(),
            }),
            html_message=render_to_string('email/pop_review_rejected.html', {
                'user': pop.created_by,
                'nome_processo': nome,
                'motivo': motivo,
                'pop_uuid': str(pop.uuid),
                'frontend_url': _get_frontend_url(),
            }),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[pop.created_by.email],
            fail_silently=True,
        )
    except Exception as e:
        logger.warning(f"[REJECT] Falha ao enviar email para {pop.created_by.email}: {e}")


# ============================================================================
# AreaViewSet — ReadOnly, lookup por slug
# ============================================================================

class AreaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/areas/          — lista areas top-level com pop_count
    GET /api/areas/{slug}/   — detalhe da area com subareas
    GET /api/areas/{slug}/pops/ — POPs publicados da area (Etapa 2)
    """
    serializer_class = AreaSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        qs = Area.objects.filter(ativo=True).annotate(
            pop_count=Count('pops', filter=Q(
                pops__is_deleted=False,
                pops__status='published',
            ))
        )
        # Na listagem, mostrar so top-level (sem sub-areas soltas)
        if self.action == 'list' and not self.request.query_params.get('all'):
            qs = qs.filter(area_pai__isnull=True)
        return qs.order_by('ordem')

    # ----- Etapa 2: listagem de POPs por area -----
    @action(detail=True, methods=['get'], url_path='pops')
    def pops(self, request, slug=None):
        """GET /api/areas/{slug}/pops/?status=published&q=..."""
        area = self.get_object()

        # Incluir sub-areas
        area_ids = [area.id] + list(area.subareas.values_list('id', flat=True))
        qs = POP.objects.filter(
            area_id__in=area_ids,
            is_deleted=False,
        ).select_related('area').order_by('-updated_at')

        # Filtro por status (default: published)
        status_filter = request.query_params.get('status', 'published')
        if status_filter != 'all':
            qs = qs.filter(status=status_filter)

        # Busca simples por nome
        q = request.query_params.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(nome_processo__icontains=q) |
                Q(codigo_processo__icontains=q) |
                Q(macroprocesso__icontains=q)
            )

        serializer = POPListSerializer(qs[:200], many=True)
        return Response(serializer.data)


# ============================================================================
# POPViewSet — CRUD completo, lookup por uuid
# ============================================================================

class POPViewSet(viewsets.ModelViewSet):
    """
    GET    /api/pops/            — lista filtrada
    POST   /api/pops/            — cria POP
    GET    /api/pops/{uuid}/     — detalhe
    PATCH  /api/pops/{uuid}/     — update parcial
    DELETE /api/pops/{uuid}/     — soft delete
    """
    lookup_field = 'uuid'

    def get_serializer_class(self):
        if self.action == 'list':
            return POPListSerializer
        return POPDetailSerializer

    def get_queryset(self):
        qs = POP.objects.filter(is_deleted=False).select_related('area')

        # Filtro mine=true — retorna POPs do usuario autenticado (sem filtro de status)
        if self.request.query_params.get('mine') == 'true':
            if not self.request.user.is_authenticated:
                raise PermissionDenied('Autenticacao necessaria para listar seus POPs.')
            qs = qs.filter(created_by=self.request.user)

        # Filtro review_queue=true — POPs in_review da mesma area do usuario
        elif self.request.query_params.get('review_queue') == 'true':
            if not self.request.user.is_authenticated:
                raise PermissionDenied('Autenticacao necessaria.')
            profile = getattr(self.request.user, 'profile', None)
            if self.request.user.is_superuser:
                qs = qs.filter(status='in_review')
            elif profile and profile.area_id:
                qs = qs.filter(status='in_review', area_id=profile.area_id)
            else:
                logger.warning(
                    f"[REVIEW_QUEUE] Usuario {self.request.user.pk} sem perfil/area, retornando lista vazia."
                )
                return POP.objects.none()
            return qs.order_by('-submitted_for_review_at', '-updated_at')

        # Filtro por area slug
        area_slug = self.request.query_params.get('area')
        if area_slug:
            qs = qs.filter(area__slug=area_slug)

        # Filtro por status (quando nao e mine nem review_queue)
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        return qs.order_by('-updated_at')

    def perform_destroy(self, instance):
        """Soft delete."""
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])

    # ----- Workflow: Submit for Review -----
    @action(detail=True, methods=['post'], url_path='submit-review',
            permission_classes=[IsAuthenticated])
    def submit_review(self, request, uuid=None):
        """POST /api/pops/{uuid}/submit-review/ — submete POP para revisao."""
        pop = self.get_object()

        if pop.status != 'draft':
            return Response(
                {'error': 'Transicao invalida para o status atual do POP.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not pop.area_id:
            return Response(
                {'error': 'POP sem setor vinculado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Permissao: autor ou operador da mesma area
        is_author = pop.created_by_id == request.user.pk
        profile = getattr(request.user, 'profile', None)
        is_same_area = profile and profile.area_id and profile.area_id == pop.area_id
        if not is_author and not is_same_area and not request.user.is_superuser:
            raise PermissionDenied("Acao permitida apenas para o mesmo setor do POP.")

        pop.review_snapshot = pop.get_dados_completos()
        pop.submitted_for_review_at = timezone.now()
        pop.submitted_by = request.user
        pop.reviewed_by = request.user
        pop.review_notes = ''
        old_status = pop.status
        pop.status = 'in_review'
        pop.save()

        _log_workflow('submit_review', pop, request.user, old_status, 'in_review')
        return Response({
            'success': True,
            'uuid': str(pop.uuid),
            'status': pop.status,
        })

    # ----- Workflow: Homologar (= Publicar) -----
    @action(detail=True, methods=['post'], url_path='homologar',
            permission_classes=[IsAuthenticated, IsAreaManagerOrAbove])
    def homologar(self, request, uuid=None):
        """POST /api/pops/{uuid}/homologar/ — homologa (publica) POP apos revisao."""
        pop = self.get_object()

        _enforce_same_area_manager(request, pop, action_name='homologar')

        if pop.status != 'in_review':
            return Response(
                {'error': 'Transicao invalida para o status atual do POP.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not pop.nome_processo:
            return Response(
                {'error': 'POP precisa de nome_processo para publicar.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Detectar se houve alteracao durante revisao
        snapshot_hash = _stable_payload_hash(pop.review_snapshot)
        current_hash = _stable_payload_hash(pop.get_dados_completos())
        content_changed = snapshot_hash is not None and snapshot_hash != current_hash

        motivo = request.data.get('motivo', '')

        with transaction.atomic():
            PopVersion.objects.filter(pop=pop, is_current=True).update(is_current=False)

            pop.versao += 1
            pop.status = 'published'
            pop.integrity_hash = pop.compute_integrity_hash()
            # Limpar metadados de revisao (manter reviewed_by para auditoria)
            pop.submitted_for_review_at = None
            pop.submitted_by = None
            pop.review_snapshot = None
            pop.save()

            version = PopVersion.objects.create(
                pop=pop,
                versao=pop.versao,
                payload=pop.get_dados_completos(),
                integrity_hash=pop.integrity_hash,
                published_by=request.user,
                motivo=motivo,
                is_current=True,
            )

        _log_workflow('homologar', pop, request.user, 'in_review', 'published',
                      extra={'versao': version.versao, 'content_changed': content_changed})

        if content_changed:
            _notify_pop_homologated(pop)

        return Response({
            'success': True,
            'uuid': str(pop.uuid),
            'versao': version.versao,
            'integrity_hash': pop.integrity_hash,
            'content_changed': content_changed,
        })

    # ----- Workflow: Publish (wrapper para compatibilidade) -----
    @action(detail=True, methods=['post'], url_path='publish',
            permission_classes=[IsAuthenticated, IsAreaManagerOrAbove])
    def publish(self, request, uuid=None):
        """POST /api/pops/{uuid}/publish/ — wrapper: delega para homologar()."""
        pop = self.get_object()

        if pop.status == 'in_review':
            return self.homologar(request, uuid=uuid)

        if pop.status == 'draft':
            return Response(
                {'error': 'Submeta para revisao primeiro.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if pop.status == 'archived':
            return Response(
                {'error': 'POP arquivado nao pode ser publicado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {'error': 'Transicao invalida para o status atual do POP.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ----- Workflow: Reject Review -----
    @action(detail=True, methods=['post'], url_path='reject-review',
            permission_classes=[IsAuthenticated, IsAreaManagerOrAbove])
    def reject_review(self, request, uuid=None):
        """POST /api/pops/{uuid}/reject-review/ — rejeita revisao, volta para draft."""
        pop = self.get_object()

        _enforce_same_area_manager(request, pop, action_name='reject_review')

        if pop.status != 'in_review':
            return Response(
                {'error': 'Transicao invalida para o status atual do POP.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        motivo = (request.data.get('motivo') or '').strip()
        if not motivo:
            return Response(
                {'error': 'Motivo e obrigatorio.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pop.review_notes = motivo
        pop.submitted_for_review_at = None
        pop.submitted_by = None
        # Manter reviewed_by e review_snapshot para auditoria
        pop.status = 'draft'
        pop.save()

        _log_workflow('reject_review', pop, request.user, 'in_review', 'draft')

        _notify_pop_rejected(pop, motivo)

        return Response({
            'success': True,
            'uuid': str(pop.uuid),
            'status': pop.status,
        })

    # ----- Workflow: Archive -----
    @action(detail=True, methods=['post'], url_path='archive',
            permission_classes=[IsAuthenticated, IsAreaManagerOrAbove])
    def archive(self, request, uuid=None):
        """POST /api/pops/{uuid}/archive/"""
        pop = self.get_object()

        _enforce_same_area_manager(request, pop, action_name='archive')

        if pop.status == 'archived':
            return Response({'error': 'POP ja esta arquivado.'}, status=status.HTTP_400_BAD_REQUEST)
        if pop.status != 'published':
            return Response(
                {'error': 'Transicao invalida para o status atual do POP.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pop.status = 'archived'
        pop.save()

        _log_workflow('archive', pop, request.user, 'published', 'archived')
        return Response({'success': True, 'uuid': str(pop.uuid)})

    # ----- Historico de versoes -----
    @action(detail=True, methods=['get'], url_path='versions')
    def versions(self, request, uuid=None):
        """GET /api/pops/{uuid}/versions/ — lista versoes publicadas."""
        pop = self.get_object()
        versions = pop.versions.all()
        serializer = PopVersionSerializer(versions, many=True)
        return Response(serializer.data)


# ============================================================================
# Etapa 2: Detalhe por area+codigo (rota manual com <path:codigo>)
# ============================================================================

@api_view(['GET'])
def pop_por_area_codigo(request, slug, codigo):
    """GET /api/areas/{slug}/pops/{codigo}/ — detalhe do POP por area+codigo."""
    area = Area.objects.filter(slug=slug, ativo=True).first()
    if not area:
        return Response({'error': 'Area nao encontrada.'}, status=status.HTTP_404_NOT_FOUND)

    # Incluir sub-areas
    area_ids = [area.id] + list(area.subareas.values_list('id', flat=True))
    pop = POP.objects.filter(
        area_id__in=area_ids,
        codigo_processo=codigo,
        is_deleted=False,
    ).select_related('area').first()

    if not pop:
        return Response({'error': 'POP nao encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = POPDetailSerializer(pop)
    return Response(serializer.data)


# ============================================================================
# Etapa 4: Resolve CAP (query params)
# ============================================================================

@api_view(['GET'])
def resolve_pop(request):
    """
    GET /api/pops/resolve/?area=cgris&codigo=6.1.1.1.5&v=3
    GET /api/pops/resolve/?cap=6.1.1.1.5
    """
    area_slug = request.query_params.get('area', '').strip()
    codigo = request.query_params.get('codigo', '').strip()
    cap = request.query_params.get('cap', '').strip()
    versao_param = request.query_params.get('v', '').strip()

    # Buscar POP
    pop = None
    if area_slug and codigo:
        area = Area.objects.filter(slug=area_slug, ativo=True).first()
        if area:
            area_ids = [area.id] + list(area.subareas.values_list('id', flat=True))
            pop = POP.objects.filter(
                area_id__in=area_ids,
                codigo_processo=codigo,
                is_deleted=False,
            ).first()
    elif cap:
        pop = POP.objects.filter(codigo_processo=cap, is_deleted=False).first()

    if not pop:
        return Response({'error': 'POP nao encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    # Versao especifica?
    if versao_param:
        try:
            versao_num = int(versao_param)
        except ValueError:
            return Response({'error': 'Parametro v deve ser inteiro.'}, status=status.HTTP_400_BAD_REQUEST)

        version = PopVersion.objects.filter(pop=pop, versao=versao_num).first()
        if not version:
            return Response(
                {'error': f'Versao {versao_num} nao encontrada.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({
            'uuid': str(pop.uuid),
            'cap': pop.codigo_processo,
            'nome_processo': pop.nome_processo,
            'status': pop.status,
            'versao': version.versao,
            'is_current': version.is_current,
            'published': True,
            'published_at': version.published_at.isoformat(),
            'integrity_hash': version.integrity_hash,
            'dados': version.payload,
        })

    # Ultima versao publicada
    current_version = PopVersion.objects.filter(pop=pop, is_current=True).first()
    if current_version:
        return Response({
            'uuid': str(pop.uuid),
            'cap': pop.codigo_processo,
            'nome_processo': pop.nome_processo,
            'status': pop.status,
            'versao': current_version.versao,
            'published': True,
            'published_at': current_version.published_at.isoformat(),
            'integrity_hash': current_version.integrity_hash,
            'dados': current_version.payload,
        })

    # Sem versao publicada: retorna dados correntes
    return Response({
        'uuid': str(pop.uuid),
        'cap': pop.codigo_processo,
        'nome_processo': pop.nome_processo,
        'status': pop.status,
        'versao': pop.versao,
        'published': False,
        'dados': pop.get_dados_completos(),
    })
