import logging

from django.db import transaction
from django.db.models import Count, Q
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from processos.models import Area, POP, PopVersion
from .catalogo_serializers import (
    AreaSerializer,
    POPListSerializer,
    POPDetailSerializer,
    PopVersionSerializer,
)

logger = logging.getLogger(__name__)


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

        # Filtro por area slug
        area_slug = self.request.query_params.get('area')
        if area_slug:
            qs = qs.filter(area__slug=area_slug)

        # Filtro por status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        return qs.order_by('-updated_at')

    def perform_destroy(self, instance):
        """Soft delete."""
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])

    # ----- Etapa 3: Publish -----
    @action(detail=True, methods=['post'], url_path='publish')
    def publish(self, request, uuid=None):
        """POST /api/pops/{uuid}/publish/ — cria PopVersion imutavel."""
        pop = self.get_object()

        if pop.status == 'archived':
            return Response(
                {'error': 'POP arquivado nao pode ser publicado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not pop.nome_processo:
            return Response(
                {'error': 'POP precisa de nome_processo para publicar.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        motivo = request.data.get('motivo', '')

        with transaction.atomic():
            # Marcar versoes anteriores como nao-correntes
            PopVersion.objects.filter(pop=pop, is_current=True).update(is_current=False)

            pop.versao += 1
            pop.status = 'published'
            pop.integrity_hash = pop.compute_integrity_hash()
            pop.save(update_fields=['versao', 'status', 'integrity_hash', 'last_activity_at'])

            version = PopVersion.objects.create(
                pop=pop,
                versao=pop.versao,
                payload=pop.get_dados_completos(),
                integrity_hash=pop.integrity_hash,
                published_by=request.user if request.user.is_authenticated else None,
                motivo=motivo,
                is_current=True,
            )

        logger.info(f"[PUBLISH] POP {pop.uuid} publicado como v{version.versao}")
        return Response({
            'success': True,
            'uuid': str(pop.uuid),
            'versao': version.versao,
            'integrity_hash': pop.integrity_hash,
        })

    # ----- Etapa 3: Archive -----
    @action(detail=True, methods=['post'], url_path='archive')
    def archive(self, request, uuid=None):
        """POST /api/pops/{uuid}/archive/"""
        pop = self.get_object()
        if pop.status == 'archived':
            return Response({'error': 'POP ja esta arquivado.'}, status=status.HTTP_400_BAD_REQUEST)

        pop.status = 'archived'
        pop.save(update_fields=['status', 'last_activity_at'])

        logger.info(f"[ARCHIVE] POP {pop.uuid} arquivado")
        return Response({'success': True, 'uuid': str(pop.uuid)})

    # ----- Etapa 3: Historico de versoes -----
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
