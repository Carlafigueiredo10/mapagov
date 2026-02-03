"""
Schema dos 6 Blocos de Identificacao Orientada de Riscos

Define:
- Perguntas estruturadas de cada bloco
- Valores possiveis para cada resposta
- Metadados para UI e inferencia

Usado por:
- Frontend (renderizar questionario)
- Backend (validar respostas)
- regras_inferencia.py (aplicar regras)
"""
from enum import Enum
from typing import List, Dict, Any


# =============================================================================
# BLOCO 1 - DEPENDENCIA DE TERCEIROS
# =============================================================================

class B1_DependenciaTerceiros(str, Enum):
    """Q1 - Grau de dependencia de terceiros"""
    NAO_EXISTE = "NAO_EXISTE"
    BAIXA = "BAIXA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"


class B1_Formalizacao(str, Enum):
    """Q2 - Grau de formalizacao da relacao"""
    FORMAL = "FORMAL"          # Contrato, ACT, convenio vigente
    PARCIAL = "PARCIAL"        # Minuta, termo em negociacao
    INFORMAL = "INFORMAL"      # Sem instrumento valido


class B1_NaturezaContratacao(str, Enum):
    """Q3 - Natureza da contratacao"""
    CONTRATO_VIGENTE = "CONTRATO_VIGENTE"
    CONTRATACAO_FUTURA = "CONTRATACAO_FUTURA"
    LICITACAO_NAO_REALIZADA = "LICITACAO_NAO_REALIZADA"
    CONTRATO_TEMPORARIO_SAZONAL = "CONTRATO_TEMPORARIO_SAZONAL"
    NAO_SE_APLICA = "NAO_SE_APLICA"


class B1_CriticidadeEntrega(str, Enum):
    """Q4 - Criticidade da entrega do terceiro"""
    NAO_CRITICA = "NAO_CRITICA"
    IMPORTANTE = "IMPORTANTE"
    CRITICA_PARA_RESULTADO_FINAL = "CRITICA_PARA_RESULTADO_FINAL"


# =============================================================================
# BLOCO 2 - RECURSOS HUMANOS E CAPACIDADES
# =============================================================================

class B2_DependenciaPessoasChave(str, Enum):
    """Q1 - Dependencia de pessoas-chave"""
    NAO_EXISTE = "NAO_EXISTE"
    BAIXA = "BAIXA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"


class B2_TempoSubstituicao(str, Enum):
    """Q2 - Tempo e custo de substituicao"""
    CURTO = "CURTO"    # Ate 30 dias, baixo custo
    MEDIO = "MEDIO"    # 30 a 90 dias, custo moderado
    LONGO = "LONGO"    # Mais de 90 dias, alto custo


class B2_RiscoVacancia(str, Enum):
    """Q3 - Risco de vacancia, afastamento ou rotatividade"""
    NAO = "NAO"
    MODERADO = "MODERADO"
    ELEVADO = "ELEVADO"


class B2_NivelCapacitacao(str, Enum):
    """Q4 - Nivel de capacitacao da equipe"""
    ADEQUADO = "ADEQUADO"
    PARCIAL = "PARCIAL"
    INSUFICIENTE = "INSUFICIENTE"


# =============================================================================
# BLOCO 3 - TECNOLOGIA E SISTEMAS
# =============================================================================

class B3_DependenciaSistemas(str, Enum):
    """Q1 - Grau de dependencia de sistemas"""
    NAO_DEPENDE = "NAO_DEPENDE"
    DEPENDE_PARCIALMENTE = "DEPENDE_PARCIALMENTE"
    DEPENDE_CRITICAMENTE = "DEPENDE_CRITICAMENTE"


class B3_TipoSistema(str, Enum):
    """Q2 - Natureza dos sistemas envolvidos"""
    INTERNO = "INTERNO"
    EXTERNO = "EXTERNO"
    MISTO = "MISTO"


class B3_MaturidadeSistema(str, Enum):
    """Q3 - Estagio de maturidade do sistema"""
    ESTAVEL_CONSOLIDADO = "ESTAVEL_CONSOLIDADO"
    EM_IMPLANTACAO_OU_EVOLUCAO = "EM_IMPLANTACAO_OU_EVOLUCAO"
    INSTAVEL_OU_CRITICO = "INSTAVEL_OU_CRITICO"


class B3_ContingenciaManual(str, Enum):
    """Q4 - Continuidade manual ou contingencia"""
    SIM_PLENA = "SIM_PLENA"
    PARCIAL = "PARCIAL"
    NAO_EXISTE = "NAO_EXISTE"


