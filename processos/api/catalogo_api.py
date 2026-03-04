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
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
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


def _compute_next_cap(source_cap):
    """
    Dado um CAP como '01.02.03.04.108', calcula o proximo numero de atividade
    disponivel no mesmo subprocesso: '01.02.03.04.XXX'.

    Prefixo = tudo menos o ultimo segmento (robusto para qualquer profundidade).
    """
    parts = source_cap.rsplit('.', 1)
    if len(parts) != 2:
        raise ValueError(f"CAP invalido para clone: {source_cap}")

    prefix = parts[0]  # ex: '01.02.03.04'

    existing_caps = POP.objects.filter(
        codigo_processo__startswith=f"{prefix}.",
        is_deleted=False,
    ).values_list('codigo_processo', flat=True)

    max_idx = 0
    for cap in existing_caps:
        suffix = cap[len(prefix) + 1:]  # tudo apos 'AA.MM.PP.SS.'
        base_suffix = suffix.split('-')[0]  # ignorar sufixos de colisao (-2, -3)
        try:
            idx = int(base_suffix)
            if idx > max_idx:
                max_idx = idx
        except ValueError:
            continue

    next_idx = max_idx + 1

    # Manter padding de 3 digitos (minimo)
    source_suffix = parts[1].split('-')[0]
    padding = max(len(source_suffix), 3)

    return f"{prefix}.{next_idx:0{padding}d}"


def _save_with_cap_retry(pop, max_attempts=3):
    """Salva POP com retry em colisao de CAP (constraint unique_cap_ativo)."""
    from django.db import IntegrityError
    for attempt in range(max_attempts):
        try:
            with transaction.atomic():
                pop.integrity_hash = pop.compute_integrity_hash()
                pop.save()
            return
        except IntegrityError as e:
            if 'unique_cap_ativo' in str(e) and pop.codigo_processo and attempt < max_attempts - 1:
                cap = pop.codigo_processo
                prefix, suffix = cap.rsplit('.', 1)
                base_suffix = suffix.split('-')[0]
                try:
                    next_num = int(base_suffix) + 1
                    padding = max(len(base_suffix), 3)
                    pop.codigo_processo = f"{prefix}.{next_num:0{padding}d}"
                except ValueError:
                    pop.codigo_processo = f"{cap}-{attempt + 2}"
                logger.warning(f"[CLONE] CAP collision, attempt {attempt + 2}: {pop.codigo_processo}")
            else:
                raise


