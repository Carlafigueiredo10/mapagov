"""
Camada de Leitura Institucional conforme o Guia de Gestao de Riscos do MGI

Este modulo implementa uma CAMADA DERIVADA para leitura gerencial dos riscos,
sem alterar a logica, scores ou classificacoes originais do sistema.

Conforme o Guia de Gestao de Riscos do MGI:
- 3 categorias institucionais: ESTRATEGICO, OPERACIONAL, INTEGRIDADE
- Apetite institucional padrao: MODERADO
- Riscos de Integridade: apetite ZERO (sempre fora do apetite)

IMPORTANTE:
- NAO modifica o score original (probabilidade x impacto)
- NAO substitui a categoria tecnica do risco
- NAO altera a matriz 5x5 ou os niveis internos
- Serve APENAS para leitura gerencial e reporte institucional
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import unicodedata


class CategoriaMGI(str, Enum):
    """Categorias de risco conforme Guia MGI"""
    ESTRATEGICO = "ESTRATEGICO"
    OPERACIONAL = "OPERACIONAL"
    INTEGRIDADE = "INTEGRIDADE"


class NivelMGI(str, Enum):
    """Niveis de risco para leitura gerencial conforme MGI

    Corte ajustado para pratica gerencial:
    - MODERADO inclui miolo (4-12) como dentro do apetite
    """
    PEQUENO = "PEQUENO"      # Score 1-3 (dentro do apetite)
    MODERADO = "MODERADO"    # Score 4-12 (apetite institucional)
    ALTO = "ALTO"            # Score 15-16 (fora do apetite)
    CRITICO = "CRITICO"      # Score 20-25 (fora do apetite)


# Ranges para nivel MGI (conforme Guia de GR do MGI)
# Nota: Score = P x I (1-25), onde P e I variam de 1 a 5
#
# Ajuste conforme pratica gerencial:
# - MODERADO inclui miolo (4-12) para refletir apetite institucional real
# - Evita "explodir" o relatorio com tudo fora do apetite
#
# IMPORTANTE: Este dict deve estar alinhado com calcular_nivel_mgi()
# Faixas continuas para cobrir todos os scores possiveis (1-25)
RANGES_NIVEL_MGI = {
    NivelMGI.PEQUENO: (1, 3),
    NivelMGI.MODERADO: (4, 12),
    NivelMGI.ALTO: (13, 16),      # Ajustado: era (15, 16), agora cobre 13-16
    NivelMGI.CRITICO: (17, 25),   # Ajustado: era (20, 25), agora cobre 17-25
}

# Apetite institucional padrao conforme MGI
APETITE_INSTITUCIONAL = NivelMGI.MODERADO


@dataclass
class LeituraMGI:
    """
    Leitura institucional de um risco conforme o Guia de GR do MGI.

    Esta estrutura NAO substitui os dados originais do risco.
    Serve para visualizacao gerencial e reporte institucional.
    """
    categoria_mgi: str
    nivel_mgi: str
    is_integridade: bool
    fora_do_apetite: bool
    justificativa_categoria: str
    justificativa_apetite: str
    # Rastreabilidade de integridade (quando is_integridade=True)
    integridade_motivo: str = ""
    integridade_gatilhos: List[str] = None  # type: ignore

    def __post_init__(self):
        if self.integridade_gatilhos is None:
            self.integridade_gatilhos = []


# =============================================================================
# MAPEAMENTO DE CATEGORIA TECNICA -> CATEGORIA MGI
# =============================================================================

# Palavras-chave FORTES que indicam risco de INTEGRIDADE
# Apenas sinais inequivocos - evita falsos positivos
PALAVRAS_INTEGRIDADE = {
    # Fraude e corrupcao (sinais fortes)
    "fraude", "corrupcao", "desvio", "suborno", "propina",
    "peculato", "concussao", "prevaricacao",
    # Conflito de interesses (sinais fortes)
    "conflito de interesse", "nepotismo", "favorecimento",
    # Manipulacao documental (sinais fortes)
    "adulteracao", "falsificacao",
    "documento falso", "informacao falsa",
    # Conduta ilicita (apenas o mais forte)
    "conduta ilicita",
    # Compliance (sinais fortes)
    "lavagem de dinheiro", "evasao", "sonegacao",
}
# NOTA: Removidos por ambiguidade: assedio, discriminacao, ma conduta,
# conduta antiética, manipulacao (pode ser de dados legitima)

# Palavras-chave que indicam risco ESTRATEGICO
PALAVRAS_ESTRATEGICO = {
    "estrategico", "estrategia", "longo prazo",
    "missao", "visao", "objetivo institucional",
    "governanca corporativa", "alta administracao",
    "planejamento estrategico", "plano plurianual",
    "imagem institucional", "reputacao",
    "relacoes externas", "parceiros estrategicos",
}

# Mapeamento base de categoria tecnica -> categoria MGI
MAPEAMENTO_CATEGORIA_BASE: Dict[str, CategoriaMGI] = {
    "OPERACIONAL": CategoriaMGI.OPERACIONAL,
    "FINANCEIRO": CategoriaMGI.OPERACIONAL,
    "TECNOLOGICO": CategoriaMGI.OPERACIONAL,
    "LEGAL": CategoriaMGI.OPERACIONAL,  # Default, pode ser reclassificado
    "REPUTACIONAL": CategoriaMGI.ESTRATEGICO,
    "IMPACTO_DESIGUAL": CategoriaMGI.ESTRATEGICO,
}


# =============================================================================
# FUNCOES DE DERIVACAO
# =============================================================================

def _normalizar_texto(texto: str) -> str:
    """Normaliza texto para comparacao (lowercase, sem acentos)"""
    if not texto:
        return ""
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(ch for ch in texto if not unicodedata.combining(ch))


def _contem_palavras_chave(texto: str, palavras: set) -> bool:
    """Verifica se texto contem alguma das palavras-chave"""
    texto_norm = _normalizar_texto(texto)
    for palavra in palavras:
        if palavra in texto_norm:
            return True
    return False


def derivar_is_integridade(
    titulo: str,
    descricao: str = "",
    justificativa: str = "",
    categoria_tecnica: str = "",  # pylint: disable=unused-argument
    bloco_origem: str = "",  # Mantido para retrocompatibilidade, nao usado
) -> tuple[bool, str, List[str]]:
    """
    Deriva se o risco e de Integridade.

    Criterio de deteccao (APENAS sinais fortes):
    - Palavras-chave inequivocas no titulo, descricao ou justificativa

    NOTA: Governanca fraca (BLOCO_5) NAO e integridade.
    Fragilidade decisoria e risco operacional, nao de integridade.

    Returns:
        tuple: (is_integridade, motivo, gatilhos)
        - motivo: descricao curta do porque foi classificado
        - gatilhos: lista de palavras-chave que acionaram (max 3)
    """
    texto_completo = f"{titulo} {descricao} {justificativa}"
    texto_norm = _normalizar_texto(texto_completo)

    # Unico criterio: palavras-chave FORTES de integridade
    gatilhos_encontrados = [
        p for p in PALAVRAS_INTEGRIDADE
        if p in texto_norm
    ]

    if gatilhos_encontrados:
        # Limitar a 3 gatilhos para exibicao
        gatilhos_exibir = gatilhos_encontrados[:3]
        motivo = "Integridade por palavra-chave forte"
        return True, motivo, gatilhos_exibir

    return False, "", []


def derivar_categoria_mgi(
    categoria_tecnica: str,
    titulo: str,
    descricao: str = "",
    justificativa: str = "",
    is_integridade: bool = False,
    tipo_origem: str = "",
) -> tuple[CategoriaMGI, str]:
    """
    Deriva a categoria MGI a partir da categoria tecnica e contexto.

    Regras de derivacao:
    1. Se is_integridade = True -> INTEGRIDADE
    2. Se contem palavras-chave estrategicas -> ESTRATEGICO
    3. Se tipo_origem indica planejamento estrategico -> ESTRATEGICO
    4. Caso contrario, usa mapeamento base

    Returns:
        tuple: (categoria_mgi, justificativa)
    """
    texto_completo = f"{titulo} {descricao} {justificativa}"

    # Regra 1: Integridade tem prioridade
    if is_integridade:
        return CategoriaMGI.INTEGRIDADE, "Risco classificado como de Integridade"

    # Regra 2: Palavras-chave estrategicas
    if _contem_palavras_chave(texto_completo, PALAVRAS_ESTRATEGICO):
        return CategoriaMGI.ESTRATEGICO, "Identificado por palavras-chave estrategicas"

    # Regra 3: Tipo de origem estrategico
    if tipo_origem in ("POLITICA", "PLANO"):
        return CategoriaMGI.ESTRATEGICO, f"Tipo de origem ({tipo_origem}) indica natureza estrategica"

    # Regra 4: Mapeamento base
    categoria_base = MAPEAMENTO_CATEGORIA_BASE.get(categoria_tecnica, CategoriaMGI.OPERACIONAL)
    return categoria_base, f"Derivado da categoria tecnica {categoria_tecnica}"


def calcular_nivel_mgi(score: int) -> NivelMGI:
    """
    Calcula o nivel MGI para leitura gerencial.

    Corte ajustado para pratica gerencial:
    - MODERADO inclui miolo (4-12) como dentro do apetite
    - Evita classificar tudo como fora do apetite

    Args:
        score: Score original do risco (P x I, 1-25)

    Returns:
        NivelMGI correspondente
    """
    # Mapeamento continuo (alinhado com RANGES_NIVEL_MGI):
    # 1-3   -> PEQUENO   (dentro do apetite)
    # 4-12  -> MODERADO  (apetite institucional)
    # 13-16 -> ALTO      (fora do apetite)
    # 17-25 -> CRITICO   (fora do apetite)

    if score <= 3:
        return NivelMGI.PEQUENO
    elif score <= 12:
        return NivelMGI.MODERADO
    elif score <= 16:
        return NivelMGI.ALTO
    else:
        return NivelMGI.CRITICO


def derivar_fora_do_apetite(
    nivel_mgi: NivelMGI,
    is_integridade: bool,
) -> tuple[bool, str]:
    """
    Deriva se o risco esta fora do apetite institucional.

    Conforme Guia MGI:
    - Apetite institucional padrao: MODERADO
    - Riscos de Integridade: apetite ZERO (sempre fora)
    - Riscos ALTO ou CRITICO: fora do apetite

    Returns:
        tuple: (fora_do_apetite, justificativa)
    """
    # Regra 1: Integridade tem apetite ZERO
    if is_integridade:
        return True, "Risco de Integridade (apetite institucional: ZERO)"

    # Regra 2: Nivel acima do apetite institucional
    if nivel_mgi in (NivelMGI.ALTO, NivelMGI.CRITICO):
        return True, f"Nivel {nivel_mgi.value} excede apetite institucional ({APETITE_INSTITUCIONAL.value})"

    return False, f"Nivel {nivel_mgi.value} dentro do apetite institucional"


# =============================================================================
# FUNCAO PRINCIPAL DE LEITURA MGI
# =============================================================================

def gerar_leitura_mgi(
    titulo: str,
    categoria_tecnica: str,
    score: int,
    descricao: str = "",
    justificativa: str = "",
    bloco_origem: str = "",
    tipo_origem: str = "",
) -> LeituraMGI:
    """
    Gera a leitura institucional de um risco conforme o Guia de GR do MGI.

    Esta funcao NAO modifica os dados originais do risco.
    Retorna uma estrutura separada para visualizacao gerencial.

    Args:
        titulo: Titulo do risco
        categoria_tecnica: Categoria original do sistema
        score: Score calculado (P x I)
        descricao: Descricao do risco
        justificativa: Justificativa da inferencia
        bloco_origem: Bloco que originou o risco (ex: BLOCO_1)
        tipo_origem: Tipo do objeto analisado (ex: PROJETO, POP)

    Returns:
        LeituraMGI com a leitura institucional
    """
    # 1. Derivar se e risco de integridade (com rastreabilidade)
    is_integridade, integ_motivo, integ_gatilhos = derivar_is_integridade(
        titulo=titulo,
        descricao=descricao,
        justificativa=justificativa,
        categoria_tecnica=categoria_tecnica,
        bloco_origem=bloco_origem,
    )

    # 2. Derivar categoria MGI
    categoria_mgi, just_categoria = derivar_categoria_mgi(
        categoria_tecnica=categoria_tecnica,
        titulo=titulo,
        descricao=descricao,
        justificativa=justificativa,
        is_integridade=is_integridade,
        tipo_origem=tipo_origem,
    )

    # 3. Calcular nivel MGI
    nivel_mgi = calcular_nivel_mgi(score)

    # 4. Derivar se esta fora do apetite
    fora_do_apetite, just_apetite = derivar_fora_do_apetite(
        nivel_mgi=nivel_mgi,
        is_integridade=is_integridade,
    )

    # Construir justificativa da categoria
    justificativa_categoria = just_categoria
    if is_integridade:
        gatilhos_str = ", ".join(integ_gatilhos) if integ_gatilhos else ""
        justificativa_categoria = f"{integ_motivo} ({gatilhos_str}). {just_categoria}"

    return LeituraMGI(
        categoria_mgi=categoria_mgi.value,
        nivel_mgi=nivel_mgi.value,
        is_integridade=is_integridade,
        fora_do_apetite=fora_do_apetite,
        justificativa_categoria=justificativa_categoria,
        justificativa_apetite=just_apetite,
        integridade_motivo=integ_motivo,
        integridade_gatilhos=integ_gatilhos,
    )


def gerar_leitura_mgi_lista(
    riscos: List[Dict[str, Any]],
    tipo_origem: str = "",
) -> List[Dict[str, Any]]:
    """
    Gera leitura MGI para uma lista de riscos.

    Retorna a mesma lista com campo adicional 'leitura_mgi'.
    NAO modifica os campos originais dos riscos.

    Args:
        riscos: Lista de dicts com dados dos riscos
        tipo_origem: Tipo do objeto analisado

    Returns:
        Lista de riscos com leitura_mgi adicionada
    """
    resultado = []

    for risco in riscos:
        # Criar copia do risco
        risco_com_mgi = {**risco}

        # Gerar leitura MGI apenas se score existe (risco avaliado)
        score = risco.get("score_risco")
        if score is not None:
            leitura = gerar_leitura_mgi(
                titulo=risco.get("titulo", ""),
                categoria_tecnica=risco.get("categoria", "OPERACIONAL"),
                score=int(score),
                descricao=risco.get("descricao", ""),
                justificativa=risco.get("justificativa", ""),
                bloco_origem=risco.get("bloco_origem", ""),
                tipo_origem=tipo_origem,
            )
            risco_com_mgi["leitura_mgi"] = {
                "categoria_mgi": leitura.categoria_mgi,
                "nivel_mgi": leitura.nivel_mgi,
                "is_integridade": leitura.is_integridade,
                "fora_do_apetite": leitura.fora_do_apetite,
                "justificativa_categoria": leitura.justificativa_categoria,
                "justificativa_apetite": leitura.justificativa_apetite,
                "integridade_motivo": leitura.integridade_motivo,
                "integridade_gatilhos": leitura.integridade_gatilhos,
            }
        else:
            # Risco pendente de avaliacao - sem leitura MGI
            risco_com_mgi["leitura_mgi"] = None

        resultado.append(risco_com_mgi)

    return resultado


# =============================================================================
# RESUMO PARA RELATORIO
# =============================================================================

def gerar_resumo_mgi(riscos_com_leitura: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Gera resumo da leitura MGI para secao do relatorio.

    Args:
        riscos_com_leitura: Lista de riscos ja com leitura_mgi

    Returns:
        Dict com resumo para o relatorio
    """
    total = len(riscos_com_leitura)

    # Filtrar apenas riscos avaliados (com leitura_mgi)
    riscos_avaliados = [r for r in riscos_com_leitura if r.get("leitura_mgi")]
    riscos_pendentes = total - len(riscos_avaliados)

    # Contagem por categoria MGI (apenas avaliados)
    por_categoria = {cat.value: 0 for cat in CategoriaMGI}
    for risco in riscos_avaliados:
        leitura = risco.get("leitura_mgi") or {}
        cat = leitura.get("categoria_mgi", "OPERACIONAL")
        por_categoria[cat] = por_categoria.get(cat, 0) + 1

    # Contagem por nivel MGI (apenas avaliados)
    por_nivel = {nivel.value: 0 for nivel in NivelMGI}
    for risco in riscos_avaliados:
        leitura = risco.get("leitura_mgi") or {}
        nivel = leitura.get("nivel_mgi", "MODERADO")
        por_nivel[nivel] = por_nivel.get(nivel, 0) + 1

    # Riscos fora do apetite
    fora_apetite = [
        r for r in riscos_avaliados
        if (r.get("leitura_mgi") or {}).get("fora_do_apetite", False)
    ]

    # Riscos de integridade
    integridade = [
        r for r in riscos_avaliados
        if (r.get("leitura_mgi") or {}).get("is_integridade", False)
    ]

    return {
        "total_riscos": total,
        "riscos_avaliados": len(riscos_avaliados),
        "riscos_pendentes": riscos_pendentes,
        "por_categoria_mgi": por_categoria,
        "por_nivel_mgi": por_nivel,
        "qtd_fora_apetite": len(fora_apetite),
        "qtd_integridade": len(integridade),
        "riscos_fora_apetite": [
            {
                "titulo": r.get("titulo"),
                "score": r.get("score_risco"),
                "nivel_mgi": (r.get("leitura_mgi") or {}).get("nivel_mgi"),
                "categoria_mgi": (r.get("leitura_mgi") or {}).get("categoria_mgi"),
                "is_integridade": (r.get("leitura_mgi") or {}).get("is_integridade"),
            }
            for r in fora_apetite
        ],
        "riscos_integridade": [
            {
                "titulo": r.get("titulo"),
                "score": r.get("score_risco"),
                "motivo": (r.get("leitura_mgi") or {}).get("integridade_motivo"),
                "gatilhos": (r.get("leitura_mgi") or {}).get("integridade_gatilhos", []),
            }
            for r in integridade
        ],
        "apetite_institucional": APETITE_INSTITUCIONAL.value,
    }