class B3_HistoricoFalhas(str, Enum):
    """Q5 - Historico recente de falhas"""
    NAO = "NAO"
    OCASIONAL = "OCASIONAL"
    RECORRENTE = "RECORRENTE"


# =============================================================================
# BLOCO 4 - PRAZOS, SLAs E PRESSOES LEGAIS
# =============================================================================

class B4_PrazosNormativos(str, Enum):
    """Q1 - Existencia de prazos legais ou normativos"""
    NAO_EXISTEM = "NAO_EXISTEM"
    EXISTEM_COM_MARGEM = "EXISTEM_COM_MARGEM"
    EXISTEM_CRITICOS = "EXISTEM_CRITICOS"


class B4_OrigemPrazo(str, Enum):
    """Q2 - Origem da obrigacao"""
    LEGAL = "LEGAL"              # Lei, decreto, MP
    REGULAMENTAR = "REGULAMENTAR"  # Portaria, instrucao
    CONTRATUAL = "CONTRATUAL"    # ACT, contrato, convenio
    ADMINISTRATIVA = "ADMINISTRATIVA"  # Meta interna, acordo informal


class B4_ConsequenciaDescumprimento(str, Enum):
    """Q3 - Consequencia do descumprimento"""
    ADMINISTRATIVA = "ADMINISTRATIVA"
    FINANCEIRA = "FINANCEIRA"
    RESPONSABILIZACAO_AGENTES = "RESPONSABILIZACAO_AGENTES"
    JUDICIALIZACAO = "JUDICIALIZACAO"
    MULTIPLA = "MULTIPLA"


class B4_MargemRenegociacao(str, Enum):
    """Q4 - Margem de renegociacao ou flexibilizacao"""
    SIM_CLARA = "SIM_CLARA"
    LIMITADA = "LIMITADA"
    INEXISTENTE = "INEXISTENTE"


class B4_PressaoExterna(str, Enum):
    """Q5 - Pressao externa associada ao prazo"""
    NAO = "NAO"
    ORGAOS_CONTROLE = "ORGAOS_CONTROLE"
    MIDIA_SOCIEDADE = "MIDIA_SOCIEDADE"
    PODER_JUDICIARIO = "PODER_JUDICIARIO"


# =============================================================================
# BLOCO 5 - GOVERNANCA E TOMADA DE DECISAO
# =============================================================================

class B5_AtribuicaoDecisoria(str, Enum):
    """Q1 - Clareza de atribuicao decisoria"""
    CLARA_E_FORMAL = "CLARA_E_FORMAL"
    CLARA_MAS_INFORMAL = "CLARA_MAS_INFORMAL"
    DIFUSA = "DIFUSA"
    INEXISTENTE = "INEXISTENTE"


class B5_AtoGovernanca(str, Enum):
    """Q2 - Existencia de ato formal de governanca"""
    EXISTE = "EXISTE"        # Portaria, regimento, resolucao
    PARCIAL = "PARCIAL"      # Minuta, pratica recorrente
    NAO_EXISTE = "NAO_EXISTE"


class B5_DependenciaInstancias(str, Enum):
    """Q3 - Dependencia de instancias externas para decisao"""
    NAO = "NAO"
    UMA_INSTANCIA = "UMA_INSTANCIA"
    MULTIPLAS_INSTANCIAS = "MULTIPLAS_INSTANCIAS"


class B5_PrevisibilidadeDecisao(str, Enum):
    """Q4 - Previsibilidade do fluxo decisorio"""
    PREVISIVEL = "PREVISIVEL"
    PARCIALMENTE_PREVISIVEL = "PARCIALMENTE_PREVISIVEL"
    IMPREVISIVEL = "IMPREVISIVEL"


class B5_ConflitoCompetencia(str, Enum):
    """Q5 - Risco de conflito de competencia"""
    NAO = "NAO"
    POSSIVEL = "POSSIVEL"
    PROVAVEL = "PROVAVEL"


# =============================================================================
# BLOCO 6 - IMPACTO DESIGUAL E SENSIBILIDADE SOCIAL
# =============================================================================

class B6_ImpactoDiferenciado(str, Enum):
    """Q1 - Existencia de impacto diferenciado"""
    NAO = "NAO"
    POSSIVEL = "POSSIVEL"
    PROVAVEL = "PROVAVEL"


class B6_GruposAfetados(str, Enum):
    """Q2 - Grupos potencialmente afetados (multipla escolha)"""
    MULHERES = "MULHERES"
    PESSOAS_NEGRAS = "PESSOAS_NEGRAS"
    PESSOAS_COM_DEFICIENCIA = "PESSOAS_COM_DEFICIENCIA"
    POPULACOES_VULNERAVEIS = "POPULACOES_VULNERAVEIS"
    TERRITORIOS_ESPECIFICOS = "TERRITORIOS_ESPECIFICOS"
    OUTROS = "OUTROS"


