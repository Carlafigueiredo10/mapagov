"""
Enums neutros para Analise de Riscos

Este modulo fica em processos/ (camada de infra/models) e NAO depende de domain.
O domain pode re-exportar daqui se precisar.

Usado por:
- models_analise_riscos.py (choices de campos)
- domain/helena_analise_riscos/enums.py (re-exporta)
"""
from enum import Enum


class StatusAnalise(str, Enum):
    """Status da analise de risco"""
    RASCUNHO = "RASCUNHO"
    EM_ANALISE = "EM_ANALISE"
    FINALIZADA = "FINALIZADA"


class ModoEntrada(str, Enum):
    """Modo de entrada do contexto para analise"""
    QUESTIONARIO = "QUESTIONARIO"  # Entrada via questionario estruturado
    PDF = "PDF"                    # Entrada via upload de PDF (futuro)
    ID = "ID"                      # Entrada via integracao com sistema (futuro)


class TipoOrigem(str, Enum):
    """Tipo do objeto sendo analisado"""
    PROJETO = "PROJETO"
    PROCESSO = "PROCESSO"
    POP = "POP"
    POLITICA = "POLITICA"
    NORMA = "NORMA"
    PLANO = "PLANO"


class EstrategiaResposta(str, Enum):
    """Estrategias de resposta ao risco - Guia MGI

    4 estrategias oficiais conforme Guia de Gestao de Riscos do MGI:
    - MITIGAR: Reduzir probabilidade ou impacto
    - EVITAR: Eliminar a causa do risco
    - COMPARTILHAR: Transferir ou dividir parte do risco
    - ACEITAR: Reconhecer sem acao imediata (requer justificativa para ALTO/CRITICO)
    """
    MITIGAR = "MITIGAR"
    EVITAR = "EVITAR"
    COMPARTILHAR = "COMPARTILHAR"
    ACEITAR = "ACEITAR"


class NivelRisco(str, Enum):
    """Nivel de risco baseado no score"""
    BAIXO = "BAIXO"
    MEDIO = "MEDIO"
    ALTO = "ALTO"
    CRITICO = "CRITICO"


class GrauConfianca(str, Enum):
    """Grau de confianca da inferencia de risco"""
    BAIXO = "BAIXO"
    MEDIO = "MEDIO"
    ALTO = "ALTO"


class CategoriaRisco(str, Enum):
    """Categorias de risco inferidas pelo sistema

    5 categorias conforme desenho conceitual:
    - OPERACIONAL: riscos de execucao e processos
    - LEGAL: riscos juridicos e de compliance
    - TECNOLOGICO: riscos de sistemas e infraestrutura
    - REPUTACIONAL: riscos de imagem institucional
    - IMPACTO_DESIGUAL: riscos de equidade/distribuicao desigual
    """
    OPERACIONAL = "OPERACIONAL"
    LEGAL = "LEGAL"
    TECNOLOGICO = "TECNOLOGICO"
    REPUTACIONAL = "REPUTACIONAL"
    IMPACTO_DESIGUAL = "IMPACTO_DESIGUAL"


class StatusTratamento(str, Enum):
    """Status de tratamento do risco (derivado, nao persistido)

    Usado para transparencia gerencial:
    - Se nao existe resposta formal -> PENDENTE_DE_DELIBERACAO
    - Se existe resposta formal -> RESPONDIDO

    NOTA: Campo derivado na API, nao requer migration.
    """
    PENDENTE_DE_DELIBERACAO = "PENDENTE_DE_DELIBERACAO"
    RESPONDIDO = "RESPONDIDO"


# =============================================================================
# BLOCO B - CAMPOS ESTRUTURADOS (ADITIVO)
# =============================================================================
# Novos enums para melhorar qualidade dos dados do Bloco B
# Sao ADITIVOS - campos antigos de texto continuam existindo
# Chave ausente = nao respondeu (diferente de lista vazia ou NAO_SEI)


class BlocoBRecurso(str, Enum):
    """Tipos de recursos necessarios (checklist, multipla escolha)"""
    PESSOAS = "PESSOAS"
    TI = "TI"
    ORCAMENTO = "ORCAMENTO"
    EQUIPAMENTOS = "EQUIPAMENTOS"
    INFRAESTRUTURA = "INFRAESTRUTURA"
    MATERIAIS = "MATERIAIS"


class BlocoBFrequencia(str, Enum):
    """Frequencia de execucao do processo/projeto"""
    CONTINUO = "CONTINUO"      # Diario/semanal
    PERIODICO = "PERIODICO"    # Mensal/trimestral
    PONTUAL = "PONTUAL"        # Evento unico
    SOB_DEMANDA = "SOB_DEMANDA"


class BlocoBSLA(str, Enum):
    """Existencia de prazos legais ou SLAs

    NAO_SEI e valor valido - indica que o usuario nao tem certeza.
    Nao deve ser tratado como NAO pelo adaptador.
    """
    SIM = "SIM"
    NAO = "NAO"
    NAO_SEI = "NAO_SEI"


class BlocoBDependencia(str, Enum):
    """Tipo de dependencia externa

    NAO_SEI e valor valido - indica que o usuario nao tem certeza.
    Nao deve ser tratado como NAO pelo adaptador.
    """
    NAO = "NAO"
    SISTEMAS = "SISTEMAS"
    TERCEIROS = "TERCEIROS"
    AMBOS = "AMBOS"
    NAO_SEI = "NAO_SEI"


class BlocoBIncidentes(str, Enum):
    """Historico de incidentes/problemas

    NAO_SEI e valor valido - indica que o usuario nao tem certeza.
    Nao deve ser tratado como NAO pelo adaptador.
    """
    SIM = "SIM"
    NAO = "NAO"
    NAO_SEI = "NAO_SEI"
