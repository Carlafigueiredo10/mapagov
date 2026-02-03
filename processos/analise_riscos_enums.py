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
    """Estrategias de resposta ao risco

    RESGUARDAR: Risco conhecido, aceito institucionalmente,
    registrado para fins de governanca, transparencia e controle.
    Nao e omissao - e decisao consciente e rastreavel.
    """
    MITIGAR = "MITIGAR"
    EVITAR = "EVITAR"
    COMPARTILHAR = "COMPARTILHAR"
    ACEITAR = "ACEITAR"
    RESGUARDAR = "RESGUARDAR"


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