class B6_NaturezaImpacto(str, Enum):
    """Q3 - Natureza do impacto (multipla escolha)"""
    ACESSO = "ACESSO"
    QUALIDADE_DO_SERVICO = "QUALIDADE_DO_SERVICO"
    TRATAMENTO_DESIGUAL = "TRATAMENTO_DESIGUAL"
    BARREIRA_TECNOLOGICA = "BARREIRA_TECNOLOGICA"
    EXPOSICAO_A_RISCO = "EXPOSICAO_A_RISCO"


class B6_EscalaImpacto(str, Enum):
    """Q4 - Escala do impacto"""
    PONTUAL = "PONTUAL"
    RECORRENTE = "RECORRENTE"
    SISTEMICO = "SISTEMICO"


class B6_MedidasMitigacao(str, Enum):
    """Q5 - Medidas mitigadoras previstas"""
    NAO_PREVISTAS = "NAO_PREVISTAS"
    PREVISTAS_PARCIALMENTE = "PREVISTAS_PARCIALMENTE"
    PREVISTAS_E_FORMALIZADAS = "PREVISTAS_E_FORMALIZADAS"


# =============================================================================
# SCHEMA COMPLETO DOS BLOCOS
# =============================================================================

BLOCOS_SCHEMA: Dict[str, Dict[str, Any]] = {
    "BLOCO_1": {
        "titulo": "Dependencia de Terceiros",
        "objetivo": "Identificar riscos operacionais, legais, contratuais e de continuidade derivados de terceiros",
        "perguntas": {
            "Q1": {
                "texto": "O projeto/processo depende de terceiros para sua execucao?",
                "tipo": "INTENSIDADE",
                "enum": "B1_DependenciaTerceiros",
                "obrigatoria": True,
            },
            "Q2": {
                "texto": "Qual o nivel de formalizacao da relacao com esses terceiros?",
                "tipo": "FORMALIZACAO",
                "enum": "B1_Formalizacao",
                "obrigatoria": True,
                "condicional": {"Q1": ["BAIXA", "MEDIA", "ALTA"]},
            },
            "Q3": {
                "texto": "Qual a natureza da contratacao?",
                "tipo": "VARIABILIDADE",
                "enum": "B1_NaturezaContratacao",
                "obrigatoria": True,
                "condicional": {"Q1": ["BAIXA", "MEDIA", "ALTA"]},
            },
            "Q4": {
                "texto": "A entrega do terceiro e critica para o resultado final?",
                "tipo": "CRITICIDADE",
                "enum": "B1_CriticidadeEntrega",
                "obrigatoria": True,
                "condicional": {"Q1": ["BAIXA", "MEDIA", "ALTA"]},
            },
        },
    },
    "BLOCO_2": {
        "titulo": "Recursos Humanos e Capacidades",
        "objetivo": "Identificar riscos de execucao, continuidade, sobrecarga e perda de memoria institucional",
        "perguntas": {
            "Q1": {
                "texto": "A execucao depende de pessoas-chave especificas?",
                "tipo": "INTENSIDADE",
                "enum": "B2_DependenciaPessoasChave",
                "obrigatoria": True,
            },
            "Q2": {
                "texto": "Qual o tempo e custo de substituicao dessas pessoas?",
                "tipo": "VARIABILIDADE",
                "enum": "B2_TempoSubstituicao",
                "obrigatoria": True,
                "condicional": {"Q1": ["BAIXA", "MEDIA", "ALTA"]},
            },
            "Q3": {
                "texto": "Ha risco de afastamento, rotatividade ou vacancia?",
                "tipo": "VARIABILIDADE",
                "enum": "B2_RiscoVacancia",
                "obrigatoria": True,
            },
            "Q4": {
                "texto": "O nivel de capacitacao atual da equipe e:",
                "tipo": "CAPACIDADE",
                "enum": "B2_NivelCapacitacao",
                "obrigatoria": True,
            },
        },
    },
    "BLOCO_3": {
        "titulo": "Tecnologia e Sistemas",
        "objetivo": "Identificar riscos de indisponibilidade, falha sistemica e dependencia tecnologica",
        "perguntas": {
            "Q1": {
                "texto": "O processo/projeto depende de sistemas de TI?",
                "tipo": "INTENSIDADE",
                "enum": "B3_DependenciaSistemas",
                "obrigatoria": True,
            },
            "Q2": {
                "texto": "Esses sistemas sao internos, externos ou mistos?",
                "tipo": "ORIGEM",
                "enum": "B3_TipoSistema",
                "obrigatoria": True,
                "condicional": {"Q1": ["DEPENDE_PARCIALMENTE", "DEPENDE_CRITICAMENTE"]},
            },
            "Q3": {
                "texto": "Qual o estagio de maturidade dos sistemas?",
                "tipo": "ESTABILIDADE",
                "enum": "B3_MaturidadeSistema",
                "obrigatoria": True,
                "condicional": {"Q1": ["DEPENDE_PARCIALMENTE", "DEPENDE_CRITICAMENTE"]},
            },
            "Q4": {
                "texto": "Em caso de indisponibilidade, o processo pode continuar manualmente?",
                "tipo": "CAPACIDADE",
                "enum": "B3_ContingenciaManual",
                "obrigatoria": True,
                "condicional": {"Q1": ["DEPENDE_PARCIALMENTE", "DEPENDE_CRITICAMENTE"]},
            },
            "Q5": {
                "texto": "Ha historico recente de falhas nesses sistemas?",
                "tipo": "EVIDENCIA",
                "enum": "B3_HistoricoFalhas",
                "obrigatoria": True,
                "condicional": {"Q1": ["DEPENDE_PARCIALMENTE", "DEPENDE_CRITICAMENTE"]},
            },
        },
    },
    "BLOCO_4": {
        "titulo": "Prazos, SLAs e Pressoes Legais",
        "objetivo": "Identificar riscos legais, reputacionais e de responsabilizacao",
        "perguntas": {
            "Q1": {
                "texto": "Existem prazos legais ou normativos associados?",
                "tipo": "EXISTENCIA",
                "enum": "B4_PrazosNormativos",
                "obrigatoria": True,
            },
            "Q2": {
                "texto": "Qual a origem da obrigacao de prazo?",
                "tipo": "FONTE",
                "enum": "B4_OrigemPrazo",
                "obrigatoria": True,
                "condicional": {"Q1": ["EXISTEM_COM_MARGEM", "EXISTEM_CRITICOS"]},
            },
            "Q3": {
                "texto": "O que acontece em caso de descumprimento?",
                "tipo": "SEVERIDADE",
                "enum": "B4_ConsequenciaDescumprimento",
                "obrigatoria": True,
                "condicional": {"Q1": ["EXISTEM_COM_MARGEM", "EXISTEM_CRITICOS"]},
            },
            "Q4": {
                "texto": "Existe margem para renegociacao do prazo?",
                "tipo": "VARIABILIDADE",
                "enum": "B4_MargemRenegociacao",
                "obrigatoria": True,
                "condicional": {"Q1": ["EXISTEM_COM_MARGEM", "EXISTEM_CRITICOS"]},
            },
            "Q5": {
                "texto": "Ha pressao externa associada ao prazo?",
                "tipo": "AMBIENTE",
                "enum": "B4_PressaoExterna",
                "obrigatoria": True,
                "condicional": {"Q1": ["EXISTEM_COM_MARGEM", "EXISTEM_CRITICOS"]},
            },
        },
    },
    "BLOCO_5": {
        "titulo": "Governanca e Tomada de Decisao",
        "objetivo": "Identificar riscos de coordenacao, autoridade e impasses decisorios",
        "perguntas": {
            "Q1": {
                "texto": "Existe ato formal que define a instancia decisoria?",
                "tipo": "FORMALIZACAO",
                "enum": "B5_AtribuicaoDecisoria",
                "obrigatoria": True,
            },
            "Q2": {
                "texto": "Existe ato formal de governanca (portaria, regimento)?",
                "tipo": "FORMALIZACAO",
                "enum": "B5_AtoGovernanca",
                "obrigatoria": True,
            },
            "Q3": {
                "texto": "Ha dependencia de instancias externas para decisao?",
                "tipo": "DEPENDENCIA",
                "enum": "B5_DependenciaInstancias",
                "obrigatoria": True,
            },
            "Q4": {
                "texto": "O fluxo decisorio e previsivel?",
                "tipo": "VARIABILIDADE",
                "enum": "B5_PrevisibilidadeDecisao",
                "obrigatoria": True,
            },
            "Q5": {
                "texto": "Ha risco de conflito de competencia?",
                "tipo": "AMBIGUIDADE",
                "enum": "B5_ConflitoCompetencia",
                "obrigatoria": True,
            },
        },
    },
    "BLOCO_6": {
        "titulo": "Impacto Desigual e Sensibilidade Social",
        "objetivo": "Identificar riscos de efeitos assimetricos sobre grupos vulneraveis",
        "perguntas": {
            "Q1": {
                "texto": "O projeto/processo pode afetar grupos especificos de forma diferenciada?",
                "tipo": "DETECCAO",
                "enum": "B6_ImpactoDiferenciado",
                "obrigatoria": True,
            },
            "Q2": {
                "texto": "Quais grupos podem ser afetados?",
                "tipo": "IDENTIFICACAO",
                "enum": "B6_GruposAfetados",
                "multipla_escolha": True,
                "obrigatoria": True,
                "condicional": {"Q1": ["POSSIVEL", "PROVAVEL"]},
            },
            "Q3": {
                "texto": "Qual a natureza do impacto?",
                "tipo": "QUALITATIVO",
                "enum": "B6_NaturezaImpacto",
                "multipla_escolha": True,
                "obrigatoria": True,
                "condicional": {"Q1": ["POSSIVEL", "PROVAVEL"]},
            },
            "Q4": {
                "texto": "Qual a escala do impacto?",
                "tipo": "ESCALA",
                "enum": "B6_EscalaImpacto",
                "obrigatoria": True,
                "condicional": {"Q1": ["POSSIVEL", "PROVAVEL"]},
            },
            "Q5": {
                "texto": "Existem medidas mitigadoras previstas?",
                "tipo": "CONTROLE",
                "enum": "B6_MedidasMitigacao",
                "obrigatoria": True,
                "condicional": {"Q1": ["POSSIVEL", "PROVAVEL"]},
            },
        },
    },
}


