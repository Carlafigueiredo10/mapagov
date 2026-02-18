"""
Geração de CP (Código de Produto) — produtos não-POP.

Formato: AA.PR.III ou AA.BB.PR.III (SNI)
Lock transacional via ControleIndicesProduto.
"""

import logging

from django.db import transaction

from processos.models_new import ControleIndicesProduto

logger = logging.getLogger(__name__)

# Catálogo de produtos (constantes por agora)
PRODUTOS = {
    "analise_riscos": "01",
    "planejamento_estrategico": "02",
}


def _carregar_prefixos_area() -> dict:
    """Carrega prefixos do model Area (fonte de verdade). Fallback SNI se banco indisponível."""
    try:
        from processos.models import Area
        return {a.codigo: a.prefixo for a in Area.objects.filter(ativo=True)}
    except Exception:
        return {
            "CGBEN": "01", "CGPAG": "02", "COATE": "03", "CGGAF": "04",
            "DIGEP": "05", "DIGEP-RO": "05.01", "DIGEP-RR": "05.02", "DIGEP-AP": "05.03",
            "CGRIS": "06", "CGCAF": "07", "CGECO": "08",
            "COADM": "09", "COGES": "10", "CDGEP": "11",
        }


def gerar_cp(area_codigo: str, produto_codigo: str) -> str:
    """
    Gera CP com lock transacional.

    Formato: AA.PR.III ou AA.BB.PR.III
    Exemplo: 03.01.001 (COATE, Análise de Riscos, Item 001)
             05.01.03.001 (DIGEP-RO, Produto 03, Item 001)

    Args:
        area_codigo: Código da área (ex: 'COATE', 'DIGEP-RO')
        produto_codigo: Código do produto, 2 dígitos (ex: '01', '02')

    Returns:
        CP único (ex: '03.01.001')

    Raises:
        ValueError: se area_codigo não encontrada no mapa de áreas
    """
    from processos.domain.governanca.normalize import resolve_prefixo_cp

    prefixos = _carregar_prefixos_area()
    prefixo = resolve_prefixo_cp(area_codigo, prefixos)

    with transaction.atomic():
        controle, _ = ControleIndicesProduto.objects.select_for_update().get_or_create(
            area_codigo=area_codigo,
            produto_codigo=produto_codigo,
            defaults={'ultimo_indice': 0}
        )
        seq = controle.ultimo_indice + 1
        controle.ultimo_indice = seq
        controle.save()

    return f"{prefixo}.{produto_codigo}.{seq:03d}"


def atribuir_cp_se_necessario(obj, area_codigo: str) -> bool:
    """
    Atribui CP ao objeto se ainda não tem e área é conhecida.

    Padrão idempotente: usa update com filtro codigo_cp__isnull=True.
    Request duplicado não gera segundo CP.

    Args:
        obj: instância de AnaliseRiscos ou PlanejamentoEstrategico (com .codigo_cp e .produto_codigo)
        area_codigo: código da área (ex: 'COATE', 'DIGEP-RO')

    Returns:
        True se CP foi atribuído, False se já tinha ou área inválida
    """
    if obj.codigo_cp or not area_codigo:
        return False

    try:
        cp = gerar_cp(area_codigo, obj.produto_codigo)
    except ValueError:
        logger.warning(f"[CP] Área desconhecida '{area_codigo}' — CP não gerado para {obj.__class__.__name__} {obj.pk}")
        return False

    updated = obj.__class__.objects.filter(
        pk=obj.pk, codigo_cp__isnull=True
    ).update(codigo_cp=cp)

    if updated:
        obj.codigo_cp = cp
        logger.info(f"[CP] {cp} atribuído a {obj.__class__.__name__} {obj.pk}")
        return True

    return False
