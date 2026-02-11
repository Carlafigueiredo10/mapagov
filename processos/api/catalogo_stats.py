from datetime import timedelta

from django.db.models import Avg, Count, Q
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from processos.models import Area, POP, PopVersion


@api_view(['GET'])
def stats_global(request):
    """
    GET /api/stats/
    Metricas globais: totais por status, ranking de areas, atividade recente.
    """
    base_qs = POP.objects.filter(is_deleted=False)

    totais = {
        'pops': base_qs.count(),
        'publicados': base_qs.filter(status='published').count(),
        'rascunhos': base_qs.filter(status='draft').count(),
        'arquivados': base_qs.filter(status='archived').count(),
        'versoes': PopVersion.objects.count(),
        'areas': Area.objects.filter(ativo=True, area_pai__isnull=True).count(),
    }

    # Ranking de areas por quantidade de POPs
    areas_ranking = list(
        Area.objects.filter(ativo=True).annotate(
            pop_count=Count('pops', filter=Q(pops__is_deleted=False))
        ).order_by('-pop_count').values('codigo', 'nome_curto', 'pop_count')[:10]
    )

    # Atividade ultimos 30 dias
    trinta_dias = timezone.now() - timedelta(days=30)
    atividade_30d = {
        'pops_criados': base_qs.filter(created_at__gte=trinta_dias).count(),
        'publicacoes': PopVersion.objects.filter(published_at__gte=trinta_dias).count(),
    }

    return Response({
        'totais': totais,
        'atividade_30d': atividade_30d,
        'areas_ranking': areas_ranking,
    })


@api_view(['GET'])
def stats_area(request, slug):
    """
    GET /api/stats/areas/{slug}/
    Metricas de uma area especifica.
    """
    area = Area.objects.filter(slug=slug, ativo=True).first()
    if not area:
        return Response({'error': 'Area nao encontrada.'}, status=404)

    # Incluir sub-areas
    area_ids = [area.id] + list(area.subareas.values_list('id', flat=True))
    pops_qs = POP.objects.filter(area_id__in=area_ids, is_deleted=False)

    status_counts = {
        item['status']: item['count']
        for item in pops_qs.values('status').annotate(count=Count('id'))
    }

    return Response({
        'area': {
            'codigo': area.codigo,
            'nome': area.nome_curto,
            'slug': area.slug,
        },
        'totais': {
            'pops': pops_qs.count(),
            'por_status': status_counts,
        },
    })
