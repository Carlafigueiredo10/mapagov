"""
Busca de POPs por texto livre.

GET /api/pops/search/?q=aposentadoria&area=cgben&status=published&limit=20

- Postgres: SearchVector + SearchQuery (portuguese) + SearchRank
- SQLite (dev): __icontains em campos-chave
- Sem indice GIN por enquanto (volume baixo)
"""
from django.db import connection
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response

from processos.api.catalogo_serializers import POPListSerializer
from processos.models import Area, POP

MAX_LIMIT = 50
DEFAULT_LIMIT = 20
MIN_QUERY_LEN = 3


def _is_postgres():
    return connection.vendor == 'postgresql'


def _search_postgres(base_qs, query):
    """Full-text search com ranking via Postgres."""
    from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

    vector = SearchVector('nome_processo', weight='A', config='portuguese') + \
             SearchVector('codigo_processo', weight='A') + \
             SearchVector('macroprocesso', weight='B', config='portuguese') + \
             SearchVector('entrega_esperada', weight='C', config='portuguese')

    search_query = SearchQuery(query, config='portuguese')

    return base_qs.annotate(
        rank=SearchRank(vector, search_query),
    ).filter(rank__gt=0).order_by('-rank')


def _search_sqlite(base_qs, query):
    """Fallback icontains para SQLite (dev)."""
    return base_qs.filter(
        Q(nome_processo__icontains=query) |
        Q(codigo_processo__icontains=query) |
        Q(macroprocesso__icontains=query) |
        Q(entrega_esperada__icontains=query)
    )


@api_view(['GET'])
def search_pops(request):
    """
    GET /api/pops/search/?q=...&area=slug&status=published&limit=20

    Busca POPs por texto livre.
    """
    q = (request.query_params.get('q') or '').strip()
    if len(q) < MIN_QUERY_LEN:
        return Response(
            {'error': f'Busca requer no minimo {MIN_QUERY_LEN} caracteres.'},
            status=400,
        )

    status = request.query_params.get('status', 'published')
    area_slug = request.query_params.get('area')

    try:
        limit = min(int(request.query_params.get('limit', DEFAULT_LIMIT)), MAX_LIMIT)
    except (ValueError, TypeError):
        limit = DEFAULT_LIMIT

    # Base queryset
    qs = POP.objects.filter(is_deleted=False).select_related('area')

    if status:
        qs = qs.filter(status=status)

    if area_slug:
        area = Area.objects.filter(slug=area_slug, ativo=True).first()
        if area:
            area_ids = [area.id] + list(area.subareas.values_list('id', flat=True))
            qs = qs.filter(area_id__in=area_ids)
        else:
            return Response([])

    # Busca
    if _is_postgres():
        qs = _search_postgres(qs, q)
    else:
        qs = _search_sqlite(qs, q)

    results = qs[:limit]
    serializer = POPListSerializer(results, many=True)
    return Response(serializer.data)