def _enforce_same_area_operator(request, pop, action_name='unknown'):
    """Valida que o operador pertence a mesma area do POP. Bypass: is_superuser."""
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
        raise PermissionDenied("Voce so pode clonar POPs do seu setor.")


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
    permission_classes = [AllowAny]
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

    # ----- Clone POP -----

    @staticmethod
    def _normalize_area(pop):
        """Normaliza area do POP para formato {nome, codigo} que a SM espera."""
        area = getattr(pop, "area", None)
        nome = getattr(pop, "area_nome", None) or ""
        codigo = getattr(pop, "area_codigo", None) or ""
        if nome or codigo:
            return {"nome": nome, "codigo": codigo}
        if area is not None:
            return {
                "nome": getattr(area, "nome", "") or str(area) or "",
                "codigo": getattr(area, "codigo", "") or "",
            }
        return {"nome": "", "codigo": ""}

    @staticmethod
    def _normalize_to_list(value):
        """Converte string com ';' ou None para list (SM espera list)."""
        if isinstance(value, list):
            return value
        if isinstance(value, str) and value.strip():
            return [v.strip() for v in value.split(";") if v.strip()]
        return []

    @action(detail=True, methods=['post'], url_path='clone',
            permission_classes=[IsAuthenticated])
    def clone(self, request, uuid=None):
        """POST /api/pops/{uuid}/clone/ — clona POP com nova atividade."""
        import copy
        import uuid as uuid_mod

        source_pop = self.get_object()

        # Permissao por area (operador ou superuser)
        _enforce_same_area_operator(request, source_pop, action_name='clone')

        # Validar status fonte
        if source_pop.status not in ('published', 'in_review'):
            return Response(
                {'error': 'Apenas POPs publicados ou em revisao podem ser clonados.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validar atividade
        nova_atividade = (request.data.get('atividade') or '').strip()
        if not nova_atividade or len(nova_atividade) < 5:
            return Response(
                {'error': 'Nome da atividade e obrigatorio (minimo 5 caracteres).'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Gerar novo CAP
        if not source_pop.codigo_processo:
            return Response(
                {'error': 'POP fonte nao possui codigo de processo (CAP).'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        novo_cap = _compute_next_cap(source_pop.codigo_processo)

        # Deep copy etapas com UUIDs regenerados
        etapas_clone = []
        for etapa in (source_pop.etapas or []):
            etapa_copy = copy.deepcopy(etapa)
            etapa_copy['id'] = str(uuid_mod.uuid4())
            etapas_clone.append(etapa_copy)

        # Criar POP clonado
        new_session_id = str(uuid_mod.uuid4())
        new_pop = POP(
            session_id=new_session_id,
            area=source_pop.area,
            processo_mestre=source_pop.processo_mestre,
            area_codigo=source_pop.area_codigo,
            area_nome=source_pop.area_nome,
            macroprocesso=source_pop.macroprocesso,
            codigo_processo=novo_cap,
            nome_processo=nova_atividade,
            processo_especifico=source_pop.processo_especifico,
            entrega_esperada=source_pop.entrega_esperada,
            dispositivos_normativos=source_pop.dispositivos_normativos,
            sistemas_utilizados=copy.deepcopy(source_pop.sistemas_utilizados) if source_pop.sistemas_utilizados else [],
            operadores=source_pop.operadores,
            pontos_atencao=source_pop.pontos_atencao,
            etapas=etapas_clone,
            documentos_utilizados=copy.deepcopy(source_pop.documentos_utilizados) if source_pop.documentos_utilizados else [],
            fluxos_entrada=copy.deepcopy(source_pop.fluxos_entrada) if source_pop.fluxos_entrada else [],
            fluxos_saida=copy.deepcopy(source_pop.fluxos_saida) if source_pop.fluxos_saida else [],
            status='draft',
            versao=0,
            created_by=request.user,
            nome_usuario=request.user.get_full_name() or request.user.username,
        )

        _save_with_cap_retry(new_pop)

        # Inicializar SM no estado REVISAO_FINAL para o clone
        from processos.domain.helena_mapeamento.helena_pop import POPStateMachine, EstadoPOP

        sm = POPStateMachine()
        sm.estado = EstadoPOP.REVISAO_FINAL
        sm.nome_usuario = new_pop.nome_usuario or (
            request.user.get_full_name() or request.user.username
        )
        sm.area_selecionada = self._normalize_area(source_pop)
        sm.macro_selecionado = getattr(source_pop, "macroprocesso", "") or ""
        sm.processo_selecionado = getattr(source_pop, "processo_especifico", "") or ""
        sm.codigo_cap = novo_cap
        sm.atividade_selecionada = nova_atividade
        sm.dados_coletados = {
            "nome_processo": nova_atividade,
            "entrega_esperada": getattr(source_pop, "entrega_esperada", "") or "",
            "dispositivos_normativos": self._normalize_to_list(
                getattr(source_pop, "dispositivos_normativos", None)
            ),
            "operadores": self._normalize_to_list(
                getattr(source_pop, "operadores", None)
            ),
            "sistemas": getattr(source_pop, "sistemas_utilizados", None) or [],
            "fluxos_entrada": getattr(new_pop, "fluxos_entrada", None) or [],
            "fluxos_saida": getattr(new_pop, "fluxos_saida", None) or [],
            "pontos_atencao": getattr(source_pop, "pontos_atencao", "") or "",
        }
        sm.etapas_coletadas = etapas_clone
        sm.tipo_interface = "revisao_final"
        if hasattr(sm, "dados_interface"):
            sm.dados_interface = {}

        session_key = f"helena_pop_state_{new_session_id}"
        request.session[session_key] = sm.to_dict()
        request.session.modified = True

        logger.info(
            "[CLONE-SM] State machine gravada: session_key=%s, estado=%s",
            session_key, sm.estado.value,
        )

        # Auditoria: registrar clone via POPChangeLog (sem migration)
        POPChangeLog.objects.create(
            pop=new_pop,
            user=request.user,
            field_name='__event__',
            old_value=None,
            new_value={'type': 'clone_from', 'source_uuid': str(source_pop.uuid)},
        )

        _log_workflow('clone', new_pop, request.user, 'n/a', 'draft',
                      extra={'source_uuid': str(source_pop.uuid),
                             'source_cap': source_pop.codigo_processo,
                             'new_cap': new_pop.codigo_processo})

        return Response({
            'success': True,
            'pop': {
                'id': new_pop.pk,
                'uuid': str(new_pop.uuid),
                'session_id': new_pop.session_id,
                'integrity_hash': new_pop.integrity_hash,
                'status': 'draft',
                'dados': new_pop.get_dados_completos(),
            },
            'source_uuid': str(source_pop.uuid),
        }, status=status.HTTP_201_CREATED)

    # ----- Retomar POP (inicializa SM na sessao) -----

    @action(detail=True, methods=['post'], url_path='retomar',
            permission_classes=[IsAuthenticated])
    def retomar(self, request, uuid=None):
        """POST /api/pops/{uuid}/retomar/ — inicializa SM em REVISAO_FINAL para retomar edicao."""
        import uuid as uuid_mod

        pop = self.get_object()

        # Permissao: dono ou superuser
        if not request.user.is_superuser and pop.created_by_id != request.user.pk:
            raise PermissionDenied('Voce nao tem permissao para retomar este POP.')

        # Somente drafts podem ser retomados para edicao
        if pop.status != 'draft':
            return Response(
                {'error': 'Apenas POPs em rascunho podem ser retomados.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Regra: so retoma POP com CAP definido
        if not pop.codigo_processo:
            return Response(
                {'error': 'Retomar disponivel apenas para POPs com atividade (CAP) definida.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Gerar session_id novo (nao depender de sessao antiga/expirada)
        session_id = str(uuid_mod.uuid4())
        pop.session_id = session_id
        pop.save(update_fields=['session_id'])

        # Inicializar SM no estado REVISAO_FINAL (mesmo padrao do clone)
        from processos.domain.helena_mapeamento.helena_pop import POPStateMachine, EstadoPOP

        sm = POPStateMachine()
        sm.estado = EstadoPOP.REVISAO_FINAL
        sm.nome_usuario = pop.nome_usuario or (
            request.user.get_full_name() or request.user.username
        )
        sm.area_selecionada = self._normalize_area(pop)
        sm.macro_selecionado = getattr(pop, "macroprocesso", "") or ""
        sm.processo_selecionado = getattr(pop, "processo_especifico", "") or ""
        sm.codigo_cap = pop.codigo_processo or ""
        sm.atividade_selecionada = pop.nome_processo or ""
        sm.dados_coletados = {
            "nome_processo": pop.nome_processo or "",
            "entrega_esperada": getattr(pop, "entrega_esperada", "") or "",
            "dispositivos_normativos": self._normalize_to_list(
                getattr(pop, "dispositivos_normativos", None)
            ),
            "operadores": self._normalize_to_list(
                getattr(pop, "operadores", None)
            ),
            "sistemas": getattr(pop, "sistemas_utilizados", None) or [],
            "fluxos_entrada": getattr(pop, "fluxos_entrada", None) or [],
            "fluxos_saida": getattr(pop, "fluxos_saida", None) or [],
            "pontos_atencao": getattr(pop, "pontos_atencao", "") or "",
            "tempo_total_minutos": getattr(pop, "tempo_total_minutos", None),
        }
        sm.etapas_coletadas = pop.etapas or []
        sm.tipo_interface = "revisao_final"
        if hasattr(sm, "dados_interface"):
            sm.dados_interface = {}

        session_key = f"helena_pop_state_{session_id}"
        request.session[session_key] = sm.to_dict()
        request.session.modified = True

        logger.info(
            "[RETOMAR-SM] SM gravada: session_key=%s, estado=%s, pop_uuid=%s",
            session_key, sm.estado.value, str(pop.uuid),
        )

        return Response({
            'success': True,
            'session_id': session_id,
            'pop': {
                'id': pop.pk,
                'uuid': str(pop.uuid),
                'session_id': session_id,
                'integrity_hash': pop.integrity_hash,
                'status': pop.status,
                'dados': pop.get_dados_completos(),
            },
        })


# ============================================================================
# Etapa 2: Detalhe por area+codigo (rota manual com <path:codigo>)
# ============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
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
    codigo = request.query_params.get('codigo', '').strip().replace(' ', '')
    cap = request.query_params.get('cap', '').strip().replace(' ', '')
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
            'area_id': pop.area_id,
            'area_nome': pop.area_nome,
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
            'area_id': pop.area_id,
            'area_nome': pop.area_nome,
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
        'area_id': pop.area_id,
        'area_nome': pop.area_nome,
        'versao': pop.versao,
        'published': False,
        'dados': pop.get_dados_completos(),
    })
