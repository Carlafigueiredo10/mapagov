"""
Regras de Inferencia de Riscos

34 regras distribuidas em 6 blocos.

Principio:
- Nao pergunta "qual e o risco"
- Cruza fatores e FAZ o risco aparecer

Cada regra segue o padrao:
SE (intensidade/dependencia)
E (formalizacao/controle)
E (criticidade/variabilidade)
ENTAO gerar_risco(...)

Riscos inferidos entram como:
- status = RASCUNHO (validacao final na Etapa 3)
- fonte_sugestao = HELENA_INFERENCIA
- grau_confianca explicito
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from .enums import CategoriaRisco, GrauConfianca


@dataclass
class RiscoInferido:
    """Estrutura de um risco inferido pelo sistema"""
    titulo: str
    categoria: str
    bloco_origem: str
    perguntas_acionadoras: List[str]
    regra_id: str
    grau_confianca: str
    justificativa: str


# =============================================================================
# BLOCO 1 - DEPENDENCIA DE TERCEIROS
# =============================================================================

def inferir_riscos_bloco_1(respostas: Dict[str, str]) -> List[RiscoInferido]:
    """
    Infere riscos do Bloco 1 - Dependencia de Terceiros

    Perguntas:
    Q1 - dependencia_terceiros: NAO_EXISTE | BAIXA | MEDIA | ALTA
    Q2 - formalizacao: FORMAL | PARCIAL | INFORMAL
    Q3 - natureza_contratacao: CONTRATO_VIGENTE | CONTRATACAO_FUTURA | LICITACAO_NAO_REALIZADA | CONTRATO_TEMPORARIO_SAZONAL | NAO_SE_APLICA
    Q4 - criticidade_entrega: NAO_CRITICA | IMPORTANTE | CRITICA_PARA_RESULTADO_FINAL
    """
    riscos = []
    q1 = respostas.get("Q1", "")
    q2 = respostas.get("Q2", "")
    q3 = respostas.get("Q3", "")
    q4 = respostas.get("Q4", "")

    # Se nao ha dependencia, nenhum risco
    if q1 == "NAO_EXISTE":
        return riscos

    # RISCO 1 - Atraso por dependencia externa
    if q1 in ("MEDIA", "ALTA") and q4 in ("IMPORTANTE", "CRITICA_PARA_RESULTADO_FINAL"):
        riscos.append(RiscoInferido(
            titulo="Risco de atraso por dependencia de terceiros",
            categoria=CategoriaRisco.OPERACIONAL.value,
            bloco_origem="BLOCO_1",
            perguntas_acionadoras=["Q1", "Q4"],
            regra_id="B1_R1_ATRASO_DEPENDENCIA",
            grau_confianca=GrauConfianca.MEDIO.value,
            justificativa=f"Dependencia {q1.lower()} de terceiros com entrega {q4.lower().replace('_', ' ')}, indicando risco de atraso na execucao."
        ))

    # RISCO 2 - Descontinuidade por falta de garantias
    if q1 == "ALTA" and q2 in ("PARCIAL", "INFORMAL"):
        riscos.append(RiscoInferido(
            titulo="Risco de descontinuidade por terceiros sem garantias formais",
            categoria=CategoriaRisco.OPERACIONAL.value,
            bloco_origem="BLOCO_1",
            perguntas_acionadoras=["Q1", "Q2"],
            regra_id="B1_R2_DESCONTINUIDADE",
            grau_confianca=GrauConfianca.ALTO.value,
            justificativa="Dependencia alta de terceiros associada a ausencia de instrumento formal vigente, comprometendo a continuidade da entrega."
        ))

    # RISCO 3 - Risco legal por relacao informal
    if q1 in ("MEDIA", "ALTA") and q2 == "INFORMAL":
        riscos.append(RiscoInferido(
            titulo="Risco legal decorrente de relacao informal com terceiros",
            categoria=CategoriaRisco.LEGAL.value,
            bloco_origem="BLOCO_1",
            perguntas_acionadoras=["Q1", "Q2"],
            regra_id="B1_R3_LEGAL_INFORMAL",
            grau_confianca=GrauConfianca.ALTO.value,
            justificativa="Dependencia significativa de terceiros sem formalizacao adequada, expondo a organizacao a questionamentos juridicos."
        ))

    # RISCO 4 - Inviabilizacao por contratacao futura
    if q3 in ("CONTRATACAO_FUTURA", "LICITACAO_NAO_REALIZADA") and q4 == "CRITICA_PARA_RESULTADO_FINAL":
        riscos.append(RiscoInferido(
            titulo="Risco de inviabilizacao por contratacao futura nao assegurada",
            categoria=CategoriaRisco.OPERACIONAL.value,
            bloco_origem="BLOCO_1",
            perguntas_acionadoras=["Q3", "Q4"],
            regra_id="B1_R4_CONTRATACAO_FUTURA",
            grau_confianca=GrauConfianca.ALTO.value,
            justificativa="Entrega critica depende de contratacao ainda nao realizada, com risco de inviabilizacao do objeto."
        ))

    # RISCO 5 - Instabilidade por contratos temporarios
    if q3 == "CONTRATO_TEMPORARIO_SAZONAL" and q1 in ("MEDIA", "ALTA"):
        riscos.append(RiscoInferido(
            titulo="Risco de instabilidade por dependencia de contratos temporarios",
            categoria=CategoriaRisco.OPERACIONAL.value,
            bloco_origem="BLOCO_1",
            perguntas_acionadoras=["Q1", "Q3"],
            regra_id="B1_R5_CONTRATO_TEMPORARIO",
            grau_confianca=GrauConfianca.MEDIO.value,
            justificativa="Dependencia relevante de contratos temporarios ou sazonais, gerando instabilidade na execucao."
        ))

    # RISCO 6 - Sistemico (combinacao critica)
    if q1 == "ALTA" and q2 == "INFORMAL" and q4 == "CRITICA_PARA_RESULTADO_FINAL":
        riscos.append(RiscoInferido(
            titulo="Risco sistemico de falha em cadeia por dependencia critica de terceiros",
            categoria=CategoriaRisco.OPERACIONAL.value,
            bloco_origem="BLOCO_1",
            perguntas_acionadoras=["Q1", "Q2", "Q4"],
            regra_id="B1_R6_SISTEMICO",
            grau_confianca=GrauConfianca.ALTO.value,
            justificativa="Combinacao critica: dependencia alta, sem formalizacao, para resultado final. Risco de falha em cadeia."
        ))

    return riscos


# =============================================================================
# BLOCO 2 - RECURSOS HUMANOS E CAPACIDADES
# =============================================================================

def inferir_riscos_bloco_2(respostas: Dict[str, str]) -> List[RiscoInferido]:
    """
    Infere riscos do Bloco 2 - Recursos Humanos

    Perguntas:
    Q1 - dependencia_pessoas_chave: NAO_EXISTE | BAIXA | MEDIA | ALTA
    Q2 - tempo_substituicao: CURTO | MEDIO | LONGO
    Q3 - risco_vacancia: NAO | MODERADO | ELEVADO
    Q4 - nivel_capacitacao: ADEQUADO | PARCIAL | INSUFICIENTE
    """
    riscos = []
    q1 = respostas.get("Q1", "")
    q2 = respostas.get("Q2", "")
    q3 = respostas.get("Q3", "")
    q4 = respostas.get("Q4", "")

    # RISCO 1 - Continuidade operacional
    if q1 in ("MEDIA", "ALTA") and q3 in ("MODERADO", "ELEVADO"):
        riscos.append(RiscoInferido(
            titulo="Risco de descontinuidade por dependencia de pessoas-chave",
            categoria=CategoriaRisco.OPERACIONAL.value,
            bloco_origem="BLOCO_2",
            perguntas_acionadoras=["Q1", "Q3"],
            regra_id="B2_R1_CONTINUIDADE",
            grau_confianca=GrauConfianca.ALTO.value,
            justificativa="Dependencia de pessoas-chave com risco de vacancia/afastamento, ameacando a continuidade operacional."
        ))

    # RISCO 2 - Perda de memoria institucional
    if q1 == "ALTA" and q2 == "LONGO":
        riscos.append(RiscoInferido(
            titulo="Risco de perda de memoria institucional",
            categoria=CategoriaRisco.OPERACIONAL.value,
            bloco_origem="BLOCO_2",
            perguntas_acionadoras=["Q1", "Q2"],
            regra_id="B2_R2_MEMORIA_INSTITUCIONAL",
            grau_confianca=GrauConfianca.ALTO.value,
            justificativa="Alta dependencia de pessoas-chave com longo tempo de substituicao, indicando risco de perda de conhecimento critico."
        ))

    # RISCO 3 - Falha por capacitacao insuficiente
    if q4 == "INSUFICIENTE":
        riscos.append(RiscoInferido(
            titulo="Risco de falha na execucao por insuficiencia de capacitacao",
            categoria=CategoriaRisco.OPERACIONAL.value,
            bloco_origem="BLOCO_2",
            perguntas_acionadoras=["Q4"],
            regra_id="B2_R3_CAPACITACAO",
            grau_confianca=GrauConfianca.MEDIO.value,
            justificativa="Nivel de capacitacao insuficiente para a complexidade do objeto, aumentando risco de falhas."
        ))

    # RISCO 4 - Atraso por curva de aprendizado
    if q4 == "PARCIAL" and q2 in ("MEDIO", "LONGO"):
        riscos.append(RiscoInferido(
            titulo="Risco de atraso por curva de aprendizado da equipe",
            categoria=CategoriaRisco.OPERACIONAL.value,
            bloco_origem="BLOCO_2",
            perguntas_acionadoras=["Q2", "Q4"],
            regra_id="B2_R4_CURVA_APRENDIZADO",
            grau_confianca=GrauConfianca.MEDIO.value,
            justificativa="Capacitacao parcial combinada com tempo de substituicao significativo, indicando risco de atraso."
        ))

    # RISCO 5 - Sobrecarga operacional
    if q1 in ("MEDIA", "ALTA") and q3 == "MODERADO" and q4 == "PARCIAL":
        riscos.append(RiscoInferido(
            titulo="Risco de sobrecarga operacional da equipe",
            categoria=CategoriaRisco.OPERACIONAL.value,
            bloco_origem="BLOCO_2",
            perguntas_acionadoras=["Q1", "Q3", "Q4"],
            regra_id="B2_R5_SOBRECARGA",
            grau_confianca=GrauConfianca.MEDIO.value,
            justificativa="Combinacao de dependencia de pessoas-chave, risco de vacancia e capacitacao parcial, gerando sobrecarga."
        ))

    # RISCO 6 - Inviabilidade operacional (critico)
    if q1 == "ALTA" and q2 == "LONGO" and q3 == "ELEVADO":
        riscos.append(RiscoInferido(
            titulo="Risco critico de inviabilidade operacional por dependencia de pessoas-chave",
            categoria=CategoriaRisco.OPERACIONAL.value,
            bloco_origem="BLOCO_2",
            perguntas_acionadoras=["Q1", "Q2", "Q3"],
            regra_id="B2_R6_INVIABILIDADE",
            grau_confianca=GrauConfianca.ALTO.value,
            justificativa="Cenario critico: alta dependencia, longo tempo de substituicao e risco elevado de vacancia."
        ))

    return riscos


# =============================================================================
# BLOCO 3 - TECNOLOGIA E SISTEMAS
# =============================================================================

def inferir_riscos_bloco_3(respostas: Dict[str, str]) -> List[RiscoInferido]:
    """
    Infere riscos do Bloco 3 - Tecnologia

    Perguntas:
    Q1 - dependencia_sistemas: NAO_DEPENDE | DEPENDE_PARCIALMENTE | DEPENDE_CRITICAMENTE
    Q2 - tipo_sistema: INTERNO | EXTERNO | MISTO
    Q3 - maturidade_sistema: ESTAVEL_CONSOLIDADO | EM_IMPLANTACAO_OU_EVOLUCAO | INSTAVEL_OU_CRITICO
    Q4 - contingencia_manual: SIM_PLENA | PARCIAL | NAO_EXISTE
    Q5 - historico_falhas: NAO | OCASIONAL | RECORRENTE
    """
    riscos = []
    q1 = respostas.get("Q1", "")
    q2 = respostas.get("Q2", "")
    q3 = respostas.get("Q3", "")
    q4 = respostas.get("Q4", "")
    q5 = respostas.get("Q5", "")

    # Se nao depende de sistemas, nenhum risco
    if q1 == "NAO_DEPENDE":
        return riscos

    # RISCO 1 - Indisponibilidade operacional
    if q1 == "DEPENDE_CRITICAMENTE" and q4 == "NAO_EXISTE":
        riscos.append(RiscoInferido(
            titulo="Risco de indisponibilidade operacional por falha de sistemas",
            categoria=CategoriaRisco.TECNOLOGICO.value,
            bloco_origem="BLOCO_3",
            perguntas_acionadoras=["Q1", "Q4"],
            regra_id="B3_R1_INDISPONIBILIDADE",
            grau_confianca=GrauConfianca.ALTO.value,
            justificativa="Dependencia critica de sistemas sem contingencia manual, indicando risco de paralisacao total."
        ))

    # RISCO 2 - Falha sistemica por instabilidade
    if q3 == "INSTAVEL_OU_CRITICO" and q1 in ("DEPENDE_PARCIALMENTE", "DEPENDE_CRITICAMENTE"):
        riscos.append(RiscoInferido(
            titulo="Risco de falha sistemica por instabilidade tecnologica",
            categoria=CategoriaRisco.TECNOLOGICO.value,
            bloco_origem="BLOCO_3",
            perguntas_acionadoras=["Q1", "Q3"],
            regra_id="B3_R2_INSTABILIDADE",
            grau_confianca=GrauConfianca.ALTO.value,
            justificativa="Sistemas em situacao instavel ou critica com dependencia operacional significativa."
        ))

    # RISCO 3 - Dependencia de sistemas externos
    if q2 in ("EXTERNO", "MISTO") and q1 == "DEPENDE_CRITICAMENTE":
        riscos.append(RiscoInferido(
            titulo="Risco de dependencia critica de sistemas externos",
            categoria=CategoriaRisco.TECNOLOGICO.value,
            bloco_origem="BLOCO_3",
            perguntas_acionadoras=["Q1", "Q2"],
            regra_id="B3_R3_SISTEMAS_EXTERNOS",
            grau_confianca=GrauConfianca.MEDIO.value,
            justificativa="Dependencia critica de sistemas fora do controle direto da organizacao."
        ))

    # RISCO 4 - Atraso por falhas recorrentes
    if q5 == "RECORRENTE":
        riscos.append(RiscoInferido(
            titulo="Risco de atraso operacional por falhas recorrentes de sistemas",
            categoria=CategoriaRisco.OPERACIONAL.value,
            bloco_origem="BLOCO_3",
            perguntas_acionadoras=["Q5"],
            regra_id="B3_R4_FALHAS_RECORRENTES",
            grau_confianca=GrauConfianca.ALTO.value,
            justificativa="Historico recorrente de falhas nos sistemas, indicando problema estrutural nao resolvido."
        ))

    # RISCO 5 - Mitigavel por contingencia parcial
    if q1 == "DEPENDE_CRITICAMENTE" and q4 == "PARCIAL":
        riscos.append(RiscoInferido(
            titulo="Risco tecnologico mitigavel por contingencia parcial",
            categoria=CategoriaRisco.TECNOLOGICO.value,
            bloco_origem="BLOCO_3",
            perguntas_acionadoras=["Q1", "Q4"],
            regra_id="B3_R5_CONTINGENCIA_PARCIAL",
            grau_confianca=GrauConfianca.MEDIO.value,
            justificativa="Dependencia critica com contingencia parcial - risco existe mas com possibilidade de mitigacao."
        ))

    # RISCO 6 - Paralisacao total (critico)
    if q1 == "DEPENDE_CRITICAMENTE" and q3 == "INSTAVEL_OU_CRITICO" and q4 == "NAO_EXISTE":
        riscos.append(RiscoInferido(
            titulo="Risco critico de paralisacao total por falha tecnologica",
            categoria=CategoriaRisco.TECNOLOGICO.value,
            bloco_origem="BLOCO_3",
            perguntas_acionadoras=["Q1", "Q3", "Q4"],
            regra_id="B3_R6_PARALISACAO_TOTAL",
            grau_confianca=GrauConfianca.ALTO.value,
            justificativa="Cenario critico: dependencia critica de sistemas instaveis sem contingencia manual."
        ))

    return riscos


# =============================================================================
# BLOCO 4 - PRAZOS, SLAs E PRESSOES LEGAIS
# =============================================================================

def inferir_riscos_bloco_4(respostas: Dict[str, str]) -> List[RiscoInferido]:
    """
    Infere riscos do Bloco 4 - Prazos e Pressoes Legais

    Perguntas:
    Q1 - prazos_normativos: NAO_EXISTEM | EXISTEM_COM_MARGEM | EXISTEM_CRITICOS
    Q2 - origem_prazo: LEGAL | REGULAMENTAR | CONTRATUAL | ADMINISTRATIVA
    Q3 - consequencia_descumprimento: ADMINISTRATIVA | FINANCEIRA | RESPONSABILIZACAO_AGENTES | JUDICIALIZACAO | MULTIPLA
    Q4 - margem_renegociacao: SIM_CLARA | LIMITADA | INEXISTENTE
    Q5 - pressao_externa: NAO | ORGAOS_CONTROLE | MIDIA_SOCIEDADE | PODER_JUDICIARIO
    """
    riscos = []
    q1 = respostas.get("Q1", "")
    q2 = respostas.get("Q2", "")
    q3 = respostas.get("Q3", "")
    q4 = respostas.get("Q4", "")
    q5 = respostas.get("Q5", "")

    # Se nao existem prazos, nenhum risco
    if q1 == "NAO_EXISTEM":
        return riscos

    # RISCO 1 - Legal por prazo normativo critico
    if q1 == "EXISTEM_CRITICOS" and q2 in ("LEGAL", "REGULAMENTAR"):
        riscos.append(RiscoInferido(
            titulo="Risco legal por descumprimento de prazo normativo",
            categoria=CategoriaRisco.LEGAL.value,
            bloco_origem="BLOCO_4",
            perguntas_acionadoras=["Q1", "Q2"],
            regra_id="B4_R1_PRAZO_NORMATIVO",
            grau_confianca=GrauConfianca.ALTO.value,
            justificativa="Prazo normativo critico de origem legal/regulamentar, com risco de descumprimento."
        ))

    # RISCO 2 - Responsabilizacao de agentes
    if q3 in ("RESPONSABILIZACAO_AGENTES", "MULTIPLA"):
        riscos.append(RiscoInferido(
            titulo="Risco de responsabilizacao de agentes publicos por descumprimento",
            categoria=CategoriaRisco.LEGAL.value,
            bloco_origem="BLOCO_4",
            perguntas_acionadoras=["Q3"],
            regra_id="B4_R2_RESPONSABILIZACAO",
            grau_confianca=GrauConfianca.ALTO.value,
            justificativa="Descumprimento pode gerar responsabilizacao direta dos agentes envolvidos."
        ))

    # RISCO 3 - Judicializacao
    if q3 in ("JUDICIALIZACAO", "MULTIPLA"):
        riscos.append(RiscoInferido(
            titulo="Risco de judicializacao decorrente de descumprimento de prazo",
            categoria=CategoriaRisco.LEGAL.value,
            bloco_origem="BLOCO_4",
            perguntas_acionadoras=["Q3"],
            regra_id="B4_R3_JUDICIALIZACAO",
            grau_confianca=GrauConfianca.ALTO.value,
            justificativa="Descumprimento pode resultar em acoes judiciais contra a organizacao."
        ))

    # RISCO 4 - Reputacional por pressao externa
    if q5 in ("MIDIA_SOCIEDADE", "ORGAOS_CONTROLE") and q1 != "NAO_EXISTEM":
        riscos.append(RiscoInferido(
            titulo="Risco reputacional associado a descumprimento de prazos",
            categoria=CategoriaRisco.REPUTACIONAL.value,
            bloco_origem="BLOCO_4",
            perguntas_acionadoras=["Q1", "Q5"],
            regra_id="B4_R4_REPUTACIONAL",
            grau_confianca=GrauConfianca.MEDIO.value,
            justificativa="Pressao externa sobre prazos pode gerar danos reputacionais em caso de descumprimento."
        ))

    # RISCO 5 - Elevado sem margem
    if q1 in ("EXISTEM_COM_MARGEM", "EXISTEM_CRITICOS") and q4 == "INEXISTENTE":
        riscos.append(RiscoInferido(
            titulo="Risco elevado por ausencia de margem de renegociacao de prazos",
            categoria=CategoriaRisco.LEGAL.value,
            bloco_origem="BLOCO_4",
            perguntas_acionadoras=["Q1", "Q4"],
            regra_id="B4_R5_SEM_MARGEM",
            grau_confianca=GrauConfianca.ALTO.value,
            justificativa="Prazos existentes sem possibilidade de renegociacao, aumentando exposicao ao risco."
        ))

    # RISCO 6 - Moderado (administravel)
    if q1 == "EXISTEM_COM_MARGEM" and q4 == "SIM_CLARA":
        riscos.append(RiscoInferido(
            titulo="Risco moderado associado a prazos administraveis",
            categoria=CategoriaRisco.OPERACIONAL.value,
            bloco_origem="BLOCO_4",
            perguntas_acionadoras=["Q1", "Q4"],
            regra_id="B4_R6_ADMINISTRAVEL",
            grau_confianca=GrauConfianca.MEDIO.value,
            justificativa="Prazos com margem e possibilidade de renegociacao - risco administravel."
        ))

    return riscos


# =============================================================================
# BLOCO 5 - GOVERNANCA E TOMADA DE DECISAO
# =============================================================================

def inferir_riscos_bloco_5(respostas: Dict[str, str]) -> List[RiscoInferido]:
    """
    Infere riscos do Bloco 5 - Governanca

    Perguntas:
    Q1 - atribuicao_decisoria: CLARA_E_FORMAL | CLARA_MAS_INFORMAL | DIFUSA | INEXISTENTE
    Q2 - ato_governanca: EXISTE | PARCIAL | NAO_EXISTE
    Q3 - dependencia_instancias: NAO | UMA_INSTANCIA | MULTIPLAS_INSTANCIAS
    Q4 - previsibilidade_decisao: PREVISIVEL | PARCIALMENTE_PREVISIVEL | IMPREVISIVEL
    Q5 - conflito_competencia: NAO | POSSIVEL | PROVAVEL
    """
    riscos = []
    q1 = respostas.get("Q1", "")
    q2 = respostas.get("Q2", "")
    q3 = respostas.get("Q3", "")
    q4 = respostas.get("Q4", "")
    q5 = respostas.get("Q5", "")

    # Governanca solida = sem risco relevante
    if q1 == "CLARA_E_FORMAL" and q2 == "EXISTE" and q4 == "PREVISIVEL":
        return riscos  # Cenario ideal, nenhum risco

    # RISCO 1 - Atraso decisorio
    if q1 in ("DIFUSA", "INEXISTENTE") or q4 == "IMPREVISIVEL":
        riscos.append(RiscoInferido(
            titulo="Risco de atraso decisorio por fragilidade de governanca",
            categoria=CategoriaRisco.OPERACIONAL.value,
            bloco_origem="BLOCO_5",
            perguntas_acionadoras=["Q1", "Q4"],
            regra_id="B5_R1_ATRASO_DECISORIO",
            grau_confianca=GrauConfianca.ALTO.value,
            justificativa="Atribuicao decisoria difusa ou fluxo imprevisivel, gerando risco de atrasos."
        ))

    # RISCO 2 - Paralisia institucional
    if q3 == "MULTIPLAS_INSTANCIAS" and q4 != "PREVISIVEL":
        riscos.append(RiscoInferido(
            titulo="Risco de paralisia institucional por dependencia decisoria externa",
            categoria=CategoriaRisco.OPERACIONAL.value,
            bloco_origem="BLOCO_5",
            perguntas_acionadoras=["Q3", "Q4"],
            regra_id="B5_R2_PARALISIA",
            grau_confianca=GrauConfianca.ALTO.value,
            justificativa="Dependencia de multiplas instancias externas com fluxo nao previsivel."
        ))

    # RISCO 3 - Conflito de competencia
    if q5 in ("POSSIVEL", "PROVAVEL"):
        riscos.append(RiscoInferido(
            titulo="Risco de conflito de competencia na tomada de decisao",
            categoria=CategoriaRisco.LEGAL.value,
            bloco_origem="BLOCO_5",
            perguntas_acionadoras=["Q5"],
            regra_id="B5_R3_CONFLITO_COMPETENCIA",
            grau_confianca=GrauConfianca.MEDIO.value,
            justificativa="Possibilidade de conflito de competencia, gerando impasses e questionamentos."
        ))

    # RISCO 4 - Decisoes informais sem respaldo
    if q1 == "CLARA_MAS_INFORMAL" and q2 in ("PARCIAL", "NAO_EXISTE"):
        riscos.append(RiscoInferido(
            titulo="Risco de decisoes informais sem respaldo institucional",
            categoria=CategoriaRisco.LEGAL.value,
            bloco_origem="BLOCO_5",
            perguntas_acionadoras=["Q1", "Q2"],
            regra_id="B5_R4_DECISOES_INFORMAIS",
            grau_confianca=GrauConfianca.ALTO.value,
            justificativa="Decisoes claras mas sem ato formal de governanca, expondo agentes a questionamentos."
        ))

    # RISCO 5 - Reputacional por falha de coordenacao
    if q1 == "DIFUSA" and q3 != "NAO":
        riscos.append(RiscoInferido(
            titulo="Risco reputacional por falhas de coordenacao decisoria",
            categoria=CategoriaRisco.REPUTACIONAL.value,
            bloco_origem="BLOCO_5",
            perguntas_acionadoras=["Q1", "Q3"],
            regra_id="B5_R5_COORDENACAO",
            grau_confianca=GrauConfianca.MEDIO.value,
            justificativa="Atribuicao difusa com dependencia externa pode gerar falhas de coordenacao visiveis."
        ))

    return riscos


# =============================================================================
# BLOCO 6 - IMPACTO DESIGUAL E SENSIBILIDADE SOCIAL
# =============================================================================

def inferir_riscos_bloco_6(respostas: Dict[str, Any]) -> List[RiscoInferido]:
    """
    Infere riscos do Bloco 6 - Impacto Desigual

    Perguntas:
    Q1 - impacto_diferenciado: NAO | POSSIVEL | PROVAVEL
    Q2 - grupos_afetados: [lista multipla]
    Q3 - natureza_impacto: [lista multipla]
    Q4 - escala_impacto: PONTUAL | RECORRENTE | SISTEMICO
    Q5 - medidas_mitigacao: NAO_PREVISTAS | PREVISTAS_PARCIALMENTE | PREVISTAS_E_FORMALIZADAS
    """
    riscos = []
    q1 = respostas.get("Q1", "")
    q2 = respostas.get("Q2", [])  # Lista
    q3 = respostas.get("Q3", [])  # Lista
    q4 = respostas.get("Q4", "")
    q5 = respostas.get("Q5", "")

    # Se nao ha impacto diferenciado, nenhum risco
    if q1 == "NAO":
        return riscos

    # Garantir que q2 e q3 sejam listas
    if isinstance(q2, str):
        q2 = [q2] if q2 else []
    if isinstance(q3, str):
        q3 = [q3] if q3 else []

    # RISCO 1 - Impacto desigual nao mitigado
    if q1 == "PROVAVEL" and q5 in ("NAO_PREVISTAS", "PREVISTAS_PARCIALMENTE"):
        riscos.append(RiscoInferido(
            titulo="Risco de impacto desigual nao mitigado",
            categoria=CategoriaRisco.IMPACTO_DESIGUAL.value,
            bloco_origem="BLOCO_6",
            perguntas_acionadoras=["Q1", "Q5"],
            regra_id="B6_R1_NAO_MITIGADO",
            grau_confianca=GrauConfianca.ALTO.value,
            justificativa="Impacto diferenciado provavel sem medidas mitigadoras adequadas."
        ))

    # RISCO 2 - Reputacional por efeito sobre grupos vulneraveis
    grupos_vulneraveis = {"PESSOAS_NEGRAS", "MULHERES", "PESSOAS_COM_DEFICIENCIA", "POPULACOES_VULNERAVEIS"}
    if q1 != "NAO" and set(q2) & grupos_vulneraveis and q4 in ("RECORRENTE", "SISTEMICO"):
        riscos.append(RiscoInferido(
            titulo="Risco reputacional por efeitos desiguais sobre grupos vulneraveis",
            categoria=CategoriaRisco.REPUTACIONAL.value,
            bloco_origem="BLOCO_6",
            perguntas_acionadoras=["Q2", "Q4"],
            regra_id="B6_R2_GRUPOS_VULNERAVEIS",
            grau_confianca=GrauConfianca.ALTO.value,
            justificativa="Impacto recorrente/sistemico sobre grupos vulneraveis gera risco reputacional significativo."
        ))

    # RISCO 3 - Questionamento institucional por tratamento desigual
    if q1 == "PROVAVEL" and ("TRATAMENTO_DESIGUAL" in q3 or "BARREIRA_TECNOLOGICA" in q3) and q5 == "NAO_PREVISTAS":
        riscos.append(RiscoInferido(
            titulo="Risco de questionamento institucional por tratamento desigual",
            categoria=CategoriaRisco.LEGAL.value,
            bloco_origem="BLOCO_6",
            perguntas_acionadoras=["Q1", "Q3", "Q5"],
            regra_id="B6_R3_QUESTIONAMENTO",
            grau_confianca=GrauConfianca.ALTO.value,
            justificativa="Tratamento desigual ou barreira tecnologica provavel sem mitigacao, expondo a questionamentos."
        ))

    # RISCO 4 - Operacional ampliado por exclusao
    if "BARREIRA_TECNOLOGICA" in q3 and "POPULACOES_VULNERAVEIS" in q2:
        riscos.append(RiscoInferido(
            titulo="Risco operacional ampliado por barreiras de acesso",
            categoria=CategoriaRisco.OPERACIONAL.value,
            bloco_origem="BLOCO_6",
            perguntas_acionadoras=["Q2", "Q3"],
            regra_id="B6_R4_BARREIRA_ACESSO",
            grau_confianca=GrauConfianca.MEDIO.value,
            justificativa="Barreira tecnologica afetando populacoes vulneraveis pode comprometer resultados operacionais."
        ))

    # RISCO 5 - Residual (impacto mitigado)
    if q1 != "NAO" and q5 == "PREVISTAS_E_FORMALIZADAS":
        riscos.append(RiscoInferido(
            titulo="Impacto desigual identificado e mitigado",
            categoria=CategoriaRisco.IMPACTO_DESIGUAL.value,
            bloco_origem="BLOCO_6",
            perguntas_acionadoras=["Q1", "Q5"],
            regra_id="B6_R5_MITIGADO",
            grau_confianca=GrauConfianca.BAIXO.value,
            justificativa="Impacto desigual identificado com medidas mitigadoras formalizadas - risco residual aceitavel."
        ))

    return riscos


# =============================================================================
# FUNCAO PRINCIPAL DE INFERENCIA
# =============================================================================

def inferir_todos_riscos(respostas_blocos: Dict[str, Dict[str, Any]]) -> List[RiscoInferido]:
    """
    Executa inferencia de riscos em todos os blocos.

    Args:
        respostas_blocos: Dict com chaves BLOCO_1 a BLOCO_6, cada uma com respostas Q1-Qn

    Returns:
        Lista de RiscoInferido
    """
    todos_riscos = []

    # Bloco 1
    if "BLOCO_1" in respostas_blocos:
        todos_riscos.extend(inferir_riscos_bloco_1(respostas_blocos["BLOCO_1"]))

    # Bloco 2
    if "BLOCO_2" in respostas_blocos:
        todos_riscos.extend(inferir_riscos_bloco_2(respostas_blocos["BLOCO_2"]))

    # Bloco 3
    if "BLOCO_3" in respostas_blocos:
        todos_riscos.extend(inferir_riscos_bloco_3(respostas_blocos["BLOCO_3"]))

    # Bloco 4
    if "BLOCO_4" in respostas_blocos:
        todos_riscos.extend(inferir_riscos_bloco_4(respostas_blocos["BLOCO_4"]))

    # Bloco 5
    if "BLOCO_5" in respostas_blocos:
        todos_riscos.extend(inferir_riscos_bloco_5(respostas_blocos["BLOCO_5"]))

    # Bloco 6
    if "BLOCO_6" in respostas_blocos:
        todos_riscos.extend(inferir_riscos_bloco_6(respostas_blocos["BLOCO_6"]))

    return todos_riscos


def riscos_para_dict(riscos: List[RiscoInferido]) -> List[Dict[str, Any]]:
    """Converte lista de RiscoInferido para lista de dicts (para JSON)"""
    return [
        {
            "titulo": r.titulo,
            "categoria": r.categoria,
            "bloco_origem": r.bloco_origem,
            "perguntas_acionadoras": r.perguntas_acionadoras,
            "regra_id": r.regra_id,
            "grau_confianca": r.grau_confianca,
            "justificativa": r.justificativa,
        }
        for r in riscos
    ]
