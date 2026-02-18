"""
Endpoint unificado de busca por código SNI.

GET /api/produtos/busca/?codigo=03.01.001

Identifica formato (CAP vs CP) e busca no model correto.
"""
import re
import logging

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

# Regex de formato — ordem importa (CAP é mais longo, testar primeiro)
RE_CAP = re.compile(r"^\d{2}\.\d{2}\.\d{2}\.\d{2}\.\d{3}$")
RE_CP = re.compile(r"^\d{2}(?:\.\d{2})?\.\d{2}\.\d{3}$")


@api_view(["GET"])
def buscar_por_codigo(request):
    """
    Busca produto por código SNI (CAP ou CP).

    Query params:
        codigo: código SNI (ex: '03.01.001', '01.02.03.04.108')

    Respostas:
        200: produto encontrado
        400: código ausente ou formato inválido
        404: código válido mas não encontrado
    """
    codigo = (request.GET.get("codigo") or "").strip()

    if not codigo:
        return Response(
            {"erro": "parâmetro 'codigo' é obrigatório"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 1. Tenta CAP (formato mais longo, testar primeiro)
    if RE_CAP.match(codigo):
        return _buscar_cap(codigo)

    # 2. Tenta CP
    if RE_CP.match(codigo):
        return _buscar_cp(codigo)

    # 3. Nenhum match
    return Response(
        {"erro": "formato de código inválido"},
        status=status.HTTP_400_BAD_REQUEST,
    )


def _buscar_cap(codigo: str) -> Response:
    """Busca POP por codigo_processo (CAP)."""
    from processos.models import POP

    pop = POP.objects.filter(
        codigo_processo=codigo, is_deleted=False
    ).first()

    if not pop:
        return Response(
            {"erro": "código não encontrado"},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response({
        "tipo": "pop",
        "codigo": codigo,
        "id": str(pop.uuid),
        "area_codigo": pop.area_codigo or "",
        "status": pop.status,
        "nome": pop.nome_processo or "",
    })


def _buscar_cp(codigo: str) -> Response:
    """Busca produto não-POP por codigo_cp (CP)."""
    from processos.models_analise_riscos import AnaliseRiscos
    from processos.models_new import PlanejamentoEstrategico

    # AR primeiro
    ar = AnaliseRiscos.objects.filter(codigo_cp=codigo).first()
    if ar:
        return Response({
            "tipo": "analise_riscos",
            "codigo": codigo,
            "id": str(ar.id),
            "area_codigo": ar.area_decipex or "",
            "status": ar.status,
            "nome": f"Análise de Riscos - {ar.tipo_origem}",
        })

    # PE
    pe = PlanejamentoEstrategico.objects.filter(codigo_cp=codigo).first()
    if pe:
        return Response({
            "tipo": "planejamento_estrategico",
            "codigo": codigo,
            "id": str(pe.id),
            "area_codigo": pe.unidade or "",
            "status": pe.status,
            "nome": pe.titulo or "",
        })

    return Response(
        {"erro": "código não encontrado"},
        status=status.HTTP_404_NOT_FOUND,
    )
