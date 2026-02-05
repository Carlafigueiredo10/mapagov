"""
Adaptador de Bloco B para Motor de Inferencia

Este modulo converte os campos estruturados do Bloco B (contexto operacional)
em sinais que podem alimentar o motor de inferencia sem reescrever as 34 regras.

PRINCIPIOS:
1. Se campo estruturado existe -> usa ele
2. Se nao existe -> fallback para texto antigo (sem heuristica agressiva)
3. NAO_SEI NUNCA vira NAO - preserva a incerteza
4. Chave ausente != lista vazia ([] = respondeu "nenhum")

MAPEAMENTOS:
- recursos -> sinais de dependencia (TI, PESSOAS)
- frequencia -> sinal de exposicao
- sla -> sinal de pressao normativa (SIM/NAO/DESCONHECIDO)
- dependencia -> sinal de dependencia externa (SISTEMAS/TERCEIROS/AMBOS/DESCONHECIDO)
- incidentes -> sinal de historico (SIM/NAO/DESCONHECIDO)
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class SinalMotor(str, Enum):
    """Sinais padronizados para o motor"""
    SIM = "SIM"
    NAO = "NAO"
    DESCONHECIDO = "DESCONHECIDO"  # Mapeado de NAO_SEI ou ausencia de dado


class SinalDependencia(str, Enum):
    """Tipos de dependencia detectados"""
    NENHUMA = "NENHUMA"
    SISTEMAS = "SISTEMAS"
    TERCEIROS = "TERCEIROS"
    AMBOS = "AMBOS"
    DESCONHECIDO = "DESCONHECIDO"


class SinalExposicao(str, Enum):
    """Nivel de exposicao baseado na frequencia"""
    BAIXA = "BAIXA"        # Pontual
    MEDIA = "MEDIA"        # Periodico, sob demanda
    ALTA = "ALTA"          # Continuo


@dataclass
class SinaisBlocoB:
    """
    Sinais extraidos do Bloco B para alimentar o motor.

    Todos os campos podem ser None se nao foi possivel determinar.
    O motor deve tratar None como "nao avaliado" (nao como NAO).
    """
    # Dependencias
    depende_ti: Optional[str] = None          # SIM/NAO/DESCONHECIDO
    depende_pessoas: Optional[str] = None     # SIM/NAO/DESCONHECIDO
    depende_orcamento: Optional[str] = None   # SIM/NAO/DESCONHECIDO

    # Exposicao
    nivel_exposicao: Optional[str] = None     # BAIXA/MEDIA/ALTA

    # Pressoes
    tem_sla: Optional[str] = None             # SIM/NAO/DESCONHECIDO
    sla_detalhe: Optional[str] = None         # Texto livre

    # Dependencia externa
    tipo_dependencia: Optional[str] = None    # NENHUMA/SISTEMAS/TERCEIROS/AMBOS/DESCONHECIDO
    dependencia_detalhe: Optional[str] = None  # Texto livre

    # Historico
    tem_incidentes: Optional[str] = None      # SIM/NAO/DESCONHECIDO
    incidentes_detalhe: Optional[str] = None  # Texto livre

    # Impacto (ancora)
    impacto_texto: Optional[str] = None       # Texto livre

    # Atores
    atores_texto: Optional[str] = None        # Texto livre


def adaptar_bloco_b(bloco_b: Dict[str, Any]) -> SinaisBlocoB:
    """
    Converte campos do Bloco B em sinais para o motor.

    Args:
        bloco_b: Dict com campos do Bloco B (estruturados e/ou texto)

    Returns:
        SinaisBlocoB com sinais normalizados
    """
    sinais = SinaisBlocoB()

    # === RECURSOS (checklist) ===
    # Chave ausente = nao respondeu, [] = nenhum recurso
    if "recursos" in bloco_b:
        recursos = bloco_b.get("recursos", [])
        if isinstance(recursos, list):
            sinais.depende_ti = SinalMotor.SIM.value if "TI" in recursos else SinalMotor.NAO.value
            sinais.depende_pessoas = SinalMotor.SIM.value if "PESSOAS" in recursos else SinalMotor.NAO.value
            sinais.depende_orcamento = SinalMotor.SIM.value if "ORCAMENTO" in recursos else SinalMotor.NAO.value
    else:
        # Fallback: tentar extrair do texto antigo (sem heuristica agressiva)
        texto_recursos = bloco_b.get("recursos_necessarios", "").lower()
        if texto_recursos:
            # Apenas palavras-chave obvias
            if any(p in texto_recursos for p in ["sistema", "ti", "software", "aplicativo"]):
                sinais.depende_ti = SinalMotor.SIM.value
            if any(p in texto_recursos for p in ["pessoa", "equipe", "servidor", "funcionario"]):
                sinais.depende_pessoas = SinalMotor.SIM.value
            if any(p in texto_recursos for p in ["orcamento", "verba", "recurso financeiro"]):
                sinais.depende_orcamento = SinalMotor.SIM.value

    # === FREQUENCIA ===
    if "frequencia" in bloco_b:
        freq = bloco_b.get("frequencia", "")
        if freq == "CONTINUO":
            sinais.nivel_exposicao = SinalExposicao.ALTA.value
        elif freq in ("PERIODICO", "SOB_DEMANDA"):
            sinais.nivel_exposicao = SinalExposicao.MEDIA.value
        elif freq == "PONTUAL":
            sinais.nivel_exposicao = SinalExposicao.BAIXA.value
    else:
        # Fallback do campo antigo (se existir enum valido)
        freq_antiga = bloco_b.get("frequencia_execucao", "")
        if freq_antiga == "CONTINUO":
            sinais.nivel_exposicao = SinalExposicao.ALTA.value
        elif freq_antiga in ("PERIODICO", "SOB_DEMANDA"):
            sinais.nivel_exposicao = SinalExposicao.MEDIA.value
        elif freq_antiga == "PONTUAL":
            sinais.nivel_exposicao = SinalExposicao.BAIXA.value

    # === SLA ===
    if "sla" in bloco_b:
        sla = bloco_b.get("sla", "")
        if sla == "SIM":
            sinais.tem_sla = SinalMotor.SIM.value
        elif sla == "NAO":
            sinais.tem_sla = SinalMotor.NAO.value
        elif sla == "NAO_SEI":
            # IMPORTANTE: NAO_SEI nunca vira NAO
            sinais.tem_sla = SinalMotor.DESCONHECIDO.value
        sinais.sla_detalhe = bloco_b.get("sla_detalhe", "")
    else:
        # Fallback: tentar extrair do texto antigo
        texto_sla = bloco_b.get("prazos_slas", "").lower()
        if texto_sla:
            if any(p in texto_sla for p in ["nao ha", "nao existe", "sem prazo"]):
                sinais.tem_sla = SinalMotor.NAO.value
            elif any(p in texto_sla for p in ["lei", "decreto", "prazo", "sla", "dias"]):
                sinais.tem_sla = SinalMotor.SIM.value
            sinais.sla_detalhe = bloco_b.get("prazos_slas", "")

    # === DEPENDENCIA EXTERNA ===
    if "dependencia" in bloco_b:
        dep = bloco_b.get("dependencia", "")
        if dep == "NAO":
            sinais.tipo_dependencia = SinalDependencia.NENHUMA.value
        elif dep == "SISTEMAS":
            sinais.tipo_dependencia = SinalDependencia.SISTEMAS.value
        elif dep == "TERCEIROS":
            sinais.tipo_dependencia = SinalDependencia.TERCEIROS.value
        elif dep == "AMBOS":
            sinais.tipo_dependencia = SinalDependencia.AMBOS.value
        elif dep == "NAO_SEI":
            # IMPORTANTE: NAO_SEI nunca vira NAO
            sinais.tipo_dependencia = SinalDependencia.DESCONHECIDO.value
        sinais.dependencia_detalhe = bloco_b.get("dependencia_detalhe", "")
    else:
        # Fallback: tentar extrair do texto antigo
        texto_dep = bloco_b.get("dependencias_externas", "").lower()
        if texto_dep:
            tem_sistemas = any(p in texto_dep for p in ["sistema", "api", "integracao"])
            tem_terceiros = any(p in texto_dep for p in ["terceiro", "fornecedor", "orgao", "empresa"])
            if any(p in texto_dep for p in ["nao ha", "nao existe", "sem dependencia"]):
                sinais.tipo_dependencia = SinalDependencia.NENHUMA.value
            elif tem_sistemas and tem_terceiros:
                sinais.tipo_dependencia = SinalDependencia.AMBOS.value
            elif tem_sistemas:
                sinais.tipo_dependencia = SinalDependencia.SISTEMAS.value
            elif tem_terceiros:
                sinais.tipo_dependencia = SinalDependencia.TERCEIROS.value
            sinais.dependencia_detalhe = bloco_b.get("dependencias_externas", "")

    # === INCIDENTES ===
    if "incidentes" in bloco_b:
        inc = bloco_b.get("incidentes", "")
        if inc == "SIM":
            sinais.tem_incidentes = SinalMotor.SIM.value
        elif inc == "NAO":
            sinais.tem_incidentes = SinalMotor.NAO.value
        elif inc == "NAO_SEI":
            # IMPORTANTE: NAO_SEI nunca vira NAO
            sinais.tem_incidentes = SinalMotor.DESCONHECIDO.value
        sinais.incidentes_detalhe = bloco_b.get("incidentes_detalhe", "")
    else:
        # Fallback: tentar extrair do texto antigo
        texto_inc = bloco_b.get("historico_problemas", "").lower()
        if texto_inc:
            if any(p in texto_inc for p in ["nao ha", "sem registro", "nao houve"]):
                sinais.tem_incidentes = SinalMotor.NAO.value
            elif any(p in texto_inc for p in ["problema", "incidente", "falha", "erro", "atraso"]):
                sinais.tem_incidentes = SinalMotor.SIM.value
            sinais.incidentes_detalhe = bloco_b.get("historico_problemas", "")

    # === TEXTOS LIVRES (sempre preservados) ===
    sinais.impacto_texto = bloco_b.get("consequencia_texto") or bloco_b.get("impacto_se_falhar", "")
    sinais.atores_texto = bloco_b.get("atores_envolvidos_texto") or bloco_b.get("areas_atores_envolvidos", "")

    return sinais


def sinais_para_dict(sinais: SinaisBlocoB) -> Dict[str, Any]:
    """Converte SinaisBlocoB para dict (para JSON/API)"""
    return {
        "depende_ti": sinais.depende_ti,
        "depende_pessoas": sinais.depende_pessoas,
        "depende_orcamento": sinais.depende_orcamento,
        "nivel_exposicao": sinais.nivel_exposicao,
        "tem_sla": sinais.tem_sla,
        "sla_detalhe": sinais.sla_detalhe,
        "tipo_dependencia": sinais.tipo_dependencia,
        "dependencia_detalhe": sinais.dependencia_detalhe,
        "tem_incidentes": sinais.tem_incidentes,
        "incidentes_detalhe": sinais.incidentes_detalhe,
        "impacto_texto": sinais.impacto_texto,
        "atores_texto": sinais.atores_texto,
    }


def mapear_para_bloco_3(sinais: SinaisBlocoB) -> Dict[str, str]:
    """
    Mapeia sinais do Bloco B para perguntas do BLOCO_3 (Tecnologia).

    Usado para enriquecer a inferencia quando o usuario nao respondeu
    o BLOCO_3 diretamente mas forneceu informacoes no Bloco B.

    Returns:
        Dict com Q1-Q5 do BLOCO_3, apenas chaves com valor determinado
    """
    respostas = {}

    # Q1 - Dependencia de sistemas
    if sinais.depende_ti == SinalMotor.SIM.value:
        if sinais.tipo_dependencia in (SinalDependencia.SISTEMAS.value, SinalDependencia.AMBOS.value):
            respostas["Q1"] = "DEPENDE_CRITICAMENTE"
        else:
            respostas["Q1"] = "DEPENDE_PARCIALMENTE"
    elif sinais.depende_ti == SinalMotor.NAO.value:
        respostas["Q1"] = "NAO_DEPENDE"
    # Se DESCONHECIDO, nao mapeia (evita falso negativo)

    # Q5 - Historico de falhas (se incidentes e sobre TI)
    if sinais.tem_incidentes == SinalMotor.SIM.value and sinais.depende_ti == SinalMotor.SIM.value:
        # Conservador: mapeia para OCASIONAL, nao RECORRENTE
        respostas["Q5"] = "OCASIONAL"
    elif sinais.tem_incidentes == SinalMotor.NAO.value:
        respostas["Q5"] = "NAO"
    # Se DESCONHECIDO, nao mapeia

    return respostas


def mapear_para_bloco_1(sinais: SinaisBlocoB) -> Dict[str, str]:
    """
    Mapeia sinais do Bloco B para perguntas do BLOCO_1 (Terceiros).

    Returns:
        Dict com Q1-Q4 do BLOCO_1, apenas chaves com valor determinado
    """
    respostas = {}

    # Q1 - Dependencia de terceiros
    if sinais.tipo_dependencia == SinalDependencia.NENHUMA.value:
        respostas["Q1"] = "NAO_EXISTE"
    elif sinais.tipo_dependencia in (SinalDependencia.TERCEIROS.value, SinalDependencia.AMBOS.value):
        # Conservador: mapeia para MEDIA, nao ALTA
        respostas["Q1"] = "MEDIA"
    # Se DESCONHECIDO ou SISTEMAS, nao mapeia Q1

    return respostas


def mapear_para_bloco_4(sinais: SinaisBlocoB) -> Dict[str, str]:
    """
    Mapeia sinais do Bloco B para perguntas do BLOCO_4 (Prazos/SLAs).

    Returns:
        Dict com Q1-Q5 do BLOCO_4, apenas chaves com valor determinado
    """
    respostas = {}

    # Q1 - Existencia de prazos
    if sinais.tem_sla == SinalMotor.SIM.value:
        # Conservador: mapeia para COM_MARGEM, nao CRITICOS
        respostas["Q1"] = "EXISTEM_COM_MARGEM"
    elif sinais.tem_sla == SinalMotor.NAO.value:
        respostas["Q1"] = "NAO_EXISTEM"
    # Se DESCONHECIDO, nao mapeia

    return respostas
