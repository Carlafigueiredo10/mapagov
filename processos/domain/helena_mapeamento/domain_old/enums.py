"""
Enumerações do domínio - elimina magic strings e centraliza lógica de classificação
"""
from enum import Enum, auto


class EstadoConversacao(Enum):
    """Estados da conversa com Helena POP"""
    NOME = auto()
    CONFIRMA_NOME = auto()
    PRE_EXPLICACAO = auto()
    EXPLICACAO = auto()
    EXPLICACAO_FINAL = auto()
    AREA = auto()
    ARQUITETURA = auto()
    SISTEMAS = auto()
    CAMPOS = auto()
    DOCUMENTOS = auto()
    PONTOS_ATENCAO = auto()
    PRE_ETAPAS = auto()
    ETAPAS = auto()
    ENTREGA_ESPERADA = auto()  # ✨ NOVO: Pergunta "Qual a entrega esperada desta atividade?"
    FLUXOS_ENTRADA = auto()
    FLUXOS_SAIDA = auto()
    FLUXOS = auto()
    REVISAO = auto()
    SELECIONAR_EDICAO = auto()


class RespostaSN(Enum):
    """Classificador de respostas Sim/Não"""
    SIM = {"sim", "s", "ok", "yes", "claro", "vamos", "bora", "uhum",
           "aham", "beleza", "tudo bem", "sigo", "pode", "pode ser",
           "pronta", "pronto", "vamo", "entendi", "yes", "y"}
    NAO = {"não", "nao", "n", "no", "jamais"}

    @classmethod
    def classificar(cls, texto: str):
        """
        Classifica texto como SIM, NAO ou None (ambíguo)

        Args:
            texto: String a classificar (será normalizada)

        Returns:
            RespostaSN.SIM, RespostaSN.NAO ou None
        """
        import unicodedata

        # Normalizar (remover acentos, lowercase, strip)
        normalizado = ''.join(
            c for c in unicodedata.normalize('NFD', texto.lower().strip())
            if unicodedata.category(c) != 'Mn'
        )

        if normalizado in cls.SIM.value:
            return cls.SIM
        if normalizado in cls.NAO.value:
            return cls.NAO
        return None


class EstadoEtapa(Enum):
    """Estados da máquina de estados de uma etapa"""
    DESCRICAO = auto()
    OPERADOR = auto()
    PERGUNTA_CONDICIONAL = auto()
    TIPO_CONDICIONAL = auto()
    ANTES_DECISAO = auto()
    CENARIOS = auto()
    SUBETAPAS_CENARIO = auto()
    DETALHES = auto()
    FINALIZADA = auto()


class TipoInterface(Enum):
    """Tipos de interface suportados pelo frontend"""
    TEXTO = "texto"
    AREAS = "areas"
    DROPDOWN_MACRO = "dropdown_macro"
    DROPDOWN_PROCESSO = "dropdown_processo"
    DROPDOWN_PROCESSO_TL = "dropdown_processo_com_texto_livre"
    DROPDOWN_SUBPROCESSO = "dropdown_subprocesso"
    DROPDOWN_SUBPROCESSO_TL = "dropdown_subprocesso_com_texto_livre"
    DROPDOWN_ATIVIDADE = "dropdown_atividade"
    DROPDOWN_ATIVIDADE_TL = "dropdown_atividade_com_texto_livre"
    SISTEMAS = "sistemas"
    NORMAS = "normas"
    OPERADORES = "operadores"
    OPERADORES_ETAPA = "operadores_etapa"
    DOCUMENTOS = "documentos"
    CONDICIONAIS = "condicionais"
    CONDICIONAIS_AJUDA = "condicionais_ajuda"
    TIPO_CONDICIONAL = "tipo_condicional"
    CENARIOS_BINARIO = "cenarios_binario"
    CENARIOS_MULTIPLOS_QUANTIDADE = "cenarios_multiplos_quantidade"
    SUBETAPAS_CENARIO = "subetapas_cenario"
    ETAPAS_TEMPO_REAL = "etapas_tempo_real"
    FLUXOS_ENTRADA = "fluxos_entrada"
    FLUXOS_SAIDA = "fluxos_saida"
    REVISAO = "revisao"
    SELECAO_EDICAO = "selecao_edicao"
    FINAL = "final"