def get_enum_values(enum_name: str) -> List[str]:
    """Retorna os valores possiveis de um enum pelo nome"""
    enums_map = {
        # Bloco 1
        "B1_DependenciaTerceiros": B1_DependenciaTerceiros,
        "B1_Formalizacao": B1_Formalizacao,
        "B1_NaturezaContratacao": B1_NaturezaContratacao,
        "B1_CriticidadeEntrega": B1_CriticidadeEntrega,
        # Bloco 2
        "B2_DependenciaPessoasChave": B2_DependenciaPessoasChave,
        "B2_TempoSubstituicao": B2_TempoSubstituicao,
        "B2_RiscoVacancia": B2_RiscoVacancia,
        "B2_NivelCapacitacao": B2_NivelCapacitacao,
        # Bloco 3
        "B3_DependenciaSistemas": B3_DependenciaSistemas,
        "B3_TipoSistema": B3_TipoSistema,
        "B3_MaturidadeSistema": B3_MaturidadeSistema,
        "B3_ContingenciaManual": B3_ContingenciaManual,
        "B3_HistoricoFalhas": B3_HistoricoFalhas,
        # Bloco 4
        "B4_PrazosNormativos": B4_PrazosNormativos,
        "B4_OrigemPrazo": B4_OrigemPrazo,
        "B4_ConsequenciaDescumprimento": B4_ConsequenciaDescumprimento,
        "B4_MargemRenegociacao": B4_MargemRenegociacao,
        "B4_PressaoExterna": B4_PressaoExterna,
        # Bloco 5
        "B5_AtribuicaoDecisoria": B5_AtribuicaoDecisoria,
        "B5_AtoGovernanca": B5_AtoGovernanca,
        "B5_DependenciaInstancias": B5_DependenciaInstancias,
        "B5_PrevisibilidadeDecisao": B5_PrevisibilidadeDecisao,
        "B5_ConflitoCompetencia": B5_ConflitoCompetencia,
        # Bloco 6
        "B6_ImpactoDiferenciado": B6_ImpactoDiferenciado,
        "B6_GruposAfetados": B6_GruposAfetados,
        "B6_NaturezaImpacto": B6_NaturezaImpacto,
        "B6_EscalaImpacto": B6_EscalaImpacto,
        "B6_MedidasMitigacao": B6_MedidasMitigacao,
    }
    enum_class = enums_map.get(enum_name)
    if enum_class:
        return [e.value for e in enum_class]
    return []


def validar_resposta(bloco: str, pergunta: str, valor: Any) -> bool:
    """Valida se uma resposta e valida para a pergunta"""
    if bloco not in BLOCOS_SCHEMA:
        return False
    if pergunta not in BLOCOS_SCHEMA[bloco]["perguntas"]:
        return False

    pergunta_info = BLOCOS_SCHEMA[bloco]["perguntas"][pergunta]
    valores_validos = get_enum_values(pergunta_info["enum"])

    # Multipla escolha
    if pergunta_info.get("multipla_escolha"):
        if not isinstance(valor, list):
            return False
        return all(v in valores_validos for v in valor)

    # Escolha unica
    return valor in valores_validos
