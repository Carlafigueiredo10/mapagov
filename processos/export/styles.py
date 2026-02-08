"""
Estilos centralizados para exportacao PDF/DOCX

Design System: DS Gov (cores institucionais)
Usado por: Analise de Riscos, POP, PE, Fluxograma

REGRA: Nenhum hardcode de cor nos renderers - tudo vem daqui.
"""

# =============================================================================
# CORES DS GOV
# =============================================================================

CORES = {
    "azul_primario": "#1351B4",
    "azul_escuro": "#071D41",
    "azul_claro": "#F0F4FF",
    "azul_capa_detalhe": "#1E5FBF",
    "cinza_texto": "#636363",
    "cinza_escuro": "#333333",
    "cinza_linha": "#E8E8E8",
    "cinza_fundo": "#F9FAFB",
    "branco": "#FFFFFF",
    "vermelho_alerta": "#E52207",
    "vermelho_fundo": "#FFF4F2",
    "verde_sucesso": "#168821",
}

# Cores por nivel de risco
CORES_NIVEL = {
    "CRITICO": "#dc2626",
    "ALTO": "#f97316",
    "MEDIO": "#eab308",
    "BAIXO": "#22c55e",
}

# Cores de fundo para niveis (tabelas)
CORES_NIVEL_FUNDO = {
    "CRITICO": "#FEE2E2",
    "ALTO": "#FFEDD5",
    "MEDIO": "#FEF9C3",
    "BAIXO": "#DCFCE7",
}


# =============================================================================
# ESPACAMENTO (pontos)
# =============================================================================

ESPACO = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 24,
}


# =============================================================================
# TIPOGRAFIA (tamanhos em pontos)
# =============================================================================

TIPO = {
    "titulo_capa": 32,
    "titulo": 18,
    "secao": 14,
    "secao_pdf": 13,
    "texto_medio": 12,
    "texto_base": 11,
    "subsecao": 10,
    "texto": 9,
    "small": 8,
    "tiny": 7,
}


# =============================================================================
# DEFAULTS DO DOCUMENTO
# =============================================================================

DEFAULTS = {
    "page_margin_cm": 2,
    "header_height_cm": 1.2,
    "footer_height_cm": 1.5,
    "line_height": 1.2,
}


# =============================================================================
# TEXTOS INSTITUCIONAIS
# =============================================================================

TEXTOS = {
    "nota_condicionais": "Campos condicionais podem nao aparecer quando nao se aplicam ao contexto da analise.",
    "modo_teste_publico": "Documento gerado em modo de teste publico (sem autenticacao).",
    "cabecalho_orgao": "MINISTERIO DA GESTAO E DA INOVACAO EM SERVICOS PUBLICOS",
}
