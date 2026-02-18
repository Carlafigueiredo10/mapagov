"""
Catálogo unificado de produtos MapaGov + matching determinístico.

Centraliza os 10 produtos do portfólio (exceto "geral") com sinônimos
para detecção de intenção sem depender de LLM.
"""

import re
import unicodedata
from difflib import SequenceMatcher

# ─── Catálogo ────────────────────────────────────────────────────────────

CATALOGO_PRODUTOS = {
    "pop": {
        "nome": "Mapear processo (POP)",
        "status": "disponivel",
        "rota": "/pop",
        "descricao_curta": (
            "Registro estruturado de atividades, responsáveis e documentos "
            "de um processo de trabalho."
        ),
        "sinonimos": (
            "pop", "procedimento operacional", "procedimento",
            "passo a passo", "mapeamento de processo", "mapear processo",
            "mapeamento", "cap",
        ),
    },
    "riscos": {
        "nome": "Análise de Riscos",
        "status": "disponivel",
        "rota": "/riscos",
        "descricao_curta": (
            "Identificação e avaliação de riscos associados a um processo, "
            "com base no Guia de Gestão de Riscos do MGI."
        ),
        "sinonimos": (
            "risco", "riscos", "analise de riscos", "analise de risco",
            "gestao de riscos", "mitigar", "probabilidade e impacto",
        ),
    },
    "planejamento": {
        "nome": "Planejamento Estratégico",
        "status": "homologacao",
        "rota": "/planejamento-estrategico",
        "descricao_curta": (
            "Construção de planejamento estratégico institucional "
            "com modelos reconhecidos de gestão."
        ),
        "sinonimos": (
            "planejamento", "planejamento estrategico", "planejar",
            "metas", "indicadores", "objetivos estrategicos",
        ),
    },
    "fluxograma": {
        "nome": "Gerador de Fluxograma",
        "status": "homologacao",
        "rota": "/fluxograma",
        "descricao_curta": (
            "Representação visual do fluxo de um processo em notação BPMN."
        ),
        "sinonimos": (
            "fluxograma", "bpmn", "fluxo de processo", "diagrama de processo",
        ),
    },
    "dashboard": {
        "nome": "Painel Executivo",
        "status": "desenvolvimento",
        "rota": "/painel",
        "descricao_curta": (
            "Indicadores e visão consolidada das iniciativas."
        ),
        "sinonimos": (
            "painel", "painel executivo", "dashboard", "indicadores",
            "visao consolidada",
        ),
    },
    "acao": {
        "nome": "Plano de Ação e Acompanhamento",
        "status": "planejado",
        "rota": None,
        "descricao_curta": (
            "Define ações, responsáveis e prazos para execução e monitoramento."
        ),
        "sinonimos": (
            "plano de acao", "plano de ação", "acompanhamento",
            "acoes", "ações", "5w2h",
        ),
    },
    "dossie": {
        "nome": "Dossiê Consolidado de Governança",
        "status": "planejado",
        "rota": None,
        "descricao_curta": (
            "Reúne todos os documentos e análises gerados pelo sistema."
        ),
        "sinonimos": (
            "dossie", "dossiê", "dossie consolidado", "dossiê consolidado",
            "dossie de governanca", "dossiê de governança",
        ),
    },
    "documentos": {
        "nome": "Relatório Técnico Consolidado",
        "status": "planejado",
        "rota": None,
        "descricao_curta": (
            "Formaliza o histórico completo do processo para arquivamento."
        ),
        "sinonimos": (
            "relatorio tecnico", "relatório técnico", "rtc",
            "relatorio tecnico consolidado", "relatório técnico consolidado",
            "relatorio consolidado",
        ),
    },
    "conformidade": {
        "nome": "Relatório de Conformidade",
        "status": "planejado",
        "rota": None,
        "descricao_curta": (
            "Verifica se o processo seguiu etapas e prazos previstos."
        ),
        "sinonimos": (
            "conformidade", "relatorio de conformidade",
            "relatório de conformidade", "compliance",
        ),
    },
    "artefatos": {
        "nome": "Revisão e Adequação de Documentos",
        "status": "planejado",
        "rota": None,
        "descricao_curta": (
            "Ajusta documentos à linguagem simples e padrões institucionais."
        ),
        "sinonimos": (
            "artefatos", "revisao de documentos", "revisão de documentos",
            "adequacao", "adequação", "linguagem simples",
        ),
    },
}

# ─── Normalização ────────────────────────────────────────────────────────

def _norm(texto: str) -> str:
    """Normaliza: remove acentos, lowercase, pontuação→espaço, trim."""
    if not texto:
        return ""
    nfd = unicodedata.normalize("NFD", texto)
    sem_acentos = "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn")
    t = sem_acentos.lower()
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


# ─── Matching determinístico ─────────────────────────────────────────────

_FUZZY_THRESHOLD = 0.82
_MIN_FUZZY_LEN = 6


def _ngrams(tokens: list, n: int):
    """Gera janelas de n tokens consecutivos."""
    for i in range(max(0, len(tokens) - n + 1)):
        yield " ".join(tokens[i : i + n])


def match_produto(mensagem: str, catalogo: dict | None = None) -> tuple | None:
    """
    Retorna (chave_produto, origem) ou None.
    origem = "substring" | "fuzzy" — para logging/métricas.
    """
    if catalogo is None:
        catalogo = CATALOGO_PRODUTOS

    msg = _norm(mensagem)
    if not msg:
        return None

    # Passagem 1: substring exata (longest match wins)
    best_key = None
    best_len = 0
    for key, prod in catalogo.items():
        for sin in prod.get("sinonimos", ()):
            s = _norm(sin)
            if not s:
                continue
            if s in msg and len(s) > best_len:
                best_key = key
                best_len = len(s)
    if best_key:
        return (best_key, "substring")

    # Passagem 2: fuzzy por n-grams (3, 2, 1 tokens), só >= 6 chars
    tokens = msg.split()
    for key, prod in catalogo.items():
        for sin in prod.get("sinonimos", ()):
            s = _norm(sin)
            if len(s) < _MIN_FUZZY_LEN:
                continue
            for n in (3, 2, 1):
                for chunk in _ngrams(tokens, n):
                    if len(chunk) < _MIN_FUZZY_LEN:
                        continue
                    if SequenceMatcher(None, chunk, s).ratio() >= _FUZZY_THRESHOLD:
                        return (key, "fuzzy")

    return None
