"""
Helena POP v2.0 - Mapeamento de Processos Operacionais Padrão

Arquitetura Clean:
- Herda de BaseHelena (stateless)
- Estado gerenciado via session_data
- Sem dependências externas de domain_old/infra_old
- Máquina de estados para coleta de dados do processo

Refatorado em 2024-11:
- Funções de governança extraídas para processos/domain/governanca/
- Loaders de dados extraídos para processos/infra/loaders/
"""
from enum import Enum
from typing import Dict, Any, List
import logging
import re
import json

from processos.domain.base import BaseHelena
from processos.infra.parsers import parse_operadores
from processos.domain.helena_mapeamento.normalizar_etapa import normalizar_etapa, normalizar_etapas

# === IMPORTS DOS MÓDULOS EXTRAÍDOS ===
# Governança (regras de negócio)
from processos.domain.governanca import (
    gerar_cap_provisorio_seguro,
    detectar_atividades_similares,
    salvar_atividade_sugerida,
)

# Loaders (carregamento de dados)
from processos.infra.loaders import (
    carregar_areas_organizacionais,
    carregar_descricoes_areas,
    carregar_sistemas,
    carregar_operadores,
    carregar_orgaos_centralizados,
    carregar_canais_atendimento,
    ArquiteturaDecipex,
    carregar_arquitetura_csv,
    carregar_tipos_documentos_requeridos,
    carregar_tipos_documentos_gerados,
)

# Tentativa de importar BaseLegalSuggestorDECIPEx (opcional)
try:
    from processos.base_legal_decipex import BaseLegalSuggestorDECIPEx
    BASE_LEGAL_DISPONIVEL = True
except ImportError:
    BASE_LEGAL_DISPONIVEL = False

logger = logging.getLogger(__name__)

logger.info("helena_pop.py carregado (v2.0)")

# Feature flag: quando True, etapas são coletadas inline dentro do POP
# Quando False, mantém fluxo antigo com mudar_contexto para HelenaEtapas
import os
ETAPAS_INLINE = os.environ.get('ETAPAS_INLINE', 'true').lower() == 'true'

# EtapaStateMachine reutilizada como módulo (não como agente separado)
from processos.domain.helena_mapeamento.helena_etapas import (
    EtapaStateMachine, EstadoEtapa
)


# ============================================================================
# CONSTANTES - Palavras-chave para detecção de intenção
# ============================================================================

# ✅ Tokens determinísticos (lowercase para comparação com casefold)
# Frontend envia em UPPERCASE, backend compara em lowercase via casefold()

PALAVRAS_CONFIRMACAO = frozenset([
    'sim', 's', 'pode', 'ok', 'claro', 'entendi', 'beleza', 'tudo',
    'concordo', 'confirmar', 'correto', 'certo', 'continuar', 'vamos',
    'seguir', 'próximo', 'conte', 'contigo', 'melhor', 'farei', 'junto',
    'tudo certo', 'ja entendi', 'já entendi', 'ok_entendi',
    # Tokens determinísticos (lowercase)
    '__confirmar_dupla__', '__confirmar__', '__seguir__'
])
PALAVRAS_NEGACAO = frozenset(['não', 'nao', 'n', 'nenhum', 'não há', 'nao ha', 'não tem', 'nao tem', 'sem pontos', 'pular', 'skip', '__pular__'])
PALAVRAS_DUVIDAS = frozenset(['duvida', 'dúvida', 'duvidas', 'dúvidas', 'mais duvidas', 'mais dúvidas', 'tenho duvidas', 'tenho dúvidas'])
PALAVRAS_DETALHES = frozenset(['detalhada', 'longa', 'detalhes', 'completa', 'detalhe'])
PALAVRAS_OBJETIVA = frozenset(['objetiva', 'curta', 'rápida', 'rapida', 'resumida'])
PALAVRAS_EDICAO = frozenset(['editar', 'edit', 'corrigir', 'alterar', 'mudar', 'ajustar', 'arrumar', 'manual', '__editar_dupla__'])
PALAVRAS_PAUSA = frozenset(['pausa', 'pausar', 'esperar', 'depois', 'mais tarde', 'aguardar', 'salvar'])
PALAVRAS_CANCELAR = frozenset(['cancelar', 'voltar', 'sair', '__cancelar__'])
PALAVRAS_MAIS_PERGUNTA = frozenset(['mais_pergunta', 'mais', 'pergunta', 'tenho mais'])


# ============================================================================
# ENUMS - Estados da Conversa
# ============================================================================

class EstadoPOP(str, Enum):
    """Estados da máquina de estados para coleta do POP"""
    # BOAS_VINDAS removido - começa direto em NOME_USUARIO (evita duplicação)
    NOME_USUARIO = "nome_usuario"
    ESCOLHA_TIPO_EXPLICACAO = "escolha_tipo_explicacao"  # 🆕 Escolher explicação curta ou longa
    EXPLICACAO_LONGA = "explicacao_longa"  # 🆕 Explicação detalhada do processo
    DUVIDAS_EXPLICACAO = "duvidas_explicacao"  # 🆕 Lidar com dúvidas sobre a explicação
    EXPLICACAO = "explicacao"
    PEDIDO_COMPROMISSO = "pedido_compromisso"  # 🆕 Pedido de compromisso antes de começar
    AREA_DECIPEX = "area_decipex"
    SUBAREA_DECIPEX = "subarea_decipex"  # 🆕 Seleção de subárea (ex: DIGEP-RO, DIGEP-RR, DIGEP-AP)
    ARQUITETURA = "arquitetura"
    CONFIRMACAO_ARQUITETURA = "confirmacao_arquitetura"  # 🎯 NOVO: confirmar arquitetura sugerida pela IA
    SELECAO_HIERARQUICA = "selecao_hierarquica"  # 🆕 FALLBACK: seleção manual via dropdowns hierárquicos
    NOME_PROCESSO = "nome_processo"
    ENTREGA_ESPERADA = "entrega_esperada"
    CONFIRMACAO_ENTREGA = "confirmacao_entrega"  # 🎯 NOVO: confirmar/editar entrega
    RECONHECIMENTO_ENTREGA = "reconhecimento_entrega"  # 🎯 Gamificação após entrega
    DISPOSITIVOS_NORMATIVOS = "dispositivos_normativos"
    TRANSICAO_ROADTRIP = "transicao_roadtrip"  # 🚗 Animação de transição entre normas e operadores
    OPERADORES = "operadores"
    SISTEMAS = "sistemas"
    FLUXOS = "fluxos"
    PONTOS_ATENCAO = "pontos_atencao"  # 🎯 Novo campo do OLD
    REVISAO_PRE_DELEGACAO = "revisao_pre_delegacao"  # 🎯 REVISÃO 2: após coletar tudo
    TRANSICAO_EPICA = "transicao_epica"  # 🎯 Transição motivacional antes das etapas
    SELECAO_EDICAO = "selecao_edicao"  # 🎯 Menu de edição granular
    DELEGACAO_ETAPAS = "delegacao_etapas"
    # Coleta inline de etapas (ETAPAS_INLINE=True)
    ETAPA_FORM = "etapa_form"  # Form unico por etapa (campos lineares)
    ETAPA_DESCRICAO = "etapa_descricao"
    ETAPA_OPERADOR = "etapa_operador"
    ETAPA_SISTEMAS = "etapa_sistemas"
    ETAPA_DOCS_REQUERIDOS = "etapa_docs_requeridos"
    ETAPA_DOCS_GERADOS = "etapa_docs_gerados"
    ETAPA_TEMPO = "etapa_tempo"
    ETAPA_CONDICIONAL = "etapa_condicional"
    ETAPA_TIPO_CONDICIONAL = "etapa_tipo_condicional"
    ETAPA_ANTES_DECISAO = "etapa_antes_decisao"
    ETAPA_CENARIOS = "etapa_cenarios"
    ETAPA_SUBETAPAS_CENARIO = "etapa_subetapas_cenario"
    ETAPA_DETALHES = "etapa_detalhes"
    ETAPA_MAIS = "etapa_mais"
    ETAPA_REVISAO = "etapa_revisao"
    REVISAO_FINAL = "revisao_final"  # Hub de revisão completa antes de finalizar
    FINALIZADO = "finalizado"


# ============================================================================
# NOTA: Funções de governança e ArquiteturaDecipex foram movidas para:
# - processos/domain/governanca/ (cap_generator, duplicatas, atividade_sugerida, versionamento_csv)
# - processos/infra/loaders/ (ArquiteturaDecipex, areas, sistemas, operadores, etc.)
#
# Os imports no topo do arquivo mantêm compatibilidade.
# ============================================================================


# ============================================================================
# STATE MACHINE - POPStateMachine
# ============================================================================

class POPStateMachine:
    """Máquina de estados para coletar dados do POP"""

    # Estrutura padrão de dados coletados (evita duplicação)
    DADOS_COLETADOS_DEFAULT = {
        'nome_processo': '',
        'entrega_esperada': '',
        'dispositivos_normativos': [],
        'operadores': [],
        'sistemas': [],
        'documentos': [],
        'fluxos_entrada': [],
        'fluxos_saida': []
    }

    def __init__(self):
        self.estado = EstadoPOP.NOME_USUARIO
        self.nome_usuario = ""
        self.area_selecionada = None
        self.subarea_selecionada = None
        self.macro_selecionado = None
        self.processo_selecionado = None
        self.subprocesso_selecionado = None
        self.atividade_selecionada = None
        self.codigo_cap = None
        self.dados_coletados = {**self.DADOS_COLETADOS_DEFAULT}
        self.concluido = False
        # Controle de delegação para Helena Mapeamento
        self.em_modo_duvidas = False
        self.contexto_duvidas = None
        self.estado_helena_mapeamento = None  # Estado interno do Helena Mapeamento
        # ✅ FIX: Persistir interface entre requests (resolve bug de 3 cliques)
        self.tipo_interface = None
        self.dados_interface = {}
        # Coleta inline de etapas
        self.etapas_coletadas: List[Dict[str, Any]] = []
        self._etapa_sm = None  # EtapaStateMachine serializada (dict ou None)
        # Retorno para revisão final após edição de seção
        self.return_to: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serializa o state machine para JSON"""
        return {
            'estado': self.estado.value,
            'nome_usuario': self.nome_usuario,
            'area_selecionada': self.area_selecionada,
            'subarea_selecionada': self.subarea_selecionada,  # 🆕 Subáreas
            'macro_selecionado': self.macro_selecionado,
            'processo_selecionado': self.processo_selecionado,
            'subprocesso_selecionado': self.subprocesso_selecionado,
            'atividade_selecionada': self.atividade_selecionada,
            'codigo_cap': self.codigo_cap,  # 🎯 CAP ÚNICO
            'dados_coletados': self.dados_coletados,
            'concluido': self.concluido,
            'em_modo_duvidas': self.em_modo_duvidas,
            'contexto_duvidas': self.contexto_duvidas,
            'estado_helena_mapeamento': self.estado_helena_mapeamento,
            # ✅ FIX: Persistir interface entre requests (resolve bug de 3 cliques)
            'tipo_interface': self.tipo_interface,
            'dados_interface': self.dados_interface,
            # Coleta inline de etapas
            'etapas_coletadas': self.etapas_coletadas,
            '_etapa_sm': self._etapa_sm,
            # Retorno para revisão final
            'return_to': self.return_to,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'POPStateMachine':
        """Deserializa o state machine do JSON"""
        sm = cls()

        # Migração de estados removidos
        MIGRACOES_ESTADO = {
            'confirma_nome': EstadoPOP.NOME_USUARIO,
        }

        estado_raw = data.get('estado', EstadoPOP.NOME_USUARIO.value)
        if estado_raw in MIGRACOES_ESTADO:
            destino = MIGRACOES_ESTADO[estado_raw]
            logger.info(f"[from_dict] Migrando estado removido '{estado_raw}' → {destino.value}")
            sm.estado = destino
        else:
            try:
                sm.estado = EstadoPOP(estado_raw)
            except ValueError:
                logger.warning(f"[from_dict] Estado desconhecido '{estado_raw}', resetando para NOME_USUARIO")
                sm.estado = EstadoPOP.NOME_USUARIO

        # Migração: nome_temporario (campo removido) → nome_usuario
        sm.nome_usuario = data.get('nome_usuario', '') or data.get('nome_temporario', '')
        sm.area_selecionada = data.get('area_selecionada')
        sm.subarea_selecionada = data.get('subarea_selecionada')  # 🆕 Subáreas
        sm.macro_selecionado = data.get('macro_selecionado')
        sm.processo_selecionado = data.get('processo_selecionado')
        sm.subprocesso_selecionado = data.get('subprocesso_selecionado')
        sm.atividade_selecionada = data.get('atividade_selecionada')
        sm.codigo_cap = data.get('codigo_cap')  # 🎯 CAP ÚNICO
        sm.dados_coletados = data.get('dados_coletados', {**cls.DADOS_COLETADOS_DEFAULT})
        sm.concluido = data.get('concluido', False)
        sm.em_modo_duvidas = data.get('em_modo_duvidas', False)
        sm.contexto_duvidas = data.get('contexto_duvidas')
        sm.estado_helena_mapeamento = data.get('estado_helena_mapeamento')
        # ✅ FIX: Recuperar interface entre requests (resolve bug de 3 cliques)
        sm.tipo_interface = data.get('tipo_interface')
        sm.dados_interface = data.get('dados_interface', {})
        # Coleta inline de etapas (defaults seguros para sessões antigas)
        sm.etapas_coletadas = data.get('etapas_coletadas', [])
        sm._etapa_sm = data.get('_etapa_sm')
        # Retorno para revisão final
        sm.return_to = data.get('return_to')
        return sm


# ============================================================================
# HELENA POP v2.0
# ============================================================================

class HelenaPOP(BaseHelena):
    """
    Helena POP v2.0 - Coleta de dados para mapeamento de processos

    Responsabilidades:
    - Guiar usuário através da coleta de dados do processo
    - Integrar com arquitetura DECIPEX
    - Sugerir base legal quando disponível
    - Preparar dados para delegação ao Helena Etapas
    """

    VERSION = "2.0.0"
    PRODUTO_NOME = "Helena POP"

    def __init__(self):
        super().__init__()

        # Carregar arquitetura DECIPEX
        self.arquitetura = ArquiteturaDecipex()

        # Integração base legal (opcional)
        if BASE_LEGAL_DISPONIVEL:
            try:
                self.suggestor_base_legal = BaseLegalSuggestorDECIPEx()
            except Exception as e:
                logger.warning(f"Não foi possível carregar BaseLegalSuggestorDECIPEx: {e}")
                self.suggestor_base_legal = None
        else:
            self.suggestor_base_legal = None

        # Memória anti-repetição de sugestões
        self._atividades_sugeridas = []
        self._codigos_sugeridos = set()

        # Lazy loading do pipeline de busca
        self._pipeline_instance = None

    # ========================================================================
    # HELPER - Detecção de Intenção
    # ========================================================================

    def _detectar_intencao(self, msg: str, tipo: str) -> bool:
        """
        Detecta intenção do usuário baseado em palavras-chave.

        Args:
            msg: Texto do usuário
            tipo: 'confirmacao', 'negacao', 'duvidas', 'detalhes', 'objetiva',
                  'edicao', 'pausa', 'cancelar', 'mais_pergunta'

        Returns:
            True se alguma palavra-chave do tipo foi encontrada na mensagem
        """
        # Normaliza para comparação case-insensitive
        msg_norm = (msg or "").strip().casefold()

        # ✅ DETECÇÃO EXATA de tokens determinísticos (comparação em minúsculo)
        if tipo == 'confirmacao':
            if msg_norm in ("__confirmar_dupla__", "__confirmar__", "__seguir__"):
                return True
        elif tipo == 'edicao':
            if msg_norm == "__editar_dupla__":
                return True
        elif tipo == 'negacao':
            if msg_norm == "__pular__":
                return True
        elif tipo == 'cancelar':
            if msg_norm == "__cancelar__":
                return True

        # Heurísticas normais (palavras-chave)
        palavras_map = {
            'confirmacao': PALAVRAS_CONFIRMACAO,
            'negacao': PALAVRAS_NEGACAO,
            'duvidas': PALAVRAS_DUVIDAS,
            'detalhes': PALAVRAS_DETALHES,
            'objetiva': PALAVRAS_OBJETIVA,
            'edicao': PALAVRAS_EDICAO,
            'pausa': PALAVRAS_PAUSA,
            'cancelar': PALAVRAS_CANCELAR,
            'mais_pergunta': PALAVRAS_MAIS_PERGUNTA,
        }
        palavras = palavras_map.get(tipo, frozenset())
        return any(palavra in msg_norm for palavra in palavras)

    @property
    def _pipeline(self):
        """Lazy loading do BuscaAtividadePipeline (instância única)"""
        if self._pipeline_instance is None:
            from processos.domain.helena_mapeamento.busca_atividade_pipeline import BuscaAtividadePipeline
            self._pipeline_instance = BuscaAtividadePipeline()
        return self._pipeline_instance

    # ========================================================================
    # PROPERTIES - Usam os loaders extraídos em processos/infra/loaders/
    # ========================================================================

    @property
    def AREAS_DECIPEX(self) -> Dict[int, Dict[str, str]]:
        """Áreas organizacionais carregadas do CSV via loader."""
        return carregar_areas_organizacionais()

    @property
    def DESCRICOES_AREAS(self) -> Dict[str, str]:
        """Descrições personalizadas de cada área via loader."""
        return carregar_descricoes_areas()

    @property
    def SISTEMAS_DECIPEX(self) -> Dict[str, List[str]]:
        """Sistemas carregados do CSV via loader."""
        return carregar_sistemas()

    @property
    def OPERADORES_DECIPEX(self) -> List[str]:
        """Operadores carregados do CSV via loader."""
        return carregar_operadores()

    def _preparar_dados_dropdown_hierarquico(self) -> Dict[str, Any]:
        """
        Prepara dados para interface de dropdown hierárquico (fallback quando IA falha).

        Returns:
            dict: Dados formatados para o frontend renderizar os dropdowns cascateados
        """
        estrutura = carregar_arquitetura_csv()

        # Formato para o frontend
        dados_dropdown = {
            'macroprocessos': list(estrutura['macroprocessos'].keys()),
            'hierarquia_completa': estrutura['macroprocessos']
        }

        return dados_dropdown

    def inicializar_estado(self, skip_intro: bool = False) -> dict:
        """
        Inicializa estado limpo para Helena POP

        Args:
            skip_intro: Se True, pula a introdução e vai direto para NOME_USUARIO
                       (usado quando frontend já mostrou mensagem de boas-vindas)

        Returns:
            dict: Estado inicial com POPStateMachine
        """
        sm = POPStateMachine()

        # Se frontend já mostrou introdução, pular para coleta de nome
        if skip_intro:
            sm.estado = EstadoPOP.NOME_USUARIO

        return sm.to_dict()

    def processar(self, mensagem: str, session_data: dict) -> dict:
        """
        Processa mensagem do usuário de acordo com o estado atual

        Args:
            mensagem: Texto do usuário
            session_data: Estado atual da sessão

        Returns:
            dict: Resposta com novo estado
        """
        # Validações
        self.validar_mensagem(mensagem)
        self.validar_session_data(session_data)

        # Carregar state machine
        sm = POPStateMachine.from_dict(session_data)

        # 🔍 DEBUG CRÍTICO: Log do estado NO INÍCIO do processamento
        logger.info(f"[PROCESSAR] ===== INÍCIO DO PROCESSAMENTO =====")
        logger.info(f"[PROCESSAR] Estado CARREGADO da sessão: {sm.estado}")
        logger.info(f"[PROCESSAR] Mensagem recebida (primeiros 100 chars): {mensagem[:100]}")
        logger.info(f"[PROCESSAR] ============================================")

        # 🎯 Inicializar variáveis que podem vir dos handlers
        metadados_arquitetura = None
        metadados_extra = None

        # Processar de acordo com o estado
        if sm.estado == EstadoPOP.NOME_USUARIO:
            resposta, novo_sm = self._processar_nome_usuario(mensagem, sm)

        elif sm.estado == EstadoPOP.ESCOLHA_TIPO_EXPLICACAO:
            resposta, novo_sm = self._processar_escolha_tipo_explicacao(mensagem, sm)

        elif sm.estado == EstadoPOP.EXPLICACAO_LONGA:
            resposta, novo_sm = self._processar_explicacao_longa(mensagem, sm)

        elif sm.estado == EstadoPOP.DUVIDAS_EXPLICACAO:
            resposta, novo_sm = self._processar_duvidas_explicacao(mensagem, sm)

        elif sm.estado == EstadoPOP.EXPLICACAO:
            resposta, novo_sm = self._processar_explicacao(mensagem, sm)

        elif sm.estado == EstadoPOP.PEDIDO_COMPROMISSO:
            resposta, novo_sm = self._processar_pedido_compromisso(mensagem, sm)

        elif sm.estado == EstadoPOP.AREA_DECIPEX:
            resultado_area = self._processar_area_decipex(mensagem, sm)
            if len(resultado_area) == 3:
                resposta, novo_sm, metadados_extra = resultado_area
            else:
                resposta, novo_sm = resultado_area
                metadados_extra = None

        elif sm.estado == EstadoPOP.SUBAREA_DECIPEX:
            resultado_subarea = self._processar_subarea_decipex(mensagem, sm)
            if len(resultado_subarea) == 3:
                resposta, novo_sm, metadados_extra = resultado_subarea
            else:
                resposta, novo_sm = resultado_subarea
                metadados_extra = None

        elif sm.estado == EstadoPOP.ARQUITETURA:
            resultado_arq = self._processar_arquitetura(mensagem, sm)
            if len(resultado_arq) == 3:
                resposta, novo_sm, metadados_arquitetura = resultado_arq
            else:
                resposta, novo_sm = resultado_arq
                metadados_arquitetura = None

        elif sm.estado == EstadoPOP.CONFIRMACAO_ARQUITETURA:
            resultado_conf = self._processar_confirmacao_arquitetura(mensagem, sm)
            if len(resultado_conf) == 3:
                resposta, novo_sm, metadados_extra = resultado_conf
            else:
                resposta, novo_sm = resultado_conf
                metadados_extra = None

        elif sm.estado == EstadoPOP.SELECAO_HIERARQUICA:
            resposta, novo_sm = self._processar_selecao_hierarquica(mensagem, sm)

        elif sm.estado == EstadoPOP.NOME_PROCESSO:
            resposta, novo_sm = self._processar_nome_processo(mensagem, sm)

        elif sm.estado == EstadoPOP.ENTREGA_ESPERADA:
            resultado_entrega = self._processar_entrega_esperada(mensagem, sm)
            if len(resultado_entrega) == 3:
                resposta, novo_sm, metadados_extra = resultado_entrega
            else:
                resposta, novo_sm = resultado_entrega
                metadados_extra = None

        elif sm.estado == EstadoPOP.CONFIRMACAO_ENTREGA:
            resposta, novo_sm = self._processar_confirmacao_entrega(mensagem, sm)

        elif sm.estado == EstadoPOP.RECONHECIMENTO_ENTREGA:
            resposta, novo_sm = self._processar_reconhecimento_entrega(mensagem, sm)

        elif sm.estado == EstadoPOP.DISPOSITIVOS_NORMATIVOS:
            resposta, novo_sm = self._processar_dispositivos_normativos(mensagem, sm)

        elif sm.estado == EstadoPOP.TRANSICAO_ROADTRIP:
            resposta, novo_sm = self._processar_transicao_roadtrip(mensagem, sm)

        elif sm.estado == EstadoPOP.OPERADORES:
            logger.info(f"[PROCESSAR] Estado ANTES de chamar _processar_operadores: {sm.estado}")
            resposta, novo_sm = self._processar_operadores(mensagem, sm)
            logger.info(f"[PROCESSAR] Estado DEPOIS de _processar_operadores: {novo_sm.estado}")
            logger.info(f"[PROCESSAR] tipo_interface setado pelo handler: {novo_sm.tipo_interface}")
            # 🔍 DEBUG: Verificar se operadores foram salvos
            logger.info(f"[PROCESSAR] 🔍 OPERADORES SALVOS: {novo_sm.dados_coletados.get('operadores')}")

        elif sm.estado == EstadoPOP.SISTEMAS:
            resposta, novo_sm = self._processar_sistemas(mensagem, sm)

        elif sm.estado == EstadoPOP.FLUXOS:
            resposta, novo_sm = self._processar_fluxos(mensagem, sm)

        elif sm.estado == EstadoPOP.PONTOS_ATENCAO:
            resposta, novo_sm = self._processar_pontos_atencao(mensagem, sm)

        elif sm.estado == EstadoPOP.REVISAO_PRE_DELEGACAO:
            resposta, novo_sm = self._processar_revisao_pre_delegacao(mensagem, sm)

        elif sm.estado == EstadoPOP.TRANSICAO_EPICA:
            resposta, novo_sm = self._processar_transicao_epica(mensagem, sm)

        elif sm.estado == EstadoPOP.REVISAO_FINAL:
            resposta, novo_sm = self._processar_revisao_final(mensagem, sm)

        elif sm.estado == EstadoPOP.DELEGACAO_ETAPAS:
            resposta, novo_sm = self._processar_delegacao_etapas(mensagem, sm)

        elif sm.estado == EstadoPOP.ETAPA_FORM:
            resposta, novo_sm = self._processar_etapa_form(mensagem, sm)

        elif sm.estado.value.startswith('etapa_'):
            resposta, novo_sm = self._processar_etapa_inline(mensagem, sm)

        else:
            logger.error(f"[PROCESSAR] Estado sem handler: {sm.estado} (mensagem: {mensagem[:80]})")
            resposta = (
                "Parece que houve um problema no fluxo da conversa. "
                "Vou te redirecionar para o início da identificação."
            )
            novo_sm = sm
            novo_sm.estado = EstadoPOP.NOME_USUARIO

        # Calcular progresso
        progresso = self._calcular_progresso(novo_sm)
        progresso_detalhado = self.obter_progresso(novo_sm)

        # Verificar se deve sugerir mudança de contexto
        sugerir_contexto = None
        if not ETAPAS_INLINE:
            # Fluxo legado: delegar para agente HelenaEtapas
            if novo_sm.estado == EstadoPOP.DELEGACAO_ETAPAS or novo_sm.concluido:
                sugerir_contexto = 'etapas'

        # 🎯 Inicializar variáveis de interface (serão preenchidas abaixo)
        tipo_interface = None
        dados_interface = None

        # Criar metadados_extra base (ou usar o que veio dos handlers)
        if not metadados_extra:
            metadados_extra = {}

        metadados_extra['progresso_detalhado'] = progresso_detalhado

        # Transição automática para HelenaEtapas (somente fluxo legado)
        if not ETAPAS_INLINE and novo_sm.concluido:
            metadados_extra['mudar_contexto'] = 'etapas'
            metadados_extra['dados_herdados'] = {
                'nome_usuario': novo_sm.nome_usuario,
                'area_selecionada': novo_sm.area_selecionada,
                'dados_coletados': novo_sm.dados_coletados,
            }

        # Mesclar metadados_arquitetura se existir (vindo do pipeline)
        if metadados_arquitetura:
            metadados_extra.update(metadados_arquitetura)

            # ✅ FIX CRÍTICO: Extrair tipo_interface dos metadados do pipeline
            # O pipeline retorna: {'interface': {'tipo': 'sugestao_atividade', 'dados': {...}}}
            # Precisamos popular tipo_interface e dados_interface para o frontend
            if 'interface' in metadados_arquitetura:
                interface_info = metadados_arquitetura['interface']
                tipo_interface = interface_info.get('tipo')
                dados_interface = interface_info.get('dados', {})
                logger.debug(f"[FIX] Extraído do pipeline: tipo_interface={tipo_interface}")

        # Se metadados_extra contém interface (vindo de handlers como CONFIRMACAO_ARQUITETURA ou ENTREGA_ESPERADA)
        if metadados_extra and 'interface' in metadados_extra:
            interface_info = metadados_extra['interface']
            tipo_interface = interface_info.get('tipo')
            dados_interface = interface_info.get('dados', {})
            logger.debug(f"[FIX] Extraído de metadados_extra: tipo_interface={tipo_interface}")

        # Badge de checkpoint na transição épica
        if novo_sm.estado == EstadoPOP.TRANSICAO_EPICA:
            metadados_extra['badge'] = {
                'tipo': 'fase_previa_completa',
                'emoji': '✔',
                'titulo': 'Fase Prévia Concluída!',
                'descricao': 'Primeiro trecho do percurso concluído. Seguimos para o próximo.',
                'mostrar_animacao': True
            }

        # Badge "Parceria confirmada!" ao aceitar compromisso
        if novo_sm.estado == EstadoPOP.AREA_DECIPEX and sm.estado == EstadoPOP.PEDIDO_COMPROMISSO:
            metadados_extra['badge'] = {
                'tipo': 'parceria_confirmada',
                'emoji': '💬',
                'titulo': 'Parceria confirmada!',
                'descricao': 'Você e Helena agora são parceiros nessa jornada de mapeamento!',
                'mostrar_animacao': True
            }

        # 🎯 Definir interface dinâmica baseada no estado (se não foi definida pelo pipeline)
        # IMPORTANTE: Só definir se tipo_interface ainda estiver None (não foi definido pelo pipeline)
        if not tipo_interface and novo_sm.estado == EstadoPOP.PEDIDO_COMPROMISSO:
            # Interface com badge de compromisso (estilo gamificação)
            tipo_interface = 'badge_compromisso'
            dados_interface = {
                'nome_compromisso': 'Compromisso de Cartógrafo(a)',
                'emoji': '🤝',
                'descricao': 'Você se comprometeu a registrar seu processo com cuidado e dedicação!'
            }

        elif novo_sm.estado == EstadoPOP.ESCOLHA_TIPO_EXPLICACAO:
            tipo_interface = 'confirmacao_dupla'
            dados_interface = {
                'botao_confirmar': 'Continuar',
                'botao_editar': 'Pular introdução',
                'valor_confirmar': 'objetiva',
                'valor_editar': 'pular_intro'
            }

        elif novo_sm.estado == EstadoPOP.EXPLICACAO_LONGA:
            # 🆕 Interface após explicação longa: Sim entendi / Não, tenho dúvidas
            tipo_interface = 'confirmacao_dupla'
            dados_interface = {
                'botao_confirmar': '🔹 Continuar',
                'botao_editar': '🔹 Dúvidas',
                'valor_confirmar': 'sim',
                'valor_editar': 'não'
            }

        elif novo_sm.estado == EstadoPOP.AREA_DECIPEX:
            tipo_interface = 'areas'
            dados_interface = {
                'opcoes_areas': {
                    str(num): {'codigo': info['codigo'], 'nome': info['nome']}
                    for num, info in self.AREAS_DECIPEX.items()
                }
            }

        elif novo_sm.estado == EstadoPOP.SUBAREA_DECIPEX:
            tipo_interface = 'subareas'
            dados_interface = {
                'area_pai': {
                    'codigo': novo_sm.area_selecionada['codigo'],
                    'nome': novo_sm.area_selecionada['nome']
                },
                'subareas': novo_sm.area_selecionada.get('subareas', [])
            }

        elif novo_sm.estado == EstadoPOP.SELECAO_HIERARQUICA:
            # 🆕 FALLBACK: Interface de dropdowns hierárquicos para seleção manual
            tipo_interface = 'arquitetura_hierarquica'
            dados_interface = self._preparar_dados_dropdown_hierarquico()

        elif not tipo_interface and novo_sm.estado == EstadoPOP.ARQUITETURA:
            # Interface de texto livre com botão de exemplos (se pipeline não retornou sugestão)
            tipo_interface = 'texto_com_exemplos'
            dados_interface = {
                'placeholder': 'Ex: Faço processo de pré aposentadoria, a pedido do servidor e envio para a área responsável pra análise.',
                'exemplos': [
                    "Analiso pensões. Fica pronto: o parecer aprovando ou negando, informo pro usuário.",
                    "Cadastro atos. Fica pronto: o ato no sistema, envio pro TCU.",
                    "Faço cálculos. Fica pronto: a planilha de valores vai pra AGU.",
                    "Faço pré-cadastro pra aposentadoria vai pra CGBEN."
                ]
            }

        elif novo_sm.estado == EstadoPOP.TRANSICAO_EPICA:
            # Interface épica com botões no padrão confirmacao_dupla
            tipo_interface = 'transicao_epica'
            dados_interface = {
                'botao_principal': {
                    'texto': 'Vamos começar ✅',
                    'classe': 'btn-confirmar',
                    'tamanho': 'grande',
                    'cor': '#28a745',
                    'animacao': '',
                    'valor_enviar': 'VAMOS'
                },
                'botao_secundario': {
                    'texto': 'Salvar e continuar depois ✏️',
                    'classe': 'btn-editar',
                    'posicao': 'abaixo',
                    'valor_enviar': 'PAUSA'
                },
                'mostrar_progresso': False,
                'progresso_texto': '',
                'background_especial': False
            }

        elif novo_sm.estado == EstadoPOP.RECONHECIMENTO_ENTREGA:
            # Gamificação após entrega esperada
            tipo_interface = 'caixinha_reconhecimento'
            dados_interface = {
                'nome_usuario': novo_sm.nome_usuario or 'você'
            }

        elif novo_sm.estado == EstadoPOP.DELEGACAO_ETAPAS:
            # Interface de transição e auto-redirect (fluxo legado)
            tipo_interface = 'transicao'
            dados_interface = {
                'proximo_modulo': 'etapas',
                'auto_redirect': True,
                'delay_ms': 2000
            }

        # Estados de etapa inline: interface já definida em _processar_etapa_inline
        elif not tipo_interface and novo_sm.estado.value.startswith('etapa_'):
            if hasattr(novo_sm, 'tipo_interface') and novo_sm.tipo_interface:
                tipo_interface = novo_sm.tipo_interface
                dados_interface = getattr(novo_sm, 'dados_interface', {})

        elif not tipo_interface and novo_sm.estado == EstadoPOP.CONFIRMACAO_ARQUITETURA:
            # Interface com 2 botões: Concordo / Editar manualmente
            # IMPORTANTE: Só definir se tipo_interface ainda não foi setado (ex: pelo pipeline RAG)
            tipo_interface = 'confirmacao_dupla'
            dados_interface = {
                'botao_confirmar': 'Concordo com a sugestão ✅',
                'botao_editar': 'Quero editar manualmente ✏️',
                'valor_confirmar': 'sim',
                'valor_editar': 'editar'
            }

        elif novo_sm.estado == EstadoPOP.DISPOSITIVOS_NORMATIVOS:
            grupos_normas = {}
            if self.suggestor_base_legal:
                try:
                    grupos_normas = self.suggestor_base_legal.obter_grupos_normas()
                except:
                    pass

            tipo_interface = 'normas'
            dados_interface = {
                'grupos': grupos_normas,
                'campo_livre': True,
                'multipla_selecao': True,
                'texto_introducao': (
                    "• Utilize a lista disponível para localizar normas já cadastradas.\n\n"
                    "• Caso necessário, é possível adicionar normas manualmente.\n\n"
                    "• Para apoio na pesquisa de normas, está disponível o acesso à **IA do Sigepe Legis**, "
                    "ferramenta mantida pelo setor de legislação, que auxilia na localização de referências normativas.\n\n"
                    "O registro das normas é de responsabilidade de quem conduz o mapeamento."
                )
            }

        elif novo_sm.estado == EstadoPOP.TRANSICAO_ROADTRIP:
            logger.info(f"🚗🚗🚗 [PROXIMA_INTERFACE] ENTROU NO ELIF TRANSICAO_ROADTRIP!")

            # ✅ SEMPRE mostrar interface roadtrip junto com a mensagem (solução simplificada)
            tipo_interface = 'roadtrip'
            dados_interface = {}
            logger.info(f"🚗 [PROXIMA_INTERFACE] Definindo interface roadtrip! tipo={tipo_interface}")

        elif novo_sm.estado == EstadoPOP.OPERADORES:
            # Interface rica de operadores
            tipo_interface = 'operadores'
            dados_interface = {
                'opcoes': self.OPERADORES_DECIPEX,
                'campo_livre': True,
                'multipla_selecao': True
            }

        elif novo_sm.estado == EstadoPOP.SISTEMAS:
            # Interface rica de sistemas organizados
            tipo_interface = 'sistemas'
            dados_interface = {
                'sistemas_por_categoria': self.SISTEMAS_DECIPEX,
                'campo_livre': True,
                'multipla_selecao': True
            }

        # ✅ FIX: Verificar se o state machine tem tipo_interface setado
        # (usado por _processar_fluxos, etc.)
        # IMPORTANTE: Não sobrescrever se já foi extraído dos metadados do pipeline
        logger.info(f"[PROCESSAR] Antes de ler sm.tipo_interface: tipo_interface={tipo_interface}, novo_sm.estado={novo_sm.estado}")
        if hasattr(novo_sm, 'tipo_interface') and novo_sm.tipo_interface:
            logger.info(f"[PROCESSAR] sm.tipo_interface EXISTE e é: {novo_sm.tipo_interface}")
        if not tipo_interface and hasattr(novo_sm, 'tipo_interface') and novo_sm.tipo_interface:
            tipo_interface = novo_sm.tipo_interface
            dados_interface = getattr(novo_sm, 'dados_interface', {})
            logger.info(f"[PROCESSAR] ✅ tipo_interface ATUALIZADO de sm para: {tipo_interface}")

        # 🎯 PREENCHIMENTO EM TEMPO REAL - Dados do formulário POP
        formulario_pop = self._preparar_dados_formulario(novo_sm)

        # ✅ FIX CRÍTICO: Frontend OLD lia "dados_extraidos", não "formulario_pop"
        # Enviar AMBOS para compatibilidade total
        dados_extraidos = formulario_pop.copy()

        # 🔒 INVARIANTE DE SEGURANÇA: Garantir resposta=None em modo interface
        # Evita regressões caso alguém esqueça de definir resposta=None em algum handler
        if tipo_interface and resposta == "":
            resposta = None

        # DEBUG: Log para verificar se dados estão sendo enviados
        def _short(r):
            """Helper para log: diferenciar None vs "" vs texto"""
            if r is None: return "<None>"
            if r == "": return "<vazia>"
            return r[:100]

        logger.info(f"[DEBUG] Dados preparados: CAP={formulario_pop.get('codigo_cap')}, Macro={formulario_pop.get('macroprocesso')}, Atividade={formulario_pop.get('atividade')}")
        logger.info(f"[DEBUG] dados_extraidos.operadores = {dados_extraidos.get('operadores')}")
        logger.debug(f"[RETORNO FINAL] tipo_interface={tipo_interface}, dados_interface presente={dados_interface is not None}, resposta={_short(resposta)}")

        # 🔍 DEBUG CRÍTICO: Log completo antes de retornar
        logger.info(f"[PROCESSAR] ===== RETORNO FINAL =====")
        logger.info(f"[PROCESSAR] novo_sm.estado = {novo_sm.estado}")
        logger.info(f"[PROCESSAR] tipo_interface = {tipo_interface}")
        logger.info(f"[PROCESSAR] dados_interface tem {len(dados_interface) if dados_interface else 0} chaves")
        logger.info(f"[PROCESSAR] resposta = {_short(resposta)}")
        logger.info(f"[PROCESSAR] ===============================")

        resultado = self.criar_resposta(
            resposta=resposta,
            novo_estado=novo_sm.to_dict(),
            progresso=progresso,
            sugerir_contexto=sugerir_contexto,
            metadados=metadados_extra,
            tipo_interface=tipo_interface,
            dados_interface=dados_interface,
            formulario_pop=formulario_pop,  # ✅ FASE 2: Novo nome
            dados_extraidos=dados_extraidos  # ✅ FIX: Compatibilidade com frontend OLD
        )

        # Flag para frontend: conversa completa → disparar geração de PDF
        if novo_sm.concluido:
            resultado['conversa_completa'] = True

        return resultado

    # ========================================================================
    # HELPERS
    # ========================================================================

    def _obter_contexto_area(self, sm: POPStateMachine) -> tuple[str, str]:
        """Retorna (area_nome, area_codigo) baseado na seleção do usuário."""
        if sm.subarea_selecionada:
            area_nome = sm.subarea_selecionada.get('nome_completo', sm.subarea_selecionada.get('nome', ''))
            area_codigo = sm.subarea_selecionada.get('codigo', '')
        elif sm.area_selecionada:
            area_nome = sm.area_selecionada.get('nome', '')
            area_codigo = sm.area_selecionada.get('codigo', '')
        else:
            area_nome = 'DECIPEX'
            area_codigo = 'DECIPEX'
        return area_nome, area_codigo

    def _parse_json_seguro(self, mensagem: str) -> dict | list | None:
        """Parse JSON de forma segura, retornando None se falhar."""
        try:
            return json.loads(mensagem)
        except (json.JSONDecodeError, TypeError):
            return None

    def _parsear_fluxo_json(self, dados_json, chave_lista: str, chave_outros: str, formato_entrada: bool = True) -> list | None:
        """Extrai lista de fluxos de JSON estruturado (entrada ou saída).

        ⚠️ IMPORTANTE: Rejeita listas simples de strings (como operadores).
        Aceita apenas:
        - dict com chaves origens_selecionadas/destinos_selecionados
        - None (para fallback a texto)
        """
        # ✅ FIX: Rejeitar listas simples (ex: ["Coordenador-Geral"] de operadores)
        # Fluxos válidos vêm como dict com chaves específicas
        if not isinstance(dados_json, dict):
            # Se for lista simples de strings, REJEITAR (retorna None para usar fallback)
            if isinstance(dados_json, list):
                # Verificar se parece com dados de operadores (lista de strings simples)
                if all(isinstance(item, str) for item in dados_json):
                    logger.warning(f"[_parsear_fluxo_json] Rejeitando lista simples de strings: {dados_json[:3]}...")
                    return None  # Força uso do fallback (texto)
            return None

        fluxos = []
        for item in dados_json.get(chave_lista, []):
            if isinstance(item, dict):
                tipo = item.get('tipo', '')
                espec = item.get('especificacao', '')
                if espec:
                    fluxos.append(f"{tipo}: {espec}" if formato_entrada else f"{tipo} ({espec})")
                else:
                    fluxos.append(tipo)
            else:
                fluxos.append(str(item))

        if dados_json.get(chave_outros):
            fluxos.append(dados_json[chave_outros])

        return fluxos

    def _processar_resposta_rag(self, descricao: str, sm: POPStateMachine) -> tuple:
        """Processa descrição do usuário na Camada 4 RAG e retorna interface ou erro."""
        hierarquia_herdada = {
            'macroprocesso': sm.macro_selecionado,
            'processo': sm.processo_selecionado,
            'subprocesso': sm.subprocesso_selecionado
        }
        area_codigo = sm.subarea_selecionada['codigo'] if sm.subarea_selecionada else sm.area_selecionada['codigo']
        autor_dados = {
            'nome': sm.nome_usuario or "Usuário",
            'cpf': "00000000000",
            'area_codigo': area_codigo,
            'area_nome': sm.area_selecionada['nome']
        }

        pipeline = self._pipeline
        resultado = pipeline._camada4_processar_resposta(
            descricao_atividade=descricao,
            hierarquia_herdada=hierarquia_herdada,
            area_codigo=area_codigo,
            autor_dados=autor_dados
        )

        if resultado.get('sucesso'):
            ativ = resultado['atividade']
            sm.macro_selecionado = ativ['macroprocesso']
            sm.processo_selecionado = ativ['processo']
            sm.subprocesso_selecionado = ativ['subprocesso']
            sm.atividade_selecionada = ativ['atividade']
            sm.codigo_cap = resultado.get('cap', 'PROVISORIO')

            # Incluir área na atividade para o frontend
            area_nome = sm.area_selecionada.get('nome', '') if sm.area_selecionada else ''
            ativ['area'] = area_nome

            metadados_extra = {
                'interface': {
                    'tipo': 'sugestao_atividade',
                    'dados': {
                        'atividade': ativ,
                        'cap': resultado.get('cap'),
                        'origem': 'rag_nova_atividade',
                        'score': 1.0,
                        'pode_editar': True,
                        'tipo_cap': 'oficial_gerado_rag',
                        'mensagem': resultado.get('mensagem', '')
                    }
                }
            }
            return "", sm, metadados_extra
        else:
            return "Desculpe, ocorreu um erro ao criar a atividade. Tente novamente.", sm, None

    def _sugerir_entrega_esperada(self, sm: POPStateMachine, descricao_usuario: str = None) -> str | None:
        """
        Sugere entrega esperada usando Helena Ajuda Inteligente.

        Args:
            sm: State machine com dados da arquitetura selecionada
            descricao_usuario: Descrição original do usuário (opcional)

        Returns:
            Sugestão de entrega esperada ou None se falhar
        """
        try:
            from processos.domain.helena_mapeamento.helena_ajuda_inteligente import analisar_atividade_com_helena

            area_nome, area_codigo = self._obter_contexto_area(sm)

            contexto = {
                'area': area_nome,
                'area_codigo': area_codigo,
                'macroprocesso': sm.macro_selecionado,
                'processo': sm.processo_selecionado,
                'subprocesso': sm.subprocesso_selecionado,
                'atividade': sm.atividade_selecionada
            }

            descricao = descricao_usuario or sm.dados_coletados.get('descricao_original') or sm.atividade_selecionada

            resultado = analisar_atividade_com_helena(
                descricao_usuario=descricao,
                nivel_atual='resultado_final',
                contexto_ja_selecionado=contexto
            )

            if resultado.get('sucesso') and 'resultado_final' in resultado.get('sugestao', {}):
                sugestao = resultado['sugestao']['resultado_final']
                logger.info(f"[ENTREGA] Sugestao IA: {sugestao}")
                return sugestao

        except Exception as e:
            logger.error(f"[ENTREGA] Erro ao sugerir entrega: {e}")

        return None

    # ========================================================================
    # PROCESSADORES DE ESTADO
    # ========================================================================

    def _processar_nome_usuario(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Processa coleta do nome do usuário (SOLUÇÃO DO OLD - sem duplicação)

        Detecta se mensagem é um nome candidato ou precisa pedir nome

        ✅ FIX DUPLICAÇÃO BOAS-VINDAS:
        - Frontend já mostra mensagem hardcoded
        - Backend apenas processa o nome, sem repetir introdução
        """
        msg_limpa = mensagem.strip()
        palavras = msg_limpa.split()

        # Saudações comuns
        saudacoes = ["oi", "olá", "ola", "hey", "e aí", "e ai", "oie"]
        confirmacoes = ["sim", "s", "não", "nao", "n"]

        # Verificar se é nome candidato
        apenas_uma_palavra = len(palavras) == 1
        palavra = palavras[0] if palavras else ""
        eh_saudacao = palavra.lower() in saudacoes
        tem_pontuacao_frase = bool(re.search(r"[!?.,]", msg_limpa)) or len(palavras) > 1
        eh_nome_candidato = (
            apenas_uma_palavra and
            len(palavra) >= 2 and
            palavra.isalpha() and
            not eh_saudacao and
            not tem_pontuacao_frase and
            palavra.lower() not in confirmacoes
        )

        if eh_nome_candidato:
            # É um nome válido - aceitar e seguir direto para explicação
            sm.nome_usuario = palavra.capitalize()
            sm.estado = EstadoPOP.ESCOLHA_TIPO_EXPLICACAO

            sm.tipo_interface = 'confirmacao_dupla'
            sm.dados_interface = {
                'botao_confirmar': 'Continuar',
                'botao_editar': 'Pular introdução',
                'valor_confirmar': 'objetiva',
                'valor_editar': 'pular_intro'
            }

            resposta = (
                f"Olá, {sm.nome_usuario}.\n\n"
                f"Neste chat, vou te guiar passo a passo para preencher um "
                f"Procedimento Operacional Padrão (POP).\n\n"
                f"A seguir, explico rapidamente como o processo funciona.\n"
                f"Se preferir, você pode pular esta introdução e iniciar o mapeamento agora.\n\n"
                f"*Seu nome aparece no cabeçalho. Se estiver incorreto, "
                f"você pode editá-lo a qualquer momento.*"
            )
            return resposta, sm

        # ✅ FIX: Se mensagem não é nome válido, apenas pedir clarificação
        # NUNCA repetir boas-vindas completas (frontend já mostrou)
        resposta = "Desculpe, não entendi. Pode me dizer seu nome? (Digite apenas o primeiro nome)"
        return resposta, sm

    def _gerar_explicacao_longa_com_delay(self) -> str:
        """Gera texto institucional com detalhes do processo."""
        return (
            "**Detalhes do processo**\n\n"
            "Este processo serve para registrar uma atividade real de trabalho "
            "e gerar um Procedimento Operacional Padrão (POP) padronizado.\n\n"
            "**O que você vai fazer**\n\n"
            "- Identificar a área e a atividade executada\n"
            "- Informar responsáveis, sistemas utilizados e base normativa\n"
            "- Descrever as etapas do trabalho, passo a passo\n"
            "- Revisar as informações e gerar o POP\n\n"
            "**O que o sistema faz por você**\n\n"
            "- Sugere classificações e nomes de processo\n"
            "- Preenche automaticamente o formulário ao lado\n"
            "- Salva seu progresso durante o preenchimento\n"
            "- Gera o POP em formato final para uso e compartilhamento\n\n"
            "**Tempo estimado**\n\n"
            "O preenchimento leva, em média, 15 a 30 minutos, "
            "dependendo da complexidade da atividade.\n\n"
            "**O que pode ser alterado depois**\n\n"
            "- Nome da atividade\n"
            "- Etapas do processo\n"
            "- Responsáveis\n"
            "- Textos descritivos\n\n"
            "**Importante saber**\n\n"
            "- Nada é publicado automaticamente\n"
            "- Você pode sair e continuar depois\n"
            "- Nenhuma informação é perdida sem confirmação"
        )

    # REMOVIDO: _processar_confirma_nome — nome é aceito direto em _processar_nome_usuario

    def _processar_escolha_tipo_explicacao(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa escolha entre explicação curta ou longa"""
        msg_lower = mensagem.lower().strip()

        # Pular introdução — ir direto para áreas organizacionais
        if msg_lower == 'pular_intro':
            sm.estado = EstadoPOP.AREA_DECIPEX

            resposta = (
                f"{sm.nome_usuario}, vamos direto ao ponto.\n\n"
                f"Para começar, selecione a área organizacional onde a atividade é executada."
            )
            return resposta, sm

        # Explicação detalhada/longa
        if self._detectar_intencao(msg_lower, 'detalhes'):
            sm.estado = EstadoPOP.EXPLICACAO_LONGA
            resposta = self._gerar_explicacao_longa_com_delay()
            sm.tipo_interface = 'confirmacao_dupla'
            sm.dados_interface = {
                'botao_confirmar': 'Continuar',
                'botao_editar': 'Tenho dúvidas',
                'valor_confirmar': 'sim',
                'valor_editar': 'duvidas'
            }
            return resposta, sm

        # Explicação objetiva/curta (fluxo atual)
        elif self._detectar_intencao(msg_lower, 'objetiva'):
            sm.estado = EstadoPOP.EXPLICACAO
            sm.tipo_interface = 'confirmacao_explicacao'
            sm.dados_interface = {
                'botoes': [
                    {'label': 'Continuar', 'valor': 'sim', 'tipo': 'primary'},
                    {'label': 'Ver detalhes do mapeamento', 'valor': 'detalhes', 'tipo': 'secondary'}
                ]
            }
            resposta = (
                f"Vou te explicar como vai funcionar.\n\n"
                f"Vamos conversar no chat e, com base nas informações e no que você descrever sobre "
                f"a atividade que executa, o sistema preenche automaticamente o Procedimento "
                f"Operacional Padrão (POP) ao lado. Você não precisa editar nada no POP — eu farei isso.\n\n"
                f"Ao final, o documento fica pronto para revisão e você poderá alterar qualquer campo."
            )
            return resposta, sm

        # Não entendeu - re-renderiza interface correta
        else:
            # ✅ FIX: Re-setar interface correta para este estado
            sm.tipo_interface = 'confirmacao_dupla'
            sm.dados_interface = {
                'botao_confirmar': '⚡ Explicação objetiva',
                'botao_editar': '📘 Explicação detalhada',
                'valor_confirmar': 'objetiva',
                'valor_editar': 'detalhada'
            }
            resposta = (
                f"Desculpe, não entendi. Por favor, escolha:\n\n"
                f"📘 **Explicação detalhada** - para entender tudo em detalhes\n"
                f"⚡ **Explicação objetiva** - para ir direto ao ponto"
            )
            return resposta, sm

    def _processar_explicacao_longa(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa resposta após explicação longa"""
        msg_lower = mensagem.lower().strip()

        # Entendeu tudo - vai para PEDIDO DE COMPROMISSO
        if self._detectar_intencao(msg_lower, 'confirmacao'):
            sm.estado = EstadoPOP.PEDIDO_COMPROMISSO

            resposta = (
                f"{sm.nome_usuario}, antes de continuar, é importante esclarecer alguns pontos.\n\n"
                f"• É comum surgirem dúvidas durante o mapeamento. Ao final do processo, será possível revisar e ajustar todas as informações registradas, inclusive com apoio de outras pessoas da equipe.\n\n"
                f"• O registro cuidadoso das atividades contribui para reduzir retrabalho nas etapas seguintes.\n\n"
                f"Quando estiver pronto, podemos prosseguir."
            )
            return resposta, sm

        # Ainda tem dúvidas - ativar Helena Mapeamento internamente
        elif self._detectar_intencao(msg_lower, 'negacao') or self._detectar_intencao(msg_lower, 'duvidas'):
            sm.estado = EstadoPOP.DUVIDAS_EXPLICACAO
            # Flag para indicar que está em modo dúvidas (Helena Mapeamento ativo)
            sm.em_modo_duvidas = True
            sm.contexto_duvidas = "explicacao_pop"  # Contexto: está tirando dúvidas sobre explicação do POP

            resposta = (
                f"Sem problemas, {sm.nome_usuario}! 😊\n\n"
                f"Pode me fazer qualquer pergunta sobre o processo. "
                f"Estou aqui para te ajudar a entender melhor!"
            )
            return resposta, sm

        # Fallback
        else:
            resposta = (
                f"Por favor, me diga:\n"
                f"🔹 **Continuar** - para seguir\n"
                f"🔹 **Dúvidas** - para eu te explicar melhor"
            )
            return resposta, sm

    def _processar_duvidas_explicacao(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Processa dúvidas sobre a explicação delegando para Helena Mapeamento.

        Fluxo:
        1. Instancia Helena Mapeamento
        2. Delega mensagem para Helena Mapeamento
        3. Helena Mapeamento responde livremente com DOIS botões
        4. "Ok, já entendi" → vai para PEDIDO_COMPROMISSO
        5. "Tenho mais uma pergunta" → continua com Helena Mapeamento
        """
        msg_lower = mensagem.lower().strip()

        # 🔥 Tratar cliques nos botões da interface anterior
        if msg_lower in ['ok_entendi', 'ok', 'entendi', 'ja entendi', 'já entendi']:
            # Usuário clicou em "Ok, já entendi" → sair do modo dúvidas
            sm.em_modo_duvidas = False
            sm.estado = EstadoPOP.PEDIDO_COMPROMISSO

            resposta = (
                f"{sm.nome_usuario}, antes de continuar, é importante esclarecer alguns pontos.\n\n"
                f"• É comum surgirem dúvidas durante o mapeamento. Ao final do processo, será possível revisar e ajustar todas as informações registradas, inclusive com apoio de outras pessoas da equipe.\n\n"
                f"• O registro cuidadoso das atividades contribui para reduzir retrabalho nas etapas seguintes.\n\n"
                f"Quando estiver pronto, podemos prosseguir."
            )

            sm.tipo_interface = 'confirmacao_dupla'
            sm.dados_interface = {
                'botao_confirmar': 'Clique aqui pra fechar nosso acordo',
                'botao_editar': 'Tenho mais dúvidas',
                'valor_confirmar': 'sim',
                'valor_editar': 'duvidas'
            }
            return resposta, sm

        elif msg_lower in ['mais_pergunta', 'mais', 'pergunta', 'tenho mais']:
            # Usuário clicou em "Tenho mais uma pergunta" → solicitar a pergunta
            sm.tipo_interface = None
            sm.dados_interface = {}

            resposta = f"Claro, {sm.nome_usuario}! Pode fazer sua pergunta que vou te ajudar. 😊"
            return resposta, sm

        from processos.domain.helena_mapeamento.helena_mapeamento import HelenaMapeamento

        # Instanciar Helena Mapeamento se ainda não existe
        helena_map = HelenaMapeamento()

        # Inicializar estado de Helena Mapeamento se necessário
        if sm.estado_helena_mapeamento is None:
            sm.estado_helena_mapeamento = helena_map.inicializar_estado()
            # Contexto: usuário está tirando dúvidas sobre explicação do POP
            sm.estado_helena_mapeamento['contexto'] = sm.contexto_duvidas
            sm.estado_helena_mapeamento['nome_usuario'] = sm.nome_usuario

        # Delegar processamento para Helena Mapeamento
        resultado = helena_map.processar(mensagem, sm.estado_helena_mapeamento)

        # Atualizar estado de Helena Mapeamento
        sm.estado_helena_mapeamento = resultado['novo_estado']

        # 🔥 SEMPRE retornar interface de confirmação dupla após resposta da Helena Mapeamento
        resposta = resultado['resposta']

        sm.tipo_interface = 'confirmacao_dupla'
        sm.dados_interface = {
            'botao_confirmar': 'Continuar',
            'botao_editar': 'Tenho mais uma pergunta',
            'valor_confirmar': 'ok_entendi',
            'valor_editar': 'mais_pergunta'
        }

        return resposta, sm

    def _processar_explicacao(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Confirma que está tudo claro e pronto para começar (modo curto)"""
        msg_lower = mensagem.lower().strip()

        # Limpar interface após resposta
        sm.tipo_interface = None
        sm.dados_interface = {}

        respostas_positivas = ['sim', 's', 'pode', 'ok', 'claro', 'vamos', 'yes', 'uhum', 'aham', 'beleza', 'entendi', 'bora', 'vamo', 'pronta', 'pronto']

        # Se escolheu "Sim" - vai para PEDIDO DE COMPROMISSO
        if msg_lower in respostas_positivas:
            sm.estado = EstadoPOP.PEDIDO_COMPROMISSO

            resposta = (
                f"{sm.nome_usuario}, antes de continuar, é importante esclarecer alguns pontos.\n\n"
                f"• É comum surgirem dúvidas durante o mapeamento. Ao final do processo, será possível revisar e ajustar todas as informações registradas, inclusive com apoio de outras pessoas da equipe.\n\n"
                f"• O registro cuidadoso das atividades contribui para reduzir retrabalho nas etapas seguintes.\n\n"
                f"Quando estiver pronto, podemos prosseguir."
            )
        # Se escolheu "Não, quero mais detalhes" - vai para EXPLICACAO_LONGA
        elif 'detalhes' in msg_lower or 'detalhe' in msg_lower or ('não' in msg_lower or 'nao' in msg_lower):
            sm.estado = EstadoPOP.EXPLICACAO_LONGA
            resposta = self._gerar_explicacao_longa_com_delay()
            sm.tipo_interface = 'confirmacao_dupla'
            sm.dados_interface = {
                'botao_confirmar': 'Continuar',
                'botao_editar': 'Tenho dúvidas',
                'valor_confirmar': 'sim',
                'valor_editar': 'duvidas'
            }
        else:
            resposta = f"Tudo bem! Só posso seguir quando você me disser 'sim', {sm.nome_usuario}. Quando quiser continuar, é só digitar."

        return resposta, sm

    def _processar_pedido_compromisso(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Processa pedido de compromisso antes de começar o mapeamento

        Gamificação: Badge "Cartógrafo de Processos" ao aceitar o compromisso
        """
        msg_lower = mensagem.lower().strip()

        # 🔥 Tratar clique no botão "Tenho mais dúvidas"
        if msg_lower in ['duvidas', 'dúvidas', 'mais duvidas', 'mais dúvidas', 'tenho duvidas', 'tenho dúvidas']:
            # Voltar para modo dúvidas
            sm.em_modo_duvidas = True
            sm.estado = EstadoPOP.DUVIDAS_EXPLICACAO
            sm.contexto_duvidas = 'compromisso'

            sm.tipo_interface = None
            sm.dados_interface = {}

            resposta = f"Sem problemas, {sm.nome_usuario}! Pode fazer sua pergunta que vou te ajudar. 😊"
            return resposta, sm

        # Aceita qualquer resposta positiva (ambas opções levam para o mesmo lugar)
        if self._detectar_intencao(msg_lower, 'confirmacao'):
            sm.estado = EstadoPOP.AREA_DECIPEX

            resposta = (
                f"{sm.nome_usuario}, o registro do processo foi iniciado.\n\n"
                f"A partir deste ponto, o mapeamento da atividade será conduzido de forma estruturada.\n\n"
                f"O detalhamento das informações ao longo do processo contribui para reduzir dúvidas futuras e retrabalho, beneficiando a equipe e a gestão."
            )
            return resposta, sm
        else:
            # Se não entendeu, repete a pergunta
            resposta = (
                f"Desculpe, não entendi.\n\n"
                f"Quando estiver pronto, podemos prosseguir."
            )
            return resposta, sm

    def _processar_area_decipex(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa seleção da área DECIPEX"""
        try:
            numero = int(mensagem.strip())
            if numero in self.AREAS_DECIPEX:
                sm.area_selecionada = self.AREAS_DECIPEX[numero]

                # Verificar se a área tem subáreas
                if sm.area_selecionada.get('tem_subareas', False):
                    sm.estado = EstadoPOP.SUBAREA_DECIPEX

                    # Buscar descrição personalizada da área
                    codigo_area = sm.area_selecionada['codigo']
                    descricao_area = self.DESCRICOES_AREAS.get(codigo_area, "")

                    resposta = (
                        f"Ótimo, {sm.nome_usuario}!\n"
                        f"Você faz parte da **{sm.area_selecionada['nome']}**, {descricao_area}"
                    )

                else:
                    # Área sem subáreas, segue para arquitetura
                    sm.estado = EstadoPOP.ARQUITETURA

                    # Buscar descrição personalizada da área
                    codigo_area = sm.area_selecionada['codigo']
                    descricao_area = self.DESCRICOES_AREAS.get(codigo_area, "")

                    resposta = (
                        f"Ótimo, {sm.nome_usuario}!\n"
                        f"Você faz parte da **{sm.area_selecionada['nome']}**, {descricao_area}\n\n"
                        f"✍️ Agora me conte: qual sua atividade principal e o que você entrega ao finalizar?\n\n"
                        f"Responda como se alguém te perguntasse \"você trabalha com o que?\"\n\n"
                        f"💡 Pode ser uma ou duas frases simples!"
                    )

                    # ✅ FLAG: Próxima resposta será descrição inicial de atividade (para quadro roxo no frontend)
                    metadados_extra = {
                        'aguardando_descricao_inicial': True
                    }

                    return resposta, sm, metadados_extra
            else:
                resposta = (
                    "Número inválido. Por favor, digite um número de 1 a 8 correspondente "
                    "a uma das áreas listadas acima."
                )
        except ValueError:
            resposta = (
                "Por favor, digite apenas o número da área (de 1 a 8)."
            )

        return resposta, sm

    def _processar_subarea_decipex(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa seleção da subárea (ex: DIGEP-RO, DIGEP-RR, DIGEP-AP)"""
        try:
            numero = int(mensagem.strip())
            subareas = sm.area_selecionada.get('subareas', [])

            if 1 <= numero <= len(subareas):
                sm.subarea_selecionada = subareas[numero - 1]
                sm.estado = EstadoPOP.ARQUITETURA

                resposta = (
                    f"Perfeito! Você trabalha na **{sm.subarea_selecionada['nome_completo']}**! 🌿\n\n"
                    f"✍️ Agora me conte: qual sua atividade principal e o que você entrega ao finalizar?\n\n"
                    f"Responda como se alguém te perguntasse \"você trabalha com o que?\"\n\n"
                    f"💡 Pode ser uma ou duas frases simples!"
                )

                # ✅ FLAG: Próxima resposta será descrição inicial de atividade (para quadro roxo no frontend)
                metadados_extra = {
                    'aguardando_descricao_inicial': True
                }

                return resposta, sm, metadados_extra
            else:
                resposta = (
                    f"Número inválido. Por favor, digite um número de 1 a {len(subareas)} correspondente "
                    "a uma das opções listadas acima."
                )
        except ValueError:
            resposta = (
                f"Por favor, digite apenas o número (1 a {len(sm.area_selecionada.get('subareas', []))})."
            )

        return resposta, sm

    def _processar_arquitetura(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Processa navegação na arquitetura DECIPEX usando sistema de busca em 4 camadas:

        CAMADA 1: Match Exato/Fuzzy no CSV
        CAMADA 2: Busca Semântica
        CAMADA 3: Seleção Manual Hierárquica
        CAMADA 4: RAG (criação de nova atividade)
        """
        # ================================================================
        # DETECTAR SE É RESPOSTA DE INTERFACE (JSON)
        # ================================================================
        dados_resposta = self._parse_json_seguro(mensagem)
        if dados_resposta:
            acao = dados_resposta.get('acao')

            # Se o usuário clicou "Não encontrei" na Camada 3
            if acao == 'nao_encontrei':
                logger.info("[HELENA POP] Usuário clicou 'Não encontrei' - acionando Camada 4 (RAG)")

                # Preparar dados do autor
                area_codigo = sm.subarea_selecionada['codigo'] if sm.subarea_selecionada else sm.area_selecionada['codigo']
                autor_dados = {
                    'nome': sm.nome_usuario or "Usuário",
                    'cpf': "00000000000",
                    'area_codigo': area_codigo,
                    'area_nome': sm.area_selecionada['nome']
                }

                pipeline = self._pipeline
                hierarquia_selecionada = dados_resposta.get('selecao')

                # Chamar Camada 4 com hierarquia selecionada
                resultado = pipeline._camada4_fallback_rag(
                    descricao_usuario='',  # Não usado nesta etapa
                    area_codigo=area_codigo,
                    contexto=None,
                    autor_dados=autor_dados,
                    hierarquia_selecionada=hierarquia_selecionada
                )

                # Retornar interface de pergunta
                if resultado.get('origem') == 'rag_aguardando_descricao':
                    # Salvar hierarquia herdada no estado para usar na próxima resposta
                    hierarquia_herdada = resultado.get('hierarquia_herdada')
                    sm.macro_selecionado = hierarquia_herdada.get('macroprocesso')
                    sm.processo_selecionado = hierarquia_herdada.get('processo')
                    sm.subprocesso_selecionado = hierarquia_herdada.get('subprocesso')

                    # Incluir área na hierarquia para o frontend
                    area_nome = sm.area_selecionada.get('nome', '') if sm.area_selecionada else ''
                    hierarquia_herdada['area'] = area_nome

                    # Marcar que estamos aguardando descrição RAG
                    sm.dados_coletados['aguardando_descricao_rag'] = True

                    metadados_extra = {
                        'interface': {
                            'tipo': 'rag_pergunta_atividade',
                            'dados': {
                                'mensagem': resultado.get('mensagem'),
                                'hierarquia_herdada': hierarquia_herdada,
                                'instrucao': resultado.get('instrucao_frontend')
                            }
                        }
                    }
                    return "", sm, metadados_extra

            # Se o usuário enviou descrição na Camada 4
            elif acao == 'enviar_descricao':
                logger.info("[HELENA POP] Processando descrição da Camada 4 (RAG)")
                descricao = dados_resposta.get('descricao')
                resposta, sm, metadados = self._processar_resposta_rag(descricao, sm)
                if metadados:
                    return resposta, sm, metadados
                return resposta, sm

            # Se o usuário confirmou uma seleção da Camada 3
            elif acao == 'confirmar':
                selecao = dados_resposta.get('selecao')
                sm.macro_selecionado = selecao['macroprocesso']
                sm.processo_selecionado = selecao['processo']
                sm.subprocesso_selecionado = selecao['subprocesso']
                sm.atividade_selecionada = selecao['atividade']
                sm.codigo_cap = selecao.get('cap', 'A definir')
                sm.estado = EstadoPOP.CONFIRMACAO_ARQUITETURA

                resposta = (
                    f"✅ Perfeito! Você selecionou:\n\n"
                    f"📋 **Macroprocesso:** {sm.macro_selecionado}\n"
                    f"📋 **Processo:** {sm.processo_selecionado}\n"
                    f"📋 **Subprocesso:** {sm.subprocesso_selecionado}\n"
                    f"📋 **Atividade:** {sm.atividade_selecionada}\n"
                    f"🔢 **Código CAP:** {sm.codigo_cap}\n\n"
                    f"Está correto?"
                )
                return resposta, sm

        # ================================================================
        # TRATAR AÇÃO "selecionar_manual" (botão da interface sugestao_atividade)
        # ================================================================
        if mensagem.strip().lower() in ['selecionar_manual', 'selecionar_manualmente']:
            logger.info("[HELENA POP] Usuário clicou 'Minha atividade não é essa, vou selecionar' - acionando Camada 3 (Dropdown)")

            # Preparar pipeline
            area_codigo = sm.subarea_selecionada['codigo'] if sm.subarea_selecionada else sm.area_selecionada['codigo']
            pipeline = self._pipeline

            # Chamar Camada 3: Seleção Manual Hierárquica (passando area_codigo para gerar CAP correto)
            hierarquia = pipeline._preparar_hierarquia_completa(area_codigo=area_codigo)

            if not hierarquia:
                logger.error("[HELENA POP] Erro ao carregar hierarquia para seleção manual")
                return "Desculpe, ocorreu um erro ao carregar as opções. Tente novamente.", sm

            # Retornar interface de seleção hierárquica
            metadados_extra = {
                'interface': {
                    'tipo': 'selecao_manual_hierarquica',
                    'dados': {
                        'hierarquia': hierarquia,
                        'acoes_usuario': ['confirmar', 'nao_encontrei'],
                        'mensagem': 'Por favor, selecione sua atividade navegando pela estrutura organizacional:',
                        'tipo_cap': 'oficial'
                    }
                }
            }

            resposta = None  # Modo interface: mensagem textual ausente por design
            return resposta, sm, metadados_extra

        # ================================================================
        # TRATAR "prefiro_digitar" (botão após RAG falhar)
        # ================================================================
        if mensagem.strip().lower() == 'prefiro_digitar':
            logger.info("[HELENA POP] Usuário rejeitou sugestão RAG - pedindo digitação manual final")

            nome = sm.nome_usuario or "você"

            # Retornar interface de texto livre para digitação final
            metadados_extra = {
                'interface': {
                    'tipo': 'texto_livre',
                    'dados': {
                        'placeholder': 'Ex: Analiso processos de aposentadoria e emito parecer final'
                    }
                }
            }

            resposta = (
                f"Sem problema, {nome}! Que pena que não consegui te ajudar 😢\n\n"
                f"Me diz então qual atividade, é bom que eu também aprendo!"
            )

            # Marcar que a próxima digitação deve ir direto pro POP sem buscar
            sm.dados_coletados['pular_busca'] = True

            return resposta, sm, metadados_extra

        # ================================================================
        # TRATAR "concordar" (botão "Você acertou, Helena!" da sugestão IA)
        # ================================================================
        msg_lower = mensagem.strip().lower()
        if msg_lower in ['concordar', 'confirmar', 'sim', 'concordo']:
            # Usuário confirmou a sugestão da IA (Camada 1 ou 2)
            # Ir direto para ENTREGA_ESPERADA (usuário já confirmou na interface de sugestão)
            logger.info(f"[HELENA POP] Usuário confirmou sugestão - pulando para ENTREGA_ESPERADA")

            # Sugerir entrega esperada usando helper
            sugestao_entrega = self._sugerir_entrega_esperada(sm)
            if sugestao_entrega:
                sm.dados_coletados['entrega_esperada'] = sugestao_entrega
                sm.dados_coletados['entrega_sugerida_temp'] = sugestao_entrega

            # Ir para ENTREGA_ESPERADA
            sm.estado = EstadoPOP.ENTREGA_ESPERADA

            if sugestao_entrega:

                # Enviar interface com sugestão e botões
                metadados_extra = {
                    'interface': {
                        'tipo': 'sugestao_entrega_esperada',
                        'dados': {
                            'sugestao': sugestao_entrega,
                            'acoes_usuario': ['concordar', 'editar_manual']
                        }
                    }
                }

                resposta = (
                    f"Perfeito! Agora vamos definir a **entrega esperada** dessa atividade. 📋"
                )
                return resposta, sm, metadados_extra
            else:
                # Se não conseguiu sugerir, pedir entrada manual
                metadados_extra = {
                    'interface': {
                        'tipo': 'texto_livre',
                        'dados': {
                            'placeholder': 'Ex: Processo analisado e parecer emitido'
                        }
                    }
                }

                resposta = (
                    f"Perfeito! Agora me conta: **qual é o resultado final** dessa atividade?\n\n"
                    f"O que fica pronto quando você termina?"
                )
                return resposta, sm, metadados_extra

        descricao_usuario = mensagem.strip()

        # Validação: mínimo 10 caracteres (APENAS para descrições de atividade nova)
        if len(descricao_usuario) < 10:
            resposta = (
                "Por favor, descreva sua atividade com mais detalhes (mínimo 10 caracteres).\n\n"
                "Exemplo: 'Analiso requerimentos de auxílio saúde de aposentados'"
            )
            return resposta, sm

        # Obter dados do autor (para rastreabilidade)
        # Se há subárea selecionada, usar ela; senão, usar área principal
        if sm.subarea_selecionada:
            area_nome = sm.subarea_selecionada['nome_completo']
            area_codigo = sm.subarea_selecionada['codigo']
        else:
            area_nome = sm.area_selecionada['nome']
            area_codigo = sm.area_selecionada['codigo']

        autor_nome = sm.nome_usuario or "Usuário"
        autor_cpf = "00000000000"  # TODO: Obter CPF real do usuário autenticado

        logger.info(f"[GOVERNANÇA] Iniciando busca para: '{descricao_usuario}' | Autor: {autor_nome} | Área: {area_codigo}")

        # ============================================================================
        # VERIFICAR SE DEVE PULAR BUSCA (usuário rejeitou RAG e digitou manualmente)
        # ============================================================================
        if sm.dados_coletados.get('pular_busca'):
            logger.info("[HELENA POP] PULANDO BUSCA - Usuário digitou atividade final após rejeitar RAG")

            # Salvar atividade digitada (usando hierarquia já definida pelo RAG ou dropdown)
            sm.atividade_selecionada = descricao_usuario
            sm.dados_coletados['descricao_original'] = descricao_usuario

            # Gerar código CAP se ainda não tiver
            if not sm.codigo_cap or sm.codigo_cap == 'PROVISORIO':
                sm.codigo_cap = self._gerar_codigo_processo(sm)

            # Limpar flag
            sm.dados_coletados['pular_busca'] = False

            # Ir para ENTREGA_ESPERADA
            sm.estado = EstadoPOP.ENTREGA_ESPERADA

            # Sugerir entrega esperada usando helper
            sugestao_entrega = self._sugerir_entrega_esperada(sm, descricao_usuario)
            if sugestao_entrega:
                sm.dados_coletados['entrega_esperada'] = sugestao_entrega
                sm.dados_coletados['entrega_sugerida_temp'] = sugestao_entrega

            if sugestao_entrega:

                metadados_extra = {
                    'interface': {
                        'tipo': 'sugestao_entrega_esperada',
                        'dados': {
                            'sugestao': sugestao_entrega,
                            'acoes_usuario': ['concordar', 'editar_manual']
                        }
                    }
                }

                resposta = (
                    f"Perfeito! Agora vamos definir a **entrega esperada** dessa atividade. 📋"
                )
                return resposta, sm, metadados_extra
            else:
                metadados_extra = {
                    'interface': {
                        'tipo': 'texto_livre',
                        'dados': {
                            'placeholder': 'Ex: Processo analisado e parecer emitido'
                        }
                    }
                }

                resposta = (
                    f"Perfeito! Agora me conta: **qual é o resultado final** dessa atividade?\n\n"
                    f"O que fica pronto quando você termina?"
                )
                return resposta, sm, metadados_extra

        # Detectar se estamos aguardando resposta da Camada 4 RAG
        if sm.dados_coletados.get('aguardando_descricao_rag', False):
            logger.info("[HELENA POP] Usuário respondeu à pergunta RAG")
            sm.dados_coletados['aguardando_descricao_rag'] = False
            resposta, sm, metadados = self._processar_resposta_rag(mensagem, sm)
            if metadados:
                return resposta, sm, metadados
            return resposta, sm

        # ============================================================================
        # PIPELINE DE BUSCA EM 4 CAMADAS
        # ============================================================================
        logger.info("="*80)
        logger.info("[PIPELINE] Usando NOVO PIPELINE de busca em 4 camadas (v4.0)")
        logger.info("="*80)

        try:
            # Usar pipeline com lazy loading
            pipeline = self._pipeline

            # Preparar dados do autor para rastreabilidade
            autor_dados = {
                'nome': autor_nome,
                'cpf': autor_cpf,
                'area_codigo': area_codigo,
                'area_nome': area_nome
            }

            # Executar pipeline
            resultado = pipeline.buscar_atividade(
                descricao_usuario=descricao_usuario,
                area_codigo=area_codigo,
                contexto=None,  # TODO: Adicionar contexto se necessário
                autor_dados=autor_dados
            )

            logger.info(f"[PIPELINE] Resultado: origem={resultado.get('origem')}, score={resultado.get('score', 0):.3f}")

            # ========================================================================
            # PROCESSAR RESULTADO DO PIPELINE
            # ========================================================================

            # Seleção manual hierárquica (Camada 3)
            if resultado.get('origem') == 'selecao_manual':
                logger.info("[HELENA POP] Enviando interface de seleção manual (dropdown 4 níveis)")

                metadados_extra = {
                    'interface': {
                        'tipo': 'selecao_manual_hierarquica',
                        'dados': {
                            'hierarquia': resultado.get('hierarquia', {}),
                            'acoes_usuario': resultado.get('acoes_usuario', ['confirmar', 'nao_encontrei']),
                            'mensagem': resultado.get('mensagem', ''),
                            'tipo_cap': resultado.get('tipo_cap', 'oficial')
                        }
                    }
                }

                resposta = None  # Modo interface: mensagem textual ausente por design
                return resposta, sm, metadados_extra

            # CASO 3: RAG aguardando descrição (Camada 4 - Parte 1)
            elif resultado.get('origem') == 'rag_aguardando_descricao':
                logger.info("[HELENA POP] RAG aguardando descrição do usuário")

                # Guardar hierarquia herdada no estado
                hierarquia = resultado.get('hierarquia_herdada', {})
                sm.macro_selecionado = hierarquia.get('macroprocesso')
                sm.processo_selecionado = hierarquia.get('processo')
                sm.subprocesso_selecionado = hierarquia.get('subprocesso')

                # Incluir área na hierarquia para o frontend
                area_nome = sm.area_selecionada.get('nome', '') if sm.area_selecionada else ''
                hierarquia['area'] = area_nome

                # Marcar que estamos aguardando descrição RAG
                sm.dados_coletados['aguardando_descricao_rag'] = True

                metadados_extra = {
                    'interface': {
                        'tipo': 'rag_pergunta_atividade',
                        'dados': {
                            'mensagem': resultado.get('mensagem', ''),
                            'hierarquia_herdada': hierarquia,
                            'instrucao': resultado.get('instrucao_frontend', '')
                        }
                    }
                }

                resposta = None  # Modo interface: mensagem textual ausente por design
                return resposta, sm, metadados_extra

            # CASO 4: Atividade encontrada via Camadas 1-2 (match/semantic)
            # Enviar interface visual com botões "Concordar" e "Selecionar manualmente"
            elif resultado.get('sucesso') and resultado.get('atividade'):
                ativ = resultado['atividade']
                origem = resultado.get('origem')

                # Para TODAS as origens que precisam de interface visual
                if origem in ['match_exato', 'match_fuzzy', 'semantic', 'rag_nova_atividade']:
                    logger.info(f"[HELENA POP] Enviando interface sugestao_atividade (origem: {origem})")

                    # Guardar dados no estado
                    sm.macro_selecionado = ativ['macroprocesso']
                    sm.processo_selecionado = ativ.get('processo', 'A definir')
                    sm.subprocesso_selecionado = ativ.get('subprocesso', 'A definir')
                    sm.atividade_selecionada = ativ['atividade']
                    sm.codigo_cap = resultado.get('cap', 'PROVISORIO')

                    # Incluir área na atividade para o frontend
                    area_nome = sm.area_selecionada.get('nome', '') if sm.area_selecionada else ''
                    ativ['area'] = area_nome

                    # Preparar interface
                    metadados_extra = {
                        'interface': {
                            'tipo': 'sugestao_atividade',
                            'dados': {
                                'atividade': ativ,
                                'cap': resultado.get('cap'),
                                'origem': origem,
                                'score': resultado.get('score', 1.0),
                                'pode_editar': resultado.get('pode_editar', False),
                                'tipo_cap': resultado.get('tipo_cap', 'csv_oficial'),
                                'acoes_usuario': resultado.get('acoes_usuario', ['confirmar', 'selecionar_manualmente']),
                                'mensagem': resultado.get('mensagem', '')
                            }
                        }
                    }

                    resposta = None  # Modo interface: mensagem textual ausente por design
                    return resposta, sm, metadados_extra

            # Pipeline não encontrou resultado adequado
            logger.warning("[PIPELINE] Pipeline não encontrou resultado - fallback seleção manual")

        except Exception as e:
            logger.error(f"[PIPELINE] Erro ao executar pipeline: {e}")

        # Fallback: Seleção manual via dropdowns hierárquicos
        sm.estado = EstadoPOP.SELECAO_HIERARQUICA
        sm.dados_coletados['descricao_original'] = descricao_usuario
        logger.info("[PIPELINE] Fallback para seleção manual")

        return (
            "Entendi! Não consegui mapear automaticamente sua descrição.\n\n"
            "Use os **dropdowns hierárquicos** abaixo para selecionar sua atividade:\n"
            "Macroprocesso → Processo → Subprocesso → Atividade"
        ), sm

    def _processar_confirmacao_arquitetura(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        PASSO 2: Processa confirmação da arquitetura sugerida pela IA

        Mostra 2 botões:
        - Concordo com a sugestão ✅
        - Quero editar manualmente ✏️
        """
        msg_lower = mensagem.lower().strip()

        # Se confirmar → ir para ENTREGA ESPERADA com sugestão da IA
        if self._detectar_intencao(msg_lower, 'confirmacao'):
            # 🐛 DEBUG: Verificar se dados da arquitetura estão salvos
            logger.info(f"[DEBUG] CONFIRMACAO ARQUITETURA:")
            logger.info(f"  - CAP: {sm.codigo_cap}")
            logger.info(f"  - Macro: {sm.macro_selecionado}")
            logger.info(f"  - Processo: {sm.processo_selecionado}")
            logger.info(f"  - Subprocesso: {sm.subprocesso_selecionado}")
            logger.info(f"  - Atividade: {sm.atividade_selecionada}")
            logger.info(f"  - dados_coletados: {sm.dados_coletados}")

            # Sugerir entrega esperada usando helper
            sugestao_entrega = self._sugerir_entrega_esperada(sm)
            if sugestao_entrega:
                sm.dados_coletados['entrega_esperada'] = sugestao_entrega
                sm.dados_coletados['entrega_sugerida_temp'] = sugestao_entrega

            # Ir para ENTREGA_ESPERADA
            sm.estado = EstadoPOP.ENTREGA_ESPERADA

            if sugestao_entrega:

                # Enviar interface com sugestão e botões
                metadados_extra = {
                    'interface': {
                        'tipo': 'sugestao_entrega_esperada',
                        'dados': {
                            'sugestao': sugestao_entrega,
                            'acoes_usuario': ['concordar', 'editar_manual']
                        }
                    }
                }
                resposta = None  # Modo interface
                return resposta, sm, metadados_extra
            else:
                resposta = (
                    f"Perfeito! Agora me conta: qual é a **entrega esperada** dessa atividade?\n\n"
                    f"Exemplo: 'Pensão concedida', 'Requerimento analisado', 'Cadastro atualizado'"
                )
                return resposta, sm

        # Se quiser editar → voltar para ENTREGA ESPERADA (arquitetura já está definida)
        elif self._detectar_intencao(msg_lower, 'edicao'):
            # ✅ FIX: Não perguntar nome do processo novamente, só editar entrega
            sm.estado = EstadoPOP.CONFIRMACAO_ENTREGA
            resposta = (
                "Sem problemas! A arquitetura está confirmada.\n\n"
                "Agora, qual é a entrega esperada desta atividade?\n\n"
                "Ex: 'Pensão concedida', 'Requerimento analisado', 'Cadastro atualizado'"
            )
            return resposta, sm

        # Se não entendeu → reperguntar
        else:
            resposta = (
                "Desculpe, não entendi sua resposta.\n\n"
                "Por favor, escolha uma das opções:\n"
                "• Digite 'sim' ou clique em 'Concordo' se a classificação está correta\n"
                "• Digite 'editar' ou clique em 'Quero editar' se deseja ajustar manualmente"
            )
            return resposta, sm

    def _processar_selecao_hierarquica(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        🆕 Processa seleção manual via dropdowns hierárquicos (fallback quando IA falha).

        Espera JSON com: {"macro": "...", "processo": "...", "subprocesso": "...", "atividade": "..."}
        """
        selecao = self._parse_json_seguro(mensagem)
        if not selecao:
            resposta = (
                "Por favor, selecione a arquitetura usando os dropdowns acima. "
                "É só ir escolhendo: Macroprocesso → Processo → Subprocesso → Atividade 📋"
            )
            return resposta, sm

        try:
            # Validar campos obrigatórios
            campos_obrigatorios = ['macroprocesso', 'processo', 'subprocesso', 'atividade']
            if not all(campo in selecao for campo in campos_obrigatorios):
                raise ValueError("Seleção incompleta")

            # Salvar no state machine
            sm.macro_selecionado = selecao['macroprocesso']
            sm.processo_selecionado = selecao['processo']
            sm.subprocesso_selecionado = selecao['subprocesso']
            sm.atividade_selecionada = selecao['atividade']

            # Salvar em dados_coletados
            sm.dados_coletados['macroprocesso'] = selecao['macroprocesso']
            sm.dados_coletados['processo'] = selecao['processo']
            sm.dados_coletados['subprocesso'] = selecao['subprocesso']
            sm.dados_coletados['atividade'] = selecao['atividade']
            sm.dados_coletados['nome_processo'] = selecao['atividade']

            # Gerar código CAP baseado na arquitetura selecionada
            if not sm.codigo_cap:
                sm.codigo_cap = self._gerar_codigo_processo(sm)
                logger.info(f"[CAP] Codigo gerado (selecao manual): {sm.codigo_cap}")

            # Sugerir entrega esperada usando helper
            sugestao_entrega = self._sugerir_entrega_esperada(sm)

            # Ir direto para ENTREGA_ESPERADA (pular confirmação de arquitetura)
            sm.estado = EstadoPOP.ENTREGA_ESPERADA

            if sugestao_entrega:
                # Se a IA conseguiu sugerir, mostrar sugestão
                sm.dados_coletados['entrega_esperada'] = sugestao_entrega
                resposta = (
                    f"Perfeito! Agora vamos definir a **entrega esperada** dessa atividade.\n\n"
                    f"Baseado na atividade **'{sm.atividade_selecionada}'**, sugiro:\n\n"
                    f"**Entrega esperada:** {sugestao_entrega}\n\n"
                    f"Essa sugestão está adequada? Digite 'sim' para confirmar ou escreva a entrega correta."
                )
            else:
                # Se não conseguiu sugerir, perguntar diretamente
                resposta = (
                    f"Perfeito! Agora me diga:\n\n"
                    f"Qual é a **entrega esperada** da atividade **'{sm.atividade_selecionada}'**?\n\n"
                    f"Exemplo: 'Demanda de controle respondida', 'Solicitação analisada e decidida', 'Relatório elaborado'"
                )

            return resposta, sm

        except Exception as e:
            logger.error(f"Erro ao processar seleção hierárquica: {e}")
            resposta = (
                "Desculpe, houve um erro ao processar sua seleção. "
                "Por favor, tente novamente selecionando os campos dos dropdowns."
            )
            return resposta, sm

    def _processar_nome_processo(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa coleta do nome do processo"""
        sm.dados_coletados['nome_processo'] = mensagem.strip()
        sm.estado = EstadoPOP.ENTREGA_ESPERADA

        resposta = (
            f"Perfeito! Vamos mapear: '{sm.dados_coletados['nome_processo']}'\n\n"
            "Agora me diga: qual é o resultado final desta atividade?\n\n"
            "Ex: 'Auxílio concedido', 'Requerimento analisado e decidido', 'Cadastro atualizado'"
        )
        return resposta, sm

    def _processar_entrega_esperada(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa coleta da entrega esperada e mostra confirmação com botões"""
        msg_lower = mensagem.lower().strip()

        # Se o usuário clicou "Concordo com a sugestão"
        if msg_lower == 'concordar':
            # Pegar a sugestão que foi enviada pela interface
            entrega_sugerida = sm.dados_coletados.get('entrega_sugerida_temp', mensagem.strip())
            sm.dados_coletados['entrega_esperada'] = entrega_sugerida
            sm.estado = EstadoPOP.CONFIRMACAO_ENTREGA
        # Se o usuário clicou "Quero editar manualmente"
        elif msg_lower == 'editar_manual':
            sm.estado = EstadoPOP.ENTREGA_ESPERADA
            resposta = (
                "Sem problemas! Qual é a **entrega esperada** dessa atividade?\n\n"
                "Exemplo: 'Pensão concedida', 'Requerimento analisado', 'Cadastro atualizado'"
            )
            return resposta, sm
        # Se o usuário digitou uma entrega manualmente
        else:
            sm.dados_coletados['entrega_esperada'] = mensagem.strip()
            sm.estado = EstadoPOP.CONFIRMACAO_ENTREGA

        # Gerar código CAP antecipadamente
        if not sm.codigo_cap:
            sm.codigo_cap = self._gerar_codigo_processo(sm)

        # Mostrar resumo completo com BOTÕES CONFIRMAR/EDITAR
        nome = sm.nome_usuario or "você"

        # Obter nome e código da área (considerando subárea se existir)
        if sm.subarea_selecionada:
            area_display = f"{sm.subarea_selecionada.get('nome_completo', '')} ({sm.subarea_selecionada.get('codigo', '')})"
        elif sm.area_selecionada:
            area_display = f"{sm.area_selecionada.get('nome', '')} ({sm.area_selecionada.get('codigo', '')})"
        else:
            area_display = "DECIPEX"

        # Pegar a entrega que foi salva (não a mensagem raw que pode ser "concordar")
        entrega_final = sm.dados_coletados.get('entrega_esperada', mensagem.strip())

        resposta = (
            f"## 📋 **RESUMO DA ARQUITETURA E ENTREGA**\n\n"
            f"**Código CAP (CPF do Processo):** {sm.codigo_cap}\n\n"
            f"**Área:** {area_display}\n\n"
            f"**Arquitetura:**\n"
            f"• Macroprocesso: {sm.macro_selecionado}\n"
            f"• Processo: {sm.processo_selecionado}\n"
            f"• Subprocesso: {sm.subprocesso_selecionado}\n"
            f"• Atividade: {sm.atividade_selecionada}\n\n"
            f"**Entrega Final:**\n"
            f"• {entrega_final}\n\n"
            f"**Está correto, {nome}?**"
        )

        # Interface com botões Confirmar/Editar
        sm.tipo_interface = 'confirmacao_dupla'
        sm.dados_interface = {
            'botao_confirmar': 'Confirmar ✅',
            'botao_editar': 'Editar ✏️',
            'valor_confirmar': 'CONFIRMAR',
            'valor_editar': 'EDITAR'
        }

        return resposta, sm

    def _processar_confirmacao_entrega(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa confirmação ou edição da entrega"""
        msg_lower = mensagem.lower().strip()

        if self._detectar_intencao(msg_lower, 'edicao'):
            # Volta para entrega_esperada
            sm.estado = EstadoPOP.ENTREGA_ESPERADA
            sm.tipo_interface = None
            sm.dados_interface = {}

            resposta = (
                "Ok! Vamos corrigir a entrega esperada.\n\n"
                "Qual é a **entrega final** (resultado) desta atividade?\n\n"
                "Ex: 'Auxílio concedido', 'Processo arquivado', 'Reposição ao Erário Efetuada'"
            )
            return resposta, sm

        # Confirmar - IR DIRETO PARA SISTEMAS (nova ordem)
        sm.estado = EstadoPOP.SISTEMAS
        sm.tipo_interface = 'sistemas'
        sm.dados_interface = {
            'sistemas_por_categoria': self.SISTEMAS_DECIPEX,
            'campo_livre': True,
            'multipla_selecao': True
        }

        nome = sm.nome_usuario or "você"

        resposta = (
            f"Perfeito, {nome}! Entrega confirmada.\n\n"
            f"Agora me diga: quais sistemas você utiliza nesta atividade?"
        )

        return resposta, sm

    def _processar_reconhecimento_entrega(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa clique na caixinha de reconhecimento e avança para normas"""
        sm.estado = EstadoPOP.DISPOSITIVOS_NORMATIVOS

        resposta = (
            f"Agora vamos registrar as normas legais, normativos e guias que orientam esta atividade."
        )

        return resposta, sm

    # Sentinels que indicam ausência de normas (não devem virar item de dados)
    _SENTINEL_SEM_NORMAS = {
        "nao sei", "não sei", "nenhuma", "nenhum",
        "nao informado", "não informado",
        "sem norma", "sem normas", "",
    }

    def _processar_dispositivos_normativos(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa coleta de dispositivos normativos e vai para reconhecimento"""
        raw = (mensagem or "").strip()
        v = raw.lower()

        if v in self._SENTINEL_SEM_NORMAS:
            normas = []
        else:
            dados = self._parse_json_seguro(mensagem)
            if isinstance(dados, list):
                normas = [n for n in dados if str(n).strip().lower() not in self._SENTINEL_SEM_NORMAS]
            else:
                # Normalizar separadores: pipe, tab, newline → vírgula
                raw_normalizado = raw.replace(' | ', ',').replace('|', ',').replace('\t', ',').replace('\n', ',')
                normas = [n.strip() for n in raw_normalizado.split(',')
                          if n.strip() and n.strip().lower() not in self._SENTINEL_SEM_NORMAS]

        sm.dados_coletados['dispositivos_normativos'] = normas

        sm.estado = EstadoPOP.TRANSICAO_ROADTRIP
        sm.tipo_interface = None
        sm.dados_interface = None

        logger.info(f"[NORMAS] Normas registradas: {len(normas)}")

        if normas:
            resposta = (
                "Normas são como placas que sempre devem orientar nosso caminho. "
                "As normas da sua atividade foram registradas.\n\n"
                "*É possível complementar posteriormente, se necessário.*"
            )
        else:
            resposta = "Nenhuma norma registrada neste momento. É possível complementar posteriormente."

        # ✅ Interface roadtrip será adicionada automaticamente no bloco de PROXIMA_INTERFACE
        # Não precisa de auto_continue!
        return resposta, sm

    def _processar_transicao_roadtrip(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Processa estado de transição roadtrip.

        Qualquer clique/mensagem avança para OPERADORES.
        """
        nome = sm.nome_usuario or "você"

        # 🎯 Avançar para operadores
        sm.estado = EstadoPOP.OPERADORES

        logger.info(f"👥 [ROADTRIP→OPERADORES] Clique no carro detectado! Indo para estado OPERADORES!")

        resposta = (
            f"Agora vamos identificar quem participa da execução dessa atividade.\n\n"
            f"Selecione abaixo:\n"
            f"– quem executa\n"
            f"– quem revisa\n"
            f"– quem apoia\n"
            f"– e quem atua antes do processo chegar até você\n\n"
            f"Se você também executa a atividade, inclua-se.\n\n"
            f"Caso algum papel não apareça na lista, é possível informar manualmente."
        )

        return resposta, sm

    def _processar_operadores(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa coleta de operadores com fuzzy matching"""
        logger.info(f"[OPERADORES] Processando mensagem: {mensagem[:100]}")

        # Aceitar JSON (de interface) ou texto
        dados = self._parse_json_seguro(mensagem)
        if isinstance(dados, list):
            operadores = dados
            logger.info(f"[OPERADORES] Parsed JSON com sucesso: {operadores}")
        else:
            # FUZZY PARSING de operadores
            logger.info("[OPERADORES] Caindo no fuzzy parsing")
            operadores = parse_operadores(mensagem, self.OPERADORES_DECIPEX)
            logger.info(f"[OPERADORES] Fuzzy parsing result: {operadores}")

        sm.dados_coletados['operadores'] = operadores

        # Se veio da revisão final, voltar para lá
        if sm.return_to == EstadoPOP.REVISAO_FINAL.value:
            sm.return_to = None
            sm.estado = EstadoPOP.REVISAO_FINAL
            sm.tipo_interface = 'revisao_final'
            sm.dados_interface = self._montar_dados_revisao_final(sm)
            logger.info(f"[OPERADORES] return_to=revisao_final, voltando para hub")
            return f"Operadores atualizados! Revise os dados abaixo.", sm

        sm.estado = EstadoPOP.FLUXOS
        logger.info(f"[OPERADORES] Salvou {len(operadores)} operadores, mudou estado para FLUXOS")

        # Interface de entrada de processo
        # ✅ CRÍTICO: Carregar dados com tratamento de exceção individual
        try:
            areas_organizacionais = carregar_areas_organizacionais()
            logger.info(f"[OPERADORES] Áreas carregadas: {len(areas_organizacionais)} áreas")
        except Exception as e:
            logger.error(f"[OPERADORES] ERRO ao carregar áreas: {e}")
            areas_organizacionais = {}  # Fallback vazio

        try:
            orgaos_centralizados = carregar_orgaos_centralizados()
            logger.info(f"[OPERADORES] Órgãos carregados: {len(orgaos_centralizados)} órgãos")
        except Exception as e:
            logger.error(f"[OPERADORES] ERRO ao carregar órgãos: {e}")
            orgaos_centralizados = []  # Fallback vazio

        try:
            canais_atendimento = carregar_canais_atendimento()
            logger.info(f"[OPERADORES] Canais carregados: {len(canais_atendimento)} canais")
        except Exception as e:
            logger.error(f"[OPERADORES] ERRO ao carregar canais: {e}")
            canais_atendimento = []  # Fallback vazio

        sm.tipo_interface = 'fluxos_entrada'
        sm.dados_interface = {
            'areas_organizacionais': list(areas_organizacionais.values()) if isinstance(areas_organizacionais, dict) else areas_organizacionais,
            'orgaos_centralizados': orgaos_centralizados,
            'canais_atendimento': canais_atendimento
        }

        nome = sm.nome_usuario or "você"
        resposta = f"Perfeito! Registrei {len(operadores)} operador(es). Agora me diga: de onde vem o processo que você executa?"

        # 🔍 DEBUG CRÍTICO: Verificar estado antes de retornar
        logger.info(f"[OPERADORES] ===== DEBUG RETORNO =====")
        logger.info(f"[OPERADORES] sm.estado = {sm.estado}")
        logger.info(f"[OPERADORES] sm.tipo_interface = {sm.tipo_interface}")
        logger.info(f"[OPERADORES] sm.dados_interface tem {len(sm.dados_interface)} chaves")
        logger.info(f"[OPERADORES] areas_organizacionais: {len(sm.dados_interface.get('areas_organizacionais', []))}")
        logger.info(f"[OPERADORES] orgaos_centralizados: {len(sm.dados_interface.get('orgaos_centralizados', []))}")
        logger.info(f"[OPERADORES] canais_atendimento: {len(sm.dados_interface.get('canais_atendimento', []))}")
        logger.info(f"[OPERADORES] =============================")

        return resposta, sm

    def _processar_sistemas(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa sistemas utilizados"""
        # Parse: espera JSON array ["SIAPE", "SEI"] ou texto "nenhum"
        if mensagem.strip().lower() in ['nenhum', 'nao sei', 'não sei']:
            sistemas = []
        else:
            dados = self._parse_json_seguro(mensagem)
            if isinstance(dados, list):
                sistemas = dados
            else:
                sistemas = []

        # Salvar sistemas
        sm.dados_coletados['sistemas'] = sistemas

        # Se veio da revisão final, voltar para lá
        if sm.return_to == EstadoPOP.REVISAO_FINAL.value:
            sm.return_to = None
            sm.estado = EstadoPOP.REVISAO_FINAL
            sm.tipo_interface = 'revisao_final'
            sm.dados_interface = self._montar_dados_revisao_final(sm)
            return "Sistemas atualizados! Revise os dados abaixo.", sm

        # Fluxo normal: avançar para DISPOSITIVOS_NORMATIVOS
        sm.estado = EstadoPOP.DISPOSITIVOS_NORMATIVOS

        grupos_normas = {}
        if self.suggestor_base_legal:
            try:
                grupos_normas = self.suggestor_base_legal.obter_grupos_normas()
            except:
                pass

        # Interface de normas
        sm.tipo_interface = 'normas'
        sm.dados_interface = {
            'grupos': grupos_normas,
            'campo_livre': True,
            'multipla_selecao': True,
            'texto_introducao': (
                "• Utilize a lista disponível para localizar normas já cadastradas.\n\n"
                "• Caso necessário, é possível adicionar normas manualmente.\n\n"
                "• Para apoio na pesquisa de normas, está disponível o acesso à **IA do Sigepe Legis**, "
                "ferramenta mantida pelo setor de legislação, que auxilia na localização de referências normativas.\n\n"
                "O registro das normas é de responsabilidade de quem conduz o mapeamento."
            )
        }

        resposta = (
            f"Agora vamos registrar as normas legais, normativos e guias que orientam esta atividade."
        )

        return resposta, sm

    def _processar_fluxos(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa coleta de fluxos (entrada e saída)"""
        msg_lower = mensagem.lower().strip()

        # Se ainda não coletou fluxos de entrada
        if not sm.dados_coletados.get('fluxos_entrada'):
            if msg_lower in ['nenhum', 'nao', 'não', 'nao_sei']:
                sm.dados_coletados['fluxos_entrada'] = []
            else:
                # Aceitar JSON estruturado ou texto simples
                dados_json = self._parse_json_seguro(mensagem)
                fluxos = self._parsear_fluxo_json(dados_json, 'origens_selecionadas', 'outras_origens', formato_entrada=True)
                if fluxos is None:
                    # ✅ GUARD RAIL: Detectar se resposta é operadores duplicados (não fluxos)
                    ops = sm.dados_coletados.get('operadores') or []
                    if (
                        isinstance(dados_json, list)
                        and all(isinstance(item, str) for item in dados_json)
                        and ops
                        and set(map(str.lower, dados_json)) == set(map(str.lower, ops))
                    ):
                        logger.warning(
                            f"[FLUXOS_ENTRADA] Resposta é operadores duplicados. "
                            f"estado={sm.estado}, ops={ops[:3]}, dados={dados_json[:3]}"
                        )
                        # Re-renderizar interface de fluxos_entrada sem modificar estado
                        try:
                            areas_organizacionais = carregar_areas_organizacionais()
                            orgaos_centralizados = carregar_orgaos_centralizados()
                            canais_atendimento = carregar_canais_atendimento()
                        except Exception as e:
                            logger.error(f"[FLUXOS] Erro ao carregar dados: {e}")
                            areas_organizacionais = {}
                            orgaos_centralizados = []
                            canais_atendimento = []
                        sm.tipo_interface = 'fluxos_entrada'
                        sm.dados_interface = {
                            'areas_organizacionais': list(areas_organizacionais.values()) if isinstance(areas_organizacionais, dict) else areas_organizacionais,
                            'orgaos_centralizados': orgaos_centralizados,
                            'canais_atendimento': canais_atendimento
                        }
                        resposta = "Por favor, selecione de onde vem o processo (origens de entrada)."
                        return resposta, sm
                    # Fallback normal (texto livre)
                    fluxos = [f.strip() for f in mensagem.replace('\n', ',').split('|') if f.strip()]
                sm.dados_coletados['fluxos_entrada'] = fluxos

                # Guardar dados estruturados originais para pré-preenchimento na saída
                if dados_json and isinstance(dados_json, dict):
                    sm.dados_coletados['fluxos_entrada_estruturados'] = dados_json.get('origens_selecionadas', [])

            # Carregar dados para interface de fluxos de SAÍDA
            try:
                areas_organizacionais = carregar_areas_organizacionais()
                orgaos_centralizados = carregar_orgaos_centralizados()
                canais_atendimento = carregar_canais_atendimento()
            except Exception as e:
                logger.error(f"[FLUXOS] Erro ao carregar dados: {e}")
                areas_organizacionais = []
                orgaos_centralizados = []
                canais_atendimento = []

            # ✅ Setar interface para fluxos de SAÍDA
            sm.tipo_interface = 'fluxos_saida'
            sm.dados_interface = {
                'areas_organizacionais': list(areas_organizacionais.values()) if isinstance(areas_organizacionais, dict) else areas_organizacionais,
                'orgaos_centralizados': orgaos_centralizados,
                'canais_atendimento': canais_atendimento,
                'fluxos_entrada': sm.dados_coletados.get('fluxos_entrada', []),
                'fluxos_entrada_estruturados': sm.dados_coletados.get('fluxos_entrada_estruturados', [])
            }

            resposta = f"Perfeito! Registrei {len(sm.dados_coletados['fluxos_entrada'])} origem(ns) de entrada. ✅"
        else:
            # Coletar fluxos de saída
            if msg_lower in ['nenhum', 'nao', 'não', 'nao_sei']:
                sm.dados_coletados['fluxos_saida'] = []
            else:
                # Aceitar JSON estruturado ou texto simples
                dados_json = self._parse_json_seguro(mensagem)
                fluxos = self._parsear_fluxo_json(dados_json, 'destinos_selecionados', 'outros_destinos', formato_entrada=False)
                if fluxos is None:
                    # ✅ GUARD RAIL: Detectar se resposta é operadores duplicados (não fluxos)
                    ops = sm.dados_coletados.get('operadores') or []
                    if (
                        isinstance(dados_json, list)
                        and all(isinstance(item, str) for item in dados_json)
                        and ops
                        and set(map(str.lower, dados_json)) == set(map(str.lower, ops))
                    ):
                        logger.warning(
                            f"[FLUXOS_SAIDA] Resposta é operadores duplicados. "
                            f"estado={sm.estado}, ops={ops[:3]}, dados={dados_json[:3]}"
                        )
                        # Re-renderizar interface de fluxos_saida sem modificar estado
                        try:
                            areas_organizacionais = carregar_areas_organizacionais()
                            orgaos_centralizados = carregar_orgaos_centralizados()
                            canais_atendimento = carregar_canais_atendimento()
                        except Exception as e:
                            logger.error(f"[FLUXOS] Erro ao carregar dados: {e}")
                            areas_organizacionais = {}
                            orgaos_centralizados = []
                            canais_atendimento = []
                        sm.tipo_interface = 'fluxos_saida'
                        sm.dados_interface = {
                            'areas_organizacionais': list(areas_organizacionais.values()) if isinstance(areas_organizacionais, dict) else areas_organizacionais,
                            'orgaos_centralizados': orgaos_centralizados,
                            'canais_atendimento': canais_atendimento,
                            'fluxos_entrada': sm.dados_coletados.get('fluxos_entrada', []),
                            'fluxos_entrada_estruturados': sm.dados_coletados.get('fluxos_entrada_estruturados', [])
                        }
                        resposta = "Por favor, selecione para onde vai o resultado do processo (destinos de saída)."
                        return resposta, sm
                    # Fallback normal (texto livre)
                    fluxos = [f.strip() for f in mensagem.replace('\n', ',').split(',') if f.strip()]
                sm.dados_coletados['fluxos_saida'] = fluxos

            # Se veio da revisão final, voltar para lá
            if sm.return_to == EstadoPOP.REVISAO_FINAL.value:
                sm.return_to = None
                sm.estado = EstadoPOP.REVISAO_FINAL
                sm.tipo_interface = 'revisao_final'
                sm.dados_interface = self._montar_dados_revisao_final(sm)
                return "Fluxos atualizados! Revise os dados abaixo.", sm

            # Ir para PONTOS_ATENCAO (fluxo completo: PONTOS → REVISAO → TRANSICAO_EPICA)
            sm.estado = EstadoPOP.PONTOS_ATENCAO
            sm.tipo_interface = 'texto_com_alternativa'
            sm.dados_interface = {
                'placeholder': 'Descreva os pontos de atenção...',
                'hint': 'Prazo crítico, documentos sensíveis, etapas que geram dúvidas, etc.',
                'botao_alternativo': {
                    'label': 'Nenhum ponto de atenção',
                    'acao': 'nenhum',
                },
            }

            nome = sm.nome_usuario or "você"

            resposta = (
                f"Ótimo! Registrei {len(sm.dados_coletados['fluxos_saida'])} fluxo(s) de saída. ✅\n\n"
                f"Agora me diga: **Há algum ponto de atenção especial** neste processo?\n\n"
                f"Por exemplo:\n"
                f"• Prazo crítico que não pode atrasar\n"
                f"• Documentos que devem ter atenção redobrada\n"
                f"• Etapas que costumam gerar dúvidas\n\n"
                f"Digite os pontos de atenção ou clique no botão abaixo."
            )

        return resposta, sm

    def _processar_pontos_atencao(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Processa pontos de atenção (último campo antes da revisão)

        Após coletar, vai para REVISAO_PRE_DELEGACAO
        """
        msg_lower = mensagem.lower().strip()
        nome = sm.nome_usuario or "você"

        # Mostrar exemplos comuns e permanecer no estado
        if msg_lower == 'ver_exemplos':
            sm.tipo_interface = 'texto_com_alternativa'
            sm.dados_interface = {
                'placeholder': 'Descreva os pontos de atenção...',
                'botao_alternativo': {
                    'label': 'Nenhum ponto de atenção',
                    'acao': 'nenhum',
                },
            }
            resposta = (
                f"Aqui estão alguns exemplos comuns de pontos de atenção:\n\n"
                f"• Verificar se há legado da centralização\n"
                f"• Se judicial, verificar se há multa\n"
                f"• Verificar se exigências devem ser feitas todas de uma vez\n"
                f"• Verificar se não há outro processo com o mesmo tema\n"
                f"• Em acerto de contas, sempre fazer batimento de devido x recebido\n\n"
                f"Se algum desses se aplica, digite o ponto de atenção ou clique no botão abaixo."
            )
            return resposta, sm

        # Aceitar respostas negativas
        if msg_lower in ['não', 'nao', 'nenhum', 'não há', 'nao ha', 'não tem', 'nao tem', 'sem pontos', 'pular', 'skip']:
            sm.dados_coletados['pontos_atencao'] = "Não há pontos especiais de atenção."
        else:
            sm.dados_coletados['pontos_atencao'] = mensagem.strip()

        # Ir para REVISAO_PRE_DELEGACAO
        sm.estado = EstadoPOP.REVISAO_PRE_DELEGACAO

        # Gerar código CAP se ainda não foi gerado
        if not sm.codigo_cap:
            sm.codigo_cap = self._gerar_codigo_processo(sm)

        # Gerar resumo completo
        resumo = self._gerar_resumo_pop(sm)

        resposta = (
            f"Perfeito, {nome}! Já registramos os dados principais do POP.\n\n"
            f"{resumo}\n\n"
            f"Caso queira alterar algum dado desta fase, a revisão final estará disponível ao concluir o mapeamento."
        )

        # Badge checkpoint — marco da Fase 1
        sm.tipo_interface = 'badge_cartografo'
        sm.dados_interface = {
            'titulo': 'Fase 1 concluída!',
            'emoji': '✔',
            'descricao': 'Os dados principais do seu POP foram registrados com sucesso.',
        }

        return resposta, sm

    def _processar_revisao_pre_delegacao(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        REVISÃO 2 - Pré-delegação

        Badge checkpoint da Fase 1 → clique mostra introdução pré-etapas (café, etc.)
        com botões "Vamos começar" / "Salvar e continuar depois".
        """
        nome = sm.nome_usuario or "você"

        # Clique no badge → introdução pré-etapas + botões
        sm.estado = EstadoPOP.TRANSICAO_EPICA

        resposta = (
            f"## 🎯 **AGORA ENTRAMOS NA PARTE PRINCIPAL DO PROCESSO**\n\n"
            f"A próxima fase é a **mais importante e detalhada**.\n"
            f"Nela, vamos mapear **cada etapa** da sua atividade, com atenção aos detalhes.\n\n"
            f"Para cada etapa, vou perguntar:\n\n"
            f"📄 O que é feito\n"
            f"👤 Quem executa\n"
            f"📚 Qual norma fundamenta\n"
            f"💻 Qual sistema é utilizado\n"
            f"🗂 Quais documentos são utilizados ou gerados\n\n"
            f"**⏱ Tempo estimado:** entre 30 minutos e 1 hora, dependendo da complexidade do processo.\n\n"
            f"**💡 Antes de começar**\n\n"
            f"Esta é a etapa mais detalhada do processo. Para facilitar, recomendamos:\n\n"
            f"☕ Ter água ou café por perto\n"
            f"🧍‍♂️ Fazer uma breve pausa para se alongar, se necessário\n"
            f"🚻 Ir ao banheiro antes de iniciar\n"
            f"📂 Ter em mãos exemplos reais do processo\n\n"
            f"Caso queira alterar algum dado da fase anterior, a revisão final estará disponível ao concluir o mapeamento.\n\n"
            f"Quando estiver pronto(a), clique em **Vamos começar** para iniciar.\n"
            f"Se preferir continuar em outro momento, utilize a opção **Salvar e continuar depois**."
        )

        sm.tipo_interface = 'confirmacao_dupla'
        sm.dados_interface = {
            'opcao_a': 'Vamos começar',
            'opcao_b': 'Salvar e continuar depois',
        }

        return resposta, sm

    def _processar_transicao_epica(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Processa botões "Vamos começar" / "Salvar e continuar depois".
        """
        msg_lower = mensagem.lower().strip()
        nome = sm.nome_usuario

        if self._detectar_intencao(msg_lower, 'pausa') or self._detectar_intencao(msg_lower, 'negacao'):
            resposta = (
                f"Sem problema, {nome}! 😊\n\n"
                "Entendo perfeitamente. Mapear processos requer concentração e tempo.\n\n"
                "**✅ Seus dados foram salvos** e você pode continuar quando quiser.\n\n"
                "📌 **Para retomar:** É só clicar em **Vamos começar**\n\n"
                "Até breve! Estarei aqui quando você voltar. 👋"
            )

            sm.tipo_interface = 'confirmacao_dupla'
            sm.dados_interface = {
                'opcao_a': 'Vamos começar',
                'opcao_b': 'Salvar e continuar depois',
            }
            return resposta, sm

        # Confirmação → direto pra etapas
        sm.estado = EstadoPOP.ETAPA_FORM
        sm._etapa_sm = None

        sm.tipo_interface = 'etapa_form'
        sm.dados_interface = self._montar_dados_etapa_form(sm, 1)

        resposta = (
            f"📋 **Vamos às etapas da atividade**\n\n"
            f"Cada etapa representa uma ação concreta que a equipe executa para cumprir a demanda. "
            f"Descreva o que é feito, em que ordem e com qual objetivo.\n\n"
            f"Essas informações serão usadas para orientar a execução do processo e apoiar análises futuras."
        )

        return resposta, sm

    def _processar_delegacao_etapas(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa delegação para Helena Etapas"""
        msg_lower = mensagem.lower().strip()

        if self._detectar_intencao(msg_lower, 'confirmacao'):
            sm.concluido = True
            sm.estado = EstadoPOP.FINALIZADO

            resposta = (
                f"Perfeito, {sm.nome_usuario}! Os dados iniciais do processo foram coletados com sucesso.\n\n"
                "Agora vou transferir você para o Helena Etapas para detalharmos cada etapa operacional.\n\n"
                "Até logo!"
            )
        else:
            resposta = (
                "Não entendi. Digite 'ok' ou 'continuar' para prosseguir para o detalhamento das etapas."
            )

        return resposta, sm

    # ========================================================================
    # COLETA INLINE DE ETAPAS (ETAPAS_INLINE=True)
    # ========================================================================

    # Mapa de EstadoEtapa → EstadoPOP correspondente
    _ETAPA_SM_TO_POP = {
        EstadoEtapa.DESCRICAO: EstadoPOP.ETAPA_DESCRICAO,
        EstadoEtapa.OPERADOR: EstadoPOP.ETAPA_OPERADOR,
        EstadoEtapa.SISTEMAS: EstadoPOP.ETAPA_SISTEMAS,
        EstadoEtapa.DOCS_REQUERIDOS: EstadoPOP.ETAPA_DOCS_REQUERIDOS,
        EstadoEtapa.DOCS_GERADOS: EstadoPOP.ETAPA_DOCS_GERADOS,
        EstadoEtapa.TEMPO_ESTIMADO: EstadoPOP.ETAPA_TEMPO,
        EstadoEtapa.PERGUNTA_CONDICIONAL: EstadoPOP.ETAPA_CONDICIONAL,
        EstadoEtapa.TIPO_CONDICIONAL: EstadoPOP.ETAPA_TIPO_CONDICIONAL,
        EstadoEtapa.ANTES_DECISAO: EstadoPOP.ETAPA_ANTES_DECISAO,
        EstadoEtapa.CENARIOS: EstadoPOP.ETAPA_CENARIOS,
        EstadoEtapa.SUBETAPAS_CENARIO: EstadoPOP.ETAPA_SUBETAPAS_CENARIO,
        EstadoEtapa.DETALHES: EstadoPOP.ETAPA_DETALHES,
        EstadoEtapa.FINALIZADA: EstadoPOP.ETAPA_MAIS,
    }

    def _processar_etapa_inline(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Dispatcher para coleta inline de etapas dentro do POP.

        Usa EtapaStateMachine como módulo: processa a mensagem, sincroniza
        o estado de volta ao EstadoPOP e define tipo_interface/dados_interface
        para cada pergunta.
        """
        # -- Comandos especiais: interceptar ANTES de qualquer estado --
        # (botões de confirmacao_dupla podem ficar visíveis após mudança de estado)
        msg_lower = mensagem.lower().strip()
        if msg_lower == '__finalizar_etapas__':
            if not sm.etapas_coletadas:
                return "⚠️ Nenhuma etapa foi mapeada ainda. Descreva a primeira etapa.", sm
            sm.estado = EstadoPOP.ETAPA_REVISAO
            sm.tipo_interface = 'editar_etapas'
            sm.dados_interface = {
                'etapas': self._serializar_etapas_para_frontend(sm.etapas_coletadas)
            }
            total = len(sm.etapas_coletadas)
            resposta = (
                f"📋 **{total} {'etapa mapeada' if total == 1 else 'etapas mapeadas'}!**\n\n"
                f"Revise as etapas abaixo. Você pode editar, deletar ou adicionar.\n"
                f"Quando estiver satisfeito, clique em **Salvar Alterações**."
            )
            return resposta, sm

        if msg_lower == '__editar_ultima_etapa__':
            if sm.etapas_coletadas:
                # Usar indice salvo (para insercoes no meio) ou fallback para ultima
                idx = (sm.dados_interface or {}).get('ultimo_etapa_idx', len(sm.etapas_coletadas) - 1)
                idx = min(idx, len(sm.etapas_coletadas) - 1)
                etapa_existente = sm.etapas_coletadas[idx]
                sm.estado = EstadoPOP.ETAPA_FORM
                sm._etapa_sm = None
                dados_form = self._montar_dados_etapa_form(sm, idx + 1)
                dados_form['etapa_preenchida'] = etapa_existente
                dados_form['editando_idx'] = idx
                sm.tipo_interface = 'etapa_form'
                sm.dados_interface = dados_form
                return f"Editando **Etapa {idx + 1}**. Ajuste os campos e confirme.", sm

        if msg_lower == '__proxima_etapa__':
            numero = len(sm.etapas_coletadas) + 1
            sm.estado = EstadoPOP.ETAPA_FORM
            sm._etapa_sm = None
            sm.tipo_interface = 'etapa_form'
            sm.dados_interface = self._montar_dados_etapa_form(sm, numero)
            resposta = f"Preencha o formulario da **Etapa {numero}**."
            return resposta, sm

        # -- ETAPA_MAIS: Perguntar se há mais etapas --
        if sm.estado == EstadoPOP.ETAPA_MAIS:
            return self._processar_etapa_mais(mensagem, sm)

        # -- ETAPA_REVISAO: Revisar/editar todas as etapas --
        if sm.estado == EstadoPOP.ETAPA_REVISAO:
            return self._processar_etapa_revisao(mensagem, sm)

        # -- Coleta normal via EtapaStateMachine --
        if not sm._etapa_sm:
            # Sessão corrompida, reiniciar coleta
            logger.warning("[ETAPA INLINE] _etapa_sm ausente, reiniciando")
            numero = len(sm.etapas_coletadas) + 1
            etapa_sm = EtapaStateMachine(
                numero_etapa=numero,
                operadores_disponiveis=sm.dados_coletados.get('operadores', [])
            )
            sm._etapa_sm = etapa_sm.to_dict()

        # Deserializar, processar, serializar
        etapa_sm = EtapaStateMachine.from_dict(sm._etapa_sm)
        resultado = etapa_sm.processar(mensagem)
        sm._etapa_sm = etapa_sm.to_dict()

        # Erro da SM → repetir pergunta
        if 'erro' in resultado:
            resposta = f"⚠️ {resultado['erro']}"
            return resposta, sm

        # Etapa finalizada → salvar e ir para ETAPA_MAIS
        if etapa_sm.completa():
            idx = etapa_sm.etapa_index

            if idx is not None:
                # --- MERGE: condicional via form ---
                # Safety check: validar bounds
                if not (0 <= idx < len(sm.etapas_coletadas)):
                    logger.error(f"[MERGE] etapa_index={idx} fora de bounds (len={len(sm.etapas_coletadas)}). Ignorando merge.")
                    sm._etapa_sm = None
                    sm.estado = EstadoPOP.ETAPA_MAIS
                    sm.tipo_interface = 'confirmacao_dupla'
                    total = len(sm.etapas_coletadas)
                    sm.dados_interface = {
                        'botao_terceiro': f'Editar Etapa {total}',
                        'valor_terceiro': f'__editar_ultima_etapa__',
                        'botao_editar': 'Finalizar etapas',
                        'valor_editar': '__finalizar_etapas__',
                        'botao_confirmar': f'Adicionar Etapa {total + 1}',
                        'valor_confirmar': '__proxima_etapa__'
                    }
                    return "Erro interno ao salvar condicionais. Voce pode continuar ou finalizar.", sm

                # Merge condicional data into existing etapa
                sm.etapas_coletadas[idx].update({
                    'tipo': 'condicional',
                    'tipo_condicional': etapa_sm.tipo_condicional,
                    'antes_decisao': {
                        'numero': f"{etapa_sm.numero}.1",
                        'descricao': etapa_sm.antes_decisao or ''
                    },
                    'cenarios': [c.to_dict() for c in etapa_sm.cenarios],
                })
                # Remover verificacoes/detalhes (condicionais usam cenarios)
                sm.etapas_coletadas[idx].pop('detalhes', None)
                sm.etapas_coletadas[idx].pop('verificacoes', None)
                # Re-normalizar depois do merge
                sm.etapas_coletadas[idx] = normalizar_etapa(sm.etapas_coletadas[idx], idx + 1)
                self._consolidar_documentos(sm)

                etapa_dict = sm.etapas_coletadas[idx]
                op = etapa_dict.get('operador_nome', '')
            else:
                # --- APPEND: fluxo conversacional legado ---
                etapa_dict = etapa_sm.obter_dict()
                numero = len(sm.etapas_coletadas) + 1
                etapa_dict = normalizar_etapa(etapa_dict, numero)
                sm.etapas_coletadas.append(etapa_dict)

            sm._etapa_sm = None
            sm.estado = EstadoPOP.ETAPA_MAIS

            total = len(sm.etapas_coletadas)
            resposta = self._formatar_resumo_etapa(etapa_dict)

            sm.tipo_interface = 'confirmacao_dupla'
            sm.dados_interface = {
                'botao_terceiro': f'Editar Etapa {total}',
                'valor_terceiro': '__editar_ultima_etapa__',
                'ultimo_etapa_idx': total - 1,
                'botao_editar': 'Finalizar etapas',
                'valor_editar': '__finalizar_etapas__',
                'botao_confirmar': f'Adicionar Etapa {total + 1}',
                'valor_confirmar': '__proxima_etapa__',
            }

            return resposta, sm

        # Sincronizar estado da SM → EstadoPOP
        novo_estado_pop = self._ETAPA_SM_TO_POP.get(etapa_sm.estado)
        if novo_estado_pop:
            sm.estado = novo_estado_pop

        # Definir interface e resposta para o próximo estado
        resposta, sm = self._definir_interface_etapa(etapa_sm, sm)
        return resposta, sm

    def _processar_etapa_mais(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa decisão: mais etapas ou finalizar"""
        msg_lower = mensagem.lower().strip()

        if msg_lower == '__editar_ultima_etapa__':
            if sm.etapas_coletadas:
                # Usar indice salvo (para insercoes no meio) ou fallback para ultima
                idx = (sm.dados_interface or {}).get('ultimo_etapa_idx', len(sm.etapas_coletadas) - 1)
                idx = min(idx, len(sm.etapas_coletadas) - 1)
                etapa_existente = sm.etapas_coletadas[idx]
                sm.estado = EstadoPOP.ETAPA_FORM
                sm._etapa_sm = None
                dados_form = self._montar_dados_etapa_form(sm, idx + 1)
                dados_form['etapa_preenchida'] = etapa_existente
                dados_form['editando_idx'] = idx
                sm.tipo_interface = 'etapa_form'
                sm.dados_interface = dados_form
                return f"Editando **Etapa {idx + 1}**. Ajuste os campos e confirme.", sm

        if msg_lower == '__proxima_etapa__' or self._detectar_intencao(msg_lower, 'confirmacao'):
            # Próxima etapa via form
            numero = len(sm.etapas_coletadas) + 1
            sm.estado = EstadoPOP.ETAPA_FORM
            sm._etapa_sm = None
            sm.tipo_interface = 'etapa_form'
            sm.dados_interface = self._montar_dados_etapa_form(sm, numero)

            resposta = f"Preencha o formulario da **Etapa {numero}**."
            return resposta, sm

        elif msg_lower == '__finalizar_etapas__' or self._detectar_intencao(msg_lower, 'negacao'):
            if not sm.etapas_coletadas:
                resposta = "⚠️ Nenhuma etapa foi mapeada. Descreva pelo menos uma etapa."
                return resposta, sm

            # Ir para revisão
            sm.estado = EstadoPOP.ETAPA_REVISAO
            sm.tipo_interface = 'editar_etapas'
            sm.dados_interface = {
                'etapas': self._serializar_etapas_para_frontend(sm.etapas_coletadas)
            }

            total = len(sm.etapas_coletadas)
            resposta = (
                f"📋 **{total} {'etapa mapeada' if total == 1 else 'etapas mapeadas'}!**\n\n"
                f"Revise as etapas abaixo. Você pode editar, deletar ou adicionar.\n"
                f"Quando estiver satisfeito, clique em **Salvar Alterações**."
            )
            return resposta, sm

        else:
            resposta = "Deseja adicionar mais uma etapa ou finalizar?"
            sm.tipo_interface = 'confirmacao_dupla'
            total = len(sm.etapas_coletadas)
            sm.dados_interface = {
                'botao_confirmar': f'Adicionar Etapa {total + 1}',
                'botao_editar': 'Finalizar etapas',
                'valor_confirmar': '__proxima_etapa__',
                'valor_editar': '__finalizar_etapas__'
            }
            return resposta, sm

    def _processar_etapa_revisao(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Processa ETAPA_REVISAO: aceita confirmar, editar, deletar.
        InterfaceEditarEtapas envia JSON com {acao, ...}.
        """
        msg_lower = mensagem.lower().strip()

        # Tentar parsear JSON da InterfaceEditarEtapas
        try:
            data = json.loads(mensagem)
            acao = data.get('acao', '')

            if acao == 'salvar_etapas':
                # Frontend envia etapas (pode ter deleções e reordenações).
                # Usar id (UUID) para preservar dados ricos do backend
                # e respeitar a ordem do frontend.
                etapas_editadas = data.get('etapas', [])
                n_front = len(etapas_editadas)
                n_back = len(sm.etapas_coletadas)
                if etapas_editadas:
                    etapas_by_id = {e.get('id'): e for e in sm.etapas_coletadas}
                    novas_etapas = []
                    for i, fe in enumerate(etapas_editadas, 1):
                        etapa_id = fe.get('id')
                        if etapa_id and etapa_id in etapas_by_id:
                            etapa = etapas_by_id[etapa_id]
                            etapa['numero'] = str(i)
                            etapa['ordem'] = i
                            novas_etapas.append(etapa)
                        else:
                            # FALLBACK: aceitar etapa do frontend (não descartar)
                            logger.warning(f"[GUARD salvar_etapas] id={etapa_id} sem match — usando dados do frontend")
                            fe['numero'] = str(i)
                            fe['ordem'] = i
                            novas_etapas.append(normalizar_etapa(fe, i))
                    if novas_etapas:
                        sm.etapas_coletadas = novas_etapas
                    # Logar apenas anomalia: match parcial ou zero
                    if len(novas_etapas) < n_front:
                        logger.warning(f"[GUARD salvar_etapas] ANOMALIA: match {len(novas_etapas)}/{n_front} (backend tinha {n_back})")
                elif n_back > 0:
                    logger.warning(f"[GUARD salvar_etapas] frontend enviou 0 etapas mas backend tinha {n_back}")
                return self._finalizar_etapas(sm)

            elif acao == 'deletar_etapa':
                # Deletar etapa por número
                numero = data.get('numero_etapa')
                if numero and numero <= len(sm.etapas_coletadas):
                    sm.etapas_coletadas.pop(numero - 1)
                    # Renumerar
                    for i, e in enumerate(sm.etapas_coletadas, 1):
                        e['numero'] = str(i)

                # Reexibir interface de edição
                sm.tipo_interface = 'editar_etapas'
                sm.dados_interface = {
                    'etapas': self._serializar_etapas_para_frontend(sm.etapas_coletadas)
                }
                resposta = f"Etapa removida. {len(sm.etapas_coletadas)} etapas restantes."
                return resposta, sm

            elif acao == 'editar_etapa':
                # Encontrar etapa por id (fallback: numero_etapa como index)
                etapa_id = data.get('etapa_id')
                numero_etapa = data.get('numero_etapa')
                etapa_encontrada = None
                etapa_idx = None

                if etapa_id:
                    for idx, e in enumerate(sm.etapas_coletadas):
                        if e.get('id') == etapa_id:
                            etapa_encontrada = e
                            etapa_idx = idx
                            break

                if etapa_encontrada is None and numero_etapa:
                    idx_fallback = int(numero_etapa) - 1
                    if 0 <= idx_fallback < len(sm.etapas_coletadas):
                        etapa_encontrada = sm.etapas_coletadas[idx_fallback]
                        etapa_idx = idx_fallback

                if etapa_encontrada is None:
                    sm.tipo_interface = 'editar_etapas'
                    sm.dados_interface = {
                        'etapas': self._serializar_etapas_para_frontend(sm.etapas_coletadas)
                    }
                    return "Etapa nao encontrada.", sm

                # Abrir form pre-preenchido
                sm.estado = EstadoPOP.ETAPA_FORM
                sm._etapa_sm = None
                dados_form = self._montar_dados_etapa_form(sm, etapa_idx + 1)
                dados_form['etapa_preenchida'] = etapa_encontrada
                dados_form['editando_idx'] = etapa_idx  # para substituir no submit
                sm.tipo_interface = 'etapa_form'
                sm.dados_interface = dados_form
                resposta = f"Editando **Etapa {etapa_idx + 1}**. Ajuste os campos e confirme."
                return resposta, sm

            elif acao == 'inserir_etapa':
                # Inserir nova etapa em posicao especifica
                posicao = data.get('posicao', len(sm.etapas_coletadas))
                posicao = max(0, min(posicao, len(sm.etapas_coletadas)))
                numero_display = posicao + 1
                sm.estado = EstadoPOP.ETAPA_FORM
                sm._etapa_sm = None
                dados_form = self._montar_dados_etapa_form(sm, numero_display)
                dados_form['inserir_na_posicao'] = posicao
                sm.tipo_interface = 'etapa_form'
                sm.dados_interface = dados_form
                resposta = f"Inserindo nova etapa na **posicao {numero_display}**. Preencha o formulario."
                return resposta, sm

            elif acao == 'adicionar_etapa':
                # Iniciar nova etapa via form (no final)
                numero = len(sm.etapas_coletadas) + 1
                sm.estado = EstadoPOP.ETAPA_FORM
                sm._etapa_sm = None
                sm.tipo_interface = 'etapa_form'
                sm.dados_interface = self._montar_dados_etapa_form(sm, numero)
                resposta = f"Preencha o formulario da **Etapa {numero}**."
                return resposta, sm

        except (json.JSONDecodeError, TypeError, AttributeError):
            pass

        # Fallback: texto simples
        if msg_lower == 'cancelar':
            # Voltar para ETAPA_MAIS
            sm.estado = EstadoPOP.ETAPA_MAIS
            sm.tipo_interface = None
            sm.dados_interface = {}
            return "Ok, voltando.", sm

        # Qualquer outra coisa = confirmar
        return self._finalizar_etapas(sm)

    def _finalizar_etapas(self, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Salva etapas em dados_coletados e vai para revisão final."""
        sm.dados_coletados['etapas'] = normalizar_etapas(sm.etapas_coletadas)
        sm.estado = EstadoPOP.REVISAO_FINAL
        sm.tipo_interface = 'revisao_final'
        sm.dados_interface = self._montar_dados_revisao_final(sm)

        total = len(sm.etapas_coletadas)
        nome = sm.nome_usuario or 'você'
        resposta = (
            f"**{total} etapas** mapeadas!\n\n"
            f"Agora revise todos os dados do POP, {nome}. "
            f"Você pode editar qualquer campo antes de gerar o documento final."
        )
        return resposta, sm

    # ====================================================================
    # REVISÃO FINAL — Hub editável antes de gerar o PDF
    # ====================================================================

    def _montar_dados_revisao_final(self, sm: POPStateMachine) -> dict:
        """Monta payload completo da revisão final para o frontend."""
        dados = sm.dados_coletados
        area = sm.area_selecionada or {}
        if not sm.etapas_coletadas:
            logger.warning(f"[GUARD _montar_dados_revisao_final] etapas_coletadas VAZIO — revisao final sem etapas")

        return {
            'campos_bloqueados': {
                'codigo_processo': sm.codigo_cap or '',
                'area': area.get('nome', '') if isinstance(area, dict) else str(area),
                'area_codigo': area.get('codigo', '') if isinstance(area, dict) else '',
                'macroprocesso': sm.macro_selecionado or '',
                'processo_especifico': sm.processo_selecionado or '',
                'subprocesso': sm.subprocesso_selecionado or '',
                'atividade': sm.atividade_selecionada or '',
            },
            'campos_editaveis_inline': {
                'nome_processo': dados.get('nome_processo', '') or sm.atividade_selecionada or '',
                'entrega_esperada': dados.get('entrega_esperada', ''),
                'dispositivos_normativos': '; '.join(dados.get('dispositivos_normativos', [])) if isinstance(dados.get('dispositivos_normativos'), list) else dados.get('dispositivos_normativos', ''),
                'pontos_atencao': dados.get('pontos_atencao', ''),
            },
            'campos_editaveis_secao': {
                'sistemas': dados.get('sistemas', []),
                'operadores': dados.get('operadores', []),
                'fluxos_entrada': dados.get('fluxos_entrada', []),
                'fluxos_saida': dados.get('fluxos_saida', []),
                'etapas': self._serializar_etapas_para_frontend(sm.etapas_coletadas),
            },
            'total_etapas': len(sm.etapas_coletadas),
        }

    def _processar_revisao_final(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Hub de revisão final. Aceita ações JSON do frontend:
        - editar_inline: salva campo texto diretamente
        - editar_secao: redireciona para editor original com return_to
        - finalizar: conclui o POP e vai para FINALIZADO
        """
        msg_lower = mensagem.lower().strip()
        nome = sm.nome_usuario or 'você'

        # Tentar parsear JSON
        try:
            data = json.loads(mensagem)
            acao = data.get('acao', '')
        except (json.JSONDecodeError, TypeError):
            data = None
            acao = ''

        # --- Edição inline de campos texto ---
        if acao == 'editar_inline':
            campo = data.get('campo', '')
            valor = data.get('valor', '')
            campos_permitidos = ['nome_processo', 'entrega_esperada', 'dispositivos_normativos', 'pontos_atencao']

            if campo not in campos_permitidos:
                sm.tipo_interface = 'revisao_final'
                sm.dados_interface = self._montar_dados_revisao_final(sm)
                return f"Campo '{campo}' não pode ser editado inline.", sm

            # Salvar: dispositivos_normativos é lista no backend
            if campo == 'dispositivos_normativos':
                sm.dados_coletados[campo] = [n.strip() for n in valor.split(';') if n.strip()]
            else:
                sm.dados_coletados[campo] = valor.strip()

            sm.tipo_interface = 'revisao_final'
            sm.dados_interface = self._montar_dados_revisao_final(sm)
            return f"Campo atualizado!", sm

        # --- Editar seção complexa: redireciona para o editor original ---
        if acao == 'editar_secao':
            secao = data.get('secao', '')
            sm.return_to = EstadoPOP.REVISAO_FINAL.value

            secao_map = {
                'sistemas': (EstadoPOP.SISTEMAS, 'sistemas', {
                    'sistemas_por_categoria': self.SISTEMAS_DECIPEX,
                    'campo_livre': True,
                    'multipla_selecao': True
                }),
                'operadores': (EstadoPOP.OPERADORES, 'operadores', {
                    'opcoes': self.OPERADORES_DECIPEX,
                    'campo_livre': True,
                    'multipla_selecao': True
                }),
                'fluxos_entrada': (EstadoPOP.FLUXOS, 'fluxos_entrada', None),
                'fluxos_saida': (EstadoPOP.FLUXOS, 'fluxos_saida', None),
                'etapas': (EstadoPOP.ETAPA_REVISAO, 'editar_etapas', {
                    'etapas': self._serializar_etapas_para_frontend(sm.etapas_coletadas)
                }),
            }

            if secao not in secao_map:
                sm.tipo_interface = 'revisao_final'
                sm.dados_interface = self._montar_dados_revisao_final(sm)
                return f"Seção '{secao}' não reconhecida.", sm

            novo_estado, tipo_iface, dados_iface = secao_map[secao]
            sm.estado = novo_estado

            # Fluxos: limpar dados prévios para re-coletar
            if secao == 'fluxos_entrada':
                sm.dados_coletados['fluxos_entrada'] = []
                sm.dados_coletados.pop('fluxos_entrada_estruturados', None)
                try:
                    areas_org = carregar_areas_organizacionais()
                    orgaos = carregar_orgaos_centralizados()
                    canais = carregar_canais_atendimento()
                except Exception:
                    areas_org, orgaos, canais = {}, [], []
                sm.tipo_interface = 'fluxos_entrada'
                sm.dados_interface = {
                    'areas_organizacionais': list(areas_org.values()) if isinstance(areas_org, dict) else areas_org,
                    'orgaos_centralizados': orgaos,
                    'canais_atendimento': canais
                }
                return "Edite os fluxos de entrada.", sm

            if secao == 'fluxos_saida':
                sm.dados_coletados['fluxos_saida'] = []
                try:
                    areas_org = carregar_areas_organizacionais()
                    orgaos = carregar_orgaos_centralizados()
                    canais = carregar_canais_atendimento()
                except Exception:
                    areas_org, orgaos, canais = {}, [], []
                sm.tipo_interface = 'fluxos_saida'
                sm.dados_interface = {
                    'areas_organizacionais': list(areas_org.values()) if isinstance(areas_org, dict) else areas_org,
                    'orgaos_centralizados': orgaos,
                    'canais_atendimento': canais,
                    'fluxos_entrada': sm.dados_coletados.get('fluxos_entrada', []),
                    'fluxos_entrada_estruturados': sm.dados_coletados.get('fluxos_entrada_estruturados', [])
                }
                return "Edite os fluxos de saída.", sm

            sm.tipo_interface = tipo_iface
            sm.dados_interface = dados_iface or {}
            return f"Editando {secao}.", sm

        # --- Finalizar: gerar PDF ---
        if acao == 'finalizar' or msg_lower in ['finalizar', 'gerar pdf']:
            sm.dados_coletados['etapas'] = normalizar_etapas(sm.etapas_coletadas)
            sm.estado = EstadoPOP.FINALIZADO
            sm.concluido = True
            sm.tipo_interface = 'final'
            sm.dados_interface = {
                'codigo': sm.codigo_cap or 'POP',
                'nome_processo': sm.dados_coletados.get('nome_processo', ''),
                'total_etapas': len(sm.etapas_coletadas),
                'pop_completo': sm.dados_coletados,
            }
            total = len(sm.etapas_coletadas)
            resposta = (
                f"**Mapeamento concluído, {nome}!**\n\n"
                f"**{total} etapas** mapeadas com sucesso!\n\n"
                f"Gerando seu POP..."
            )
            return resposta, sm

        # --- Voltar para edição de etapas ---
        if acao == 'voltar_etapas' or msg_lower == 'voltar_etapas':
            sm.estado = EstadoPOP.ETAPA_REVISAO
            sm.tipo_interface = 'editar_etapas'
            sm.dados_interface = {
                'etapas': self._serializar_etapas_para_frontend(sm.etapas_coletadas)
            }
            return "Voltando para edição de etapas.", sm

        # --- Fallback: não reconheceu ação ---
        sm.tipo_interface = 'revisao_final'
        sm.dados_interface = self._montar_dados_revisao_final(sm)
        return (
            f"Revise os dados abaixo, {nome}. "
            f"Edite o que precisar e clique em **Finalizar e Gerar PDF** quando estiver pronto."
        ), sm

    # ====================================================================
    # ETAPA FORM — 1 tela por etapa (campos lineares)
    # ====================================================================

    @staticmethod
    def _formatar_resumo_etapa(etapa: dict) -> str:
        """Formata resumo rico de uma etapa com TODOS os dados vinculados."""
        numero = etapa.get('numero', '?')
        descricao = etapa.get('acao_principal', '') or etapa.get('descricao', '')
        op = etapa.get('operador_nome', '')
        sistemas = etapa.get('sistemas', [])
        docs_req = etapa.get('docs_requeridos', [])
        docs_ger = etapa.get('docs_gerados', [])
        detalhes = etapa.get('verificacoes', []) or etapa.get('detalhes', [])
        tempo = etapa.get('tempo_estimado', None)
        is_condicional = etapa.get('tipo') == 'condicional'

        linhas = [
            f"\nEtapa {numero} completa!\n",
            f"**Resumo:**",
            f"- **Acao operacional:** {descricao}",
            f"- **Responsavel:** {op or 'Nao especificado'}",
            f"- **Sistemas:** {', '.join(sistemas) if sistemas else 'Nenhum'}",
        ]

        if docs_req:
            linhas.append(f"- **Docs consultados/recebidos:** {', '.join(docs_req)}")
        if docs_ger:
            linhas.append(f"- **Docs produzidos:** {', '.join(docs_ger)}")
        if tempo:
            linhas.append(f"- **Tempo estimado:** {tempo}")

        if is_condicional:
            linhas.append(f"- **Caminhos diferentes:** Sim")
            antes = etapa.get('antes_decisao')
            if antes and antes.get('descricao'):
                linhas.append(f"- **Antes da decisao:** {antes['descricao']}")
            cenarios = etapa.get('cenarios', [])
            for c in cenarios:
                c_num = c.get('numero', '?')
                c_desc = c.get('descricao', '')
                linhas.append(f"  - **Cenario {c_num}:** {c_desc}")
                subs = c.get('subetapas', [])
                for sub in subs:
                    s_num = sub.get('numero', '?')
                    s_desc = sub.get('descricao', '')
                    linhas.append(f"    - {s_num} {s_desc}")
        else:
            if detalhes:
                linhas.append(f"- **Detalhes/variacoes:**")
                for d in detalhes:
                    linhas.append(f"  - {d}")

        return '\n'.join(linhas) + '\n'

    @staticmethod
    def _consolidar_documentos(sm: POPStateMachine) -> None:
        """
        Consolida docs de todas as etapas em sm.dados_coletados['documentos_utilizados'].
        Deduplicado por (nome_doc, tipo_uso), mantendo ordem de aparição.
        Formato de saída: lista de {tipo_documento, descricao, tipo_uso, obrigatorio, sistema}.
        """
        vistos: set = set()
        consolidados: list = []

        for etapa in sm.etapas_coletadas:
            for doc_str in etapa.get('docs_requeridos', []):
                chave = (doc_str, 'Utilizado')
                if chave not in vistos:
                    vistos.add(chave)
                    if ': ' in doc_str:
                        tipo, descricao = doc_str.split(': ', 1)
                    else:
                        tipo, descricao = doc_str, ''
                    consolidados.append({
                        'tipo_documento': tipo,
                        'descricao': descricao,
                        'tipo_uso': 'Utilizado',
                        'obrigatorio': True,
                        'sistema': '',
                    })

            for doc_str in etapa.get('docs_gerados', []):
                chave = (doc_str, 'Gerado')
                if chave not in vistos:
                    vistos.add(chave)
                    if ': ' in doc_str:
                        tipo, descricao = doc_str.split(': ', 1)
                    else:
                        tipo, descricao = doc_str, ''
                    consolidados.append({
                        'tipo_documento': tipo,
                        'descricao': descricao,
                        'tipo_uso': 'Gerado',
                        'obrigatorio': True,
                        'sistema': '',
                    })

        sm.dados_coletados['documentos_utilizados'] = consolidados

    def _montar_dados_etapa_form(self, sm: POPStateMachine, numero: int) -> dict:
        """Monta dados_interface para o form de etapa."""
        # Sumário de etapas já mapeadas (para navegação no topo do form)
        etapas_sumario = [
            {
                'numero': e.get('numero', str(i + 1)),
                'acao_principal': e.get('acao_principal', e.get('descricao', ''))[: 40],
            }
            for i, e in enumerate(sm.etapas_coletadas)
        ]
        return {
            'numero_etapa': numero,
            'total_etapas': len(sm.etapas_coletadas),
            'etapas_sumario': etapas_sumario,
            'operadores': sm.dados_coletados.get('operadores', []),
            'sistemas': carregar_sistemas(),
            'tipos_documentos_requeridos': carregar_tipos_documentos_requeridos(),
            'tipos_documentos_gerados': carregar_tipos_documentos_gerados(),
        }

    def _processar_etapa_form(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Handler do submit do ETAPA_FORM.
        Recebe JSON {"etapa": {...}} e persiste em etapas[].
        Se is_condicional: inicia SM no TIPO_CONDICIONAL.
        Senao: vai para ETAPA_MAIS.
        """
        # Interceptar comandos especiais (botões residuais)
        msg_lower = mensagem.lower().strip()
        if msg_lower == '__finalizar_etapas__':
            if not sm.etapas_coletadas:
                return "Nenhuma etapa foi mapeada ainda. Preencha o formulario.", sm
            sm.estado = EstadoPOP.ETAPA_REVISAO
            sm.tipo_interface = 'editar_etapas'
            sm.dados_interface = {
                'etapas': self._serializar_etapas_para_frontend(sm.etapas_coletadas)
            }
            total = len(sm.etapas_coletadas)
            return f"{total} {'etapa mapeada' if total == 1 else 'etapas mapeadas'}. Revise abaixo.", sm

        # Parse JSON do form
        try:
            data = json.loads(mensagem)
            etapa_data = data.get('etapa', {})
        except (json.JSONDecodeError, TypeError):
            return "Erro ao processar dados. Preencha o formulario e confirme.", sm

        # Validar acao_principal (fallback descricao para retrocompat)
        descricao = (etapa_data.get('acao_principal') or etapa_data.get('descricao') or '').strip()
        if not descricao:
            return "A acao principal da etapa e obrigatoria.", sm

        # Normalizar verificacoes (fallback detalhes para retrocompat)
        detalhes_raw = etapa_data.get('verificacoes') or etapa_data.get('detalhes', [])
        if isinstance(detalhes_raw, str):
            detalhes = [l.strip() for l in detalhes_raw.split('\n') if l.strip()]
        else:
            detalhes = [str(d).strip() for d in detalhes_raw if str(d).strip()]

        # Detectar se estamos editando uma etapa existente
        editando_idx = sm.dados_interface.get('editando_idx') if sm.dados_interface else None
        etapa_id_existente = etapa_data.get('id')

        if editando_idx is not None and 0 <= editando_idx < len(sm.etapas_coletadas):
            # MODO EDICAO: substituir etapa existente
            numero = editando_idx + 1
            etapa_existente = sm.etapas_coletadas[editando_idx]
            etapa_obj = {
                **etapa_existente,  # preservar campos que o form nao envia
                'numero': str(numero),
                'acao_principal': descricao,
                'descricao': descricao,
                'operador_nome': (etapa_data.get('operador_nome') or 'Nao especificado').strip(),
                'sistemas': etapa_data.get('sistemas', []),
                'docs_requeridos': etapa_data.get('docs_requeridos', []),
                'docs_gerados': etapa_data.get('docs_gerados', []),
                'tempo_estimado': (etapa_data.get('tempo_estimado') or '').strip() or None,
                'verificacoes': detalhes,
                'detalhes': detalhes,
            }
            # Preservar id original
            if etapa_id_existente:
                etapa_obj['id'] = etapa_id_existente

            # Processar condicional do form
            is_cond_edit = etapa_data.get('is_condicional', False)
            if is_cond_edit:
                cenarios_input = etapa_data.get('cenarios_input', [])
                cenarios_fmt = []
                for idx_c, ci in enumerate(cenarios_input, 1):
                    cond = ci.get('condicao', '').strip() if isinstance(ci, dict) else ''
                    acao_c = ci.get('acao', '').strip() if isinstance(ci, dict) else ''
                    if cond or acao_c:
                        desc_c = f"Se {cond} \u2192 {acao_c}" if cond and acao_c else cond or acao_c
                        cenarios_fmt.append({'numero': str(idx_c), 'descricao': desc_c, 'subetapas': []})
                etapa_obj['tipo'] = 'condicional'
                etapa_obj['tipo_condicional'] = 'binario' if len(cenarios_fmt) <= 2 else 'multiplos'
                etapa_obj['antes_decisao'] = {'numero': str(numero), 'descricao': descricao}
                etapa_obj['cenarios'] = cenarios_fmt
            else:
                # Limpar condicionais se usuario desmarcou
                etapa_obj.pop('tipo', None)
                etapa_obj.pop('tipo_condicional', None)
                etapa_obj.pop('antes_decisao', None)
                etapa_obj.pop('cenarios', None)

            etapa_obj = normalizar_etapa(etapa_obj, numero)
            sm.etapas_coletadas[editando_idx] = etapa_obj
            self._consolidar_documentos(sm)

            # Voltar para revisao
            sm.estado = EstadoPOP.ETAPA_REVISAO
            sm.tipo_interface = 'editar_etapas'
            sm.dados_interface = {
                'etapas': self._serializar_etapas_para_frontend(sm.etapas_coletadas)
            }
            return f"Etapa {numero} atualizada. Revise abaixo.", sm

        # MODO NOVO: montar etapa e inserir na posicao correta
        inserir_na_posicao = sm.dados_interface.get('inserir_na_posicao') if sm.dados_interface else None
        numero = len(sm.etapas_coletadas) + 1
        etapa_obj = {
            'numero': str(numero),
            'acao_principal': descricao,
            'descricao': descricao,  # alias retrocompat
            'operador_nome': (etapa_data.get('operador_nome') or 'Nao especificado').strip(),
            'sistemas': etapa_data.get('sistemas', []),
            'docs_requeridos': etapa_data.get('docs_requeridos', []),
            'docs_gerados': etapa_data.get('docs_gerados', []),
            'tempo_estimado': (etapa_data.get('tempo_estimado') or '').strip() or None,
            'verificacoes': detalhes,
            'detalhes': detalhes,  # alias retrocompat
        }

        # Normalizar e inserir (na posicao especifica ou ao final)
        etapa_obj = normalizar_etapa(etapa_obj, numero)
        if inserir_na_posicao is not None and 0 <= inserir_na_posicao <= len(sm.etapas_coletadas):
            sm.etapas_coletadas.insert(inserir_na_posicao, etapa_obj)
            # Renumerar todas as etapas
            for i, e in enumerate(sm.etapas_coletadas, 1):
                e['numero'] = str(i)
                e['ordem'] = i
            etapa_index = inserir_na_posicao
        else:
            sm.etapas_coletadas.append(etapa_obj)
            etapa_index = len(sm.etapas_coletadas) - 1
        self._consolidar_documentos(sm)

        is_condicional = etapa_data.get('is_condicional', False)

        if is_condicional:
            # Processar cenarios diretamente do form (Block 3)
            cenarios_input = etapa_data.get('cenarios_input', [])
            cenarios_formatados = []
            for idx_c, ci in enumerate(cenarios_input, 1):
                condicao = ci.get('condicao', '').strip() if isinstance(ci, dict) else ''
                acao_c = ci.get('acao', '').strip() if isinstance(ci, dict) else ''
                if condicao or acao_c:
                    desc = f"Se {condicao} \u2192 {acao_c}" if condicao and acao_c else condicao or acao_c
                    cenarios_formatados.append({
                        'numero': str(idx_c),
                        'descricao': desc,
                        'subetapas': []
                    })

            # Atualizar etapa com dados condicionais
            etapa_obj['tipo'] = 'condicional'
            etapa_obj['tipo_condicional'] = 'binario' if len(cenarios_formatados) <= 2 else 'multiplos'
            etapa_obj['antes_decisao'] = {
                'numero': str(numero),
                'descricao': etapa_obj.get('acao_principal', '')
            }
            etapa_obj['cenarios'] = cenarios_formatados
            sm.etapas_coletadas[etapa_index] = normalizar_etapa(etapa_obj, numero)

        # Ir para ETAPA_MAIS (proximo ou finalizar)
        sm._etapa_sm = None
        sm.estado = EstadoPOP.ETAPA_MAIS

        # Numero real da etapa (pode diferir apos insercao no meio)
        numero_real = int(sm.etapas_coletadas[etapa_index].get('numero', etapa_index + 1))
        total = len(sm.etapas_coletadas)
        resposta = self._formatar_resumo_etapa(etapa_obj)

        sm.tipo_interface = 'confirmacao_dupla'
        sm.dados_interface = {
            'botao_terceiro': f'Editar Etapa {numero_real}',
            'valor_terceiro': '__editar_ultima_etapa__',
            'ultimo_etapa_idx': etapa_index,  # indice real para editar
            'botao_editar': 'Finalizar etapas',
            'valor_editar': '__finalizar_etapas__',
            'botao_confirmar': f'Adicionar Etapa {total + 1}',
            'valor_confirmar': '__proxima_etapa__'
        }

        return resposta, sm

    def _definir_interface_etapa(self, etapa_sm: EtapaStateMachine, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Define tipo_interface e dados_interface para cada estado
        da EtapaStateMachine, conectando aos componentes React existentes.
        """
        numero = etapa_sm.numero

        # Limpar interface anterior
        sm.tipo_interface = None
        sm.dados_interface = {}

        if etapa_sm.estado == EstadoEtapa.OPERADOR:
            # Interface rica com lista de operadores já coletados
            operadores = sm.dados_coletados.get('operadores', [])
            if operadores:
                sm.tipo_interface = 'operadores_etapa'
                sm.dados_interface = {
                    'numero_etapa': numero,
                    'opcoes': operadores
                }
                resposta = None  # Interface substitui texto
            else:
                resposta = (
                    f"👤 **Etapa {numero} — Quem EXECUTA esta etapa?**\n\n"
                    f"_Informe o cargo, função ou pessoa responsável._"
                )

        elif etapa_sm.estado == EstadoEtapa.SISTEMAS:
            # (A) Texto livre, sem interface 'sistemas'
            resposta = (
                f"💻 **Etapa {numero} — Quais SISTEMAS são utilizados?**\n\n"
                f"_Digite separados por vírgula, ou 'nenhum'_\n\n"
                f"**Exemplos:** SEI, SIAFI, SIGA, Sigepe"
            )

        elif etapa_sm.estado == EstadoEtapa.DOCS_REQUERIDOS:
            tipos_docs = carregar_tipos_documentos_requeridos()
            sm.tipo_interface = 'docs_requeridos_etapa'
            sm.dados_interface = {
                'numero_etapa': numero,
                'modo': 'requeridos',
                'tipos_documentos': tipos_docs,
            }
            resposta = None

        elif etapa_sm.estado == EstadoEtapa.DOCS_GERADOS:
            tipos_docs = carregar_tipos_documentos_gerados()
            sm.tipo_interface = 'docs_gerados_etapa'
            sm.dados_interface = {
                'numero_etapa': numero,
                'modo': 'gerados',
                'tipos_documentos': tipos_docs,
            }
            resposta = None

        elif etapa_sm.estado == EstadoEtapa.TEMPO_ESTIMADO:
            resposta = (
                f"⏱️ **Etapa {numero} — Qual o TEMPO ESTIMADO?**\n\n"
                f"_Exemplos: 15 minutos, 2 horas, 1 dia útil, ou 'pular'_"
            )

        elif etapa_sm.estado == EstadoEtapa.PERGUNTA_CONDICIONAL:
            sm.tipo_interface = 'condicionais_etapa'
            sm.dados_interface = {'numero_etapa': numero}
            resposta = None

        elif etapa_sm.estado == EstadoEtapa.TIPO_CONDICIONAL:
            sm.tipo_interface = 'tipo_condicional'
            sm.dados_interface = {'numero_etapa': numero}
            resposta = None

        elif etapa_sm.estado == EstadoEtapa.ANTES_DECISAO:
            resposta = (
                f"⚙️ **Etapa {numero} — O que é feito ANTES da decisão?**\n\n"
                f"_Exemplo: Analisar conformidade documental_"
            )

        elif etapa_sm.estado == EstadoEtapa.CENARIOS:
            antes = etapa_sm.antes_decisao or ''
            if etapa_sm.tipo_condicional == 'binario':
                sm.tipo_interface = 'cenarios_binario'
                sm.dados_interface = {
                    'numero_etapa': numero,
                    'antes_decisao': antes
                }
            else:
                sm.tipo_interface = 'cenarios_multiplos_quantidade'
                sm.dados_interface = {
                    'numero_etapa': numero,
                    'antes_decisao': antes,
                    'quantidade': 3
                }
            resposta = None

        elif etapa_sm.estado == EstadoEtapa.SUBETAPAS_CENARIO:
            idx = etapa_sm._cenario_index
            if idx < len(etapa_sm.cenarios):
                cenario_atual = etapa_sm.cenarios[idx]
                sm.tipo_interface = 'subetapas_cenario'
                sm.dados_interface = {
                    'numero_cenario': cenario_atual.numero,
                    'descricao_cenario': cenario_atual.descricao,
                    'todos_cenarios': [
                        {'numero': c.numero, 'descricao': c.descricao}
                        for c in etapa_sm.cenarios
                    ],
                    'cenario_atual_index': idx
                }
                resposta = None
            else:
                resposta = "Processando cenários..."

        elif etapa_sm.estado == EstadoEtapa.DETALHES:
            resposta = (
                f"📝 **Etapa {numero} — Quer adicionar DETALHES?**\n\n"
                f"_Pequenas ações dentro da etapa. Digite um detalhe ou 'não'._"
            )

        else:
            resposta = "Processando..."

        return resposta, sm

    def _serializar_etapas_para_frontend(self, etapas: list) -> list:
        """Serializa etapas para frontend — retorna dados completos normalizados."""
        return normalizar_etapas(etapas)

    # ========================================================================
    # HELPERS
    # ========================================================================


    def _buscar_linha_arquitetura(self, sm: POPStateMachine):
        """Busca linha no CSV da arquitetura pelo filtro hierárquico."""
        filtro = (
            (self.arquitetura.df['Macroprocesso'] == sm.macro_selecionado) &
            (self.arquitetura.df['Processo'] == sm.processo_selecionado) &
            (self.arquitetura.df['Subprocesso'] == sm.subprocesso_selecionado) &
            (self.arquitetura.df['Atividade'] == sm.atividade_selecionada)
        )
        return self.arquitetura.df[filtro]

    def _gerar_codigo_processo(self, sm: POPStateMachine) -> str:
        """Gera código CAP (Código na Arquitetura de Processos) automaticamente."""
        area_info = sm.area_selecionada
        if not area_info:
            return "X.X.X.X.X"

        prefixo = area_info.get("prefixo", "X")
        logger.info(f"[CAP] Buscando: {sm.macro_selecionado}/{sm.processo_selecionado}/{sm.subprocesso_selecionado}/{sm.atividade_selecionada}")

        # Tentar buscar código direto no CSV
        try:
            linha = self._buscar_linha_arquitetura(sm)
            if not linha.empty:
                # Buscar coluna Codigo (case insensitive)
                col_codigo = next((c for c in linha.columns if c.lower() == 'codigo'), None)
                if col_codigo:
                    codigo_csv = linha[col_codigo].iloc[0]
                    if not self._codigo_existe_no_banco(codigo_csv):
                        logger.info(f"[CAP] Encontrado no CSV: {codigo_csv}")
                        return codigo_csv
        except Exception as e:
            logger.error(f"[CAP] Erro ao buscar no CSV: {e}")

        # Gerar código baseado em numeração do CSV ou índices dinâmicos
        try:
            linha = self._buscar_linha_arquitetura(sm)
            if not linha.empty and 'Numero' in linha.columns:
                partes = str(linha.iloc[0]['Numero']).split('.')
                if len(partes) >= 4:
                    codigo_base = f"{prefixo}.{partes[0]}.{partes[1]}.{partes[2]}.{partes[3]}"
                else:
                    raise ValueError("Formato inválido")
            else:
                raise ValueError("Numeração não encontrada")
        except (ValueError, IndexError, KeyError):
            # Fallback: gerar índices dinamicamente
            logger.warning("[CAP] Gerando código dinamicamente")
            def idx(lista, valor):
                return lista.index(valor) + 1 if valor in lista else 1

            macros = self.arquitetura.obter_macroprocessos_unicos()
            processos = self.arquitetura.obter_processos_por_macro(sm.macro_selecionado)
            subprocessos = self.arquitetura.obter_subprocessos_por_processo(sm.macro_selecionado, sm.processo_selecionado)
            atividades = self.arquitetura.obter_atividades_por_subprocesso(sm.macro_selecionado, sm.processo_selecionado, sm.subprocesso_selecionado)

            codigo_base = f"{prefixo}.{idx(macros, sm.macro_selecionado)}.{idx(processos, sm.processo_selecionado)}.{idx(subprocessos, sm.subprocesso_selecionado)}.{idx(atividades, sm.atividade_selecionada)}"

        # Validar duplicatas e incrementar sufixo se necessário
        codigo_final = codigo_base
        for sufixo in range(1, 51):
            if not self._codigo_existe_no_banco(codigo_final):
                break
            codigo_final = f"{codigo_base}-{sufixo}"

        logger.info(f"[CAP] Gerado: {codigo_final}")
        return codigo_final

    def _codigo_existe_no_banco(self, codigo: str) -> bool:
        """Verifica se código CAP já existe no banco de dados"""
        try:
            from processos.models import POP
            return POP.objects.filter(
                codigo_processo=codigo,
                is_deleted=False
            ).exists()
        except:
            # Se houver erro na consulta, não bloquear a geração
            return False

    def _calcular_progresso(self, sm: POPStateMachine) -> str:
        """Calcula progresso da coleta baseado em campos preenchidos.

        Peso: pré-etapas = 30%, etapas = 70%.
        """
        d = sm.dados_coletados
        campos_pre = [
            sm.nome_usuario,
            d.get('area_decipex'),
            d.get('macroprocesso'),
            d.get('processo'),
            d.get('subprocesso'),
            d.get('atividade'),
            d.get('nome_processo'),
            d.get('entrega_esperada'),
            d.get('dispositivos_normativos'),
            d.get('operadores'),
            d.get('sistemas'),
            d.get('documentos_entrada') or d.get('documentos_saida'),
            d.get('fluxos_entrada') or d.get('fluxos_saida'),
        ]
        pre_preenchidos = sum(1 for c in campos_pre if c)
        total_pre = len(campos_pre)
        tem_etapas = bool(sm.etapas_coletadas)

        # Percentual ponderado: pré-etapas = 30%, etapas = 70%
        pct_pre = int((pre_preenchidos / total_pre) * 30) if total_pre else 0
        pct_etapas = 70 if tem_etapas else 0
        pct_total = pct_pre + pct_etapas

        return f"{pct_total}/100"

    def obter_progresso(self, sm: POPStateMachine) -> dict:
        """Retorna detalhes completos do progresso atual.

        Peso: pré-etapas = 30%, etapas = 70%.
        """
        d = sm.dados_coletados
        campos_pre = [
            ('Nome do usuário', sm.nome_usuario),
            ('Área DECIPEX', d.get('area_decipex')),
            ('Macroprocesso', d.get('macroprocesso')),
            ('Processo', d.get('processo')),
            ('Subprocesso', d.get('subprocesso')),
            ('Atividade', d.get('atividade')),
            ('Nome do processo', d.get('nome_processo')),
            ('Entrega esperada', d.get('entrega_esperada')),
            ('Dispositivos normativos', d.get('dispositivos_normativos')),
            ('Operadores', d.get('operadores')),
            ('Sistemas', d.get('sistemas')),
            ('Documentos', d.get('documentos_entrada') or d.get('documentos_saida')),
            ('Fluxos', d.get('fluxos_entrada') or d.get('fluxos_saida')),
        ]
        pre_preenchidos = sum(1 for _, v in campos_pre if v)
        faltantes = [nome for nome, v in campos_pre if not v]
        total_pre = len(campos_pre)
        tem_etapas = bool(sm.etapas_coletadas)

        # Percentual ponderado: pré-etapas = 30%, etapas = 70%
        pct_pre = int((pre_preenchidos / total_pre) * 30) if total_pre else 0
        pct_etapas = 70 if tem_etapas else 0
        percentual = pct_pre + pct_etapas

        if not tem_etapas:
            faltantes.append('Etapas')

        # Detalhe de etapas em andamento
        etapa_info = ""
        if sm.estado.value.startswith('etapa_'):
            n_etapas = len(sm.etapas_coletadas)
            etapa_info = f" (coletando etapa {n_etapas + 1})"

        return {
            "campos_preenchidos": pre_preenchidos + (1 if tem_etapas else 0),
            "total_campos": total_pre + 1,
            "percentual": percentual,
            "estado_atual": sm.estado.value,
            "campos_faltantes": faltantes,
            "etapa_info": etapa_info,
            "completo": sm.estado in (EstadoPOP.DELEGACAO_ETAPAS, EstadoPOP.FINALIZADO) or percentual == 100
        }

    def _preparar_dados_formulario(self, sm: POPStateMachine) -> dict:
        """
        Prepara dados do POP para o FormularioPOP.tsx (PREENCHIMENTO EM TEMPO REAL)

        Este método retorna SEMPRE os dados coletados até o momento, permitindo
        que o frontend mostre o formulário sendo preenchido em tempo real.

        Returns:
            dict: Dados formatados para o FormularioPOP.tsx
        """
        dados = sm.dados_coletados
        logger.info(f"[_preparar_dados_formulario] dados_coletados.operadores = {dados.get('operadores')}")
        logger.info(f"[_preparar_dados_formulario] dados_coletados.fluxos_entrada = {dados.get('fluxos_entrada')}")
        logger.info(f"[_preparar_dados_formulario] dados_coletados.fluxos_saida = {dados.get('fluxos_saida')}")
        area_info = sm.area_selecionada or {}

        # Gerar código CAP se ainda não foi gerado
        codigo_cap = sm.codigo_cap if sm.codigo_cap else "Aguardando..."

        etapas_out = sm.etapas_coletadas if sm.etapas_coletadas else []
        if not etapas_out and sm.estado.value in ('etapa_revisao', 'revisao_final', 'finalizado'):
            logger.warning(f"[GUARD _preparar_dados_formulario] etapas VAZIO no estado {sm.estado} — possivel sessao corrompida")

        return {
            # Identificação
            "codigo_cap": codigo_cap,
            "codigo_processo": codigo_cap,
            "area": {
                "nome": area_info.get("nome", ""),
                "codigo": area_info.get("codigo", "")
            },
            "macroprocesso": sm.macro_selecionado or "",
            "processo": sm.processo_selecionado or "",
            "processo_especifico": sm.processo_selecionado or "",
            "subprocesso": sm.subprocesso_selecionado or "",
            "atividade": sm.atividade_selecionada or "",

            # Dados coletados
            "nome_processo": dados.get("nome_processo", "") or sm.atividade_selecionada or "",
            "entrega_esperada": dados.get("entrega_esperada", ""),
            "dispositivos_normativos": dados.get("dispositivos_normativos", []),
            "operadores": dados.get("operadores", []),
            "sistemas": dados.get("sistemas", []),
            "documentos_utilizados": dados.get("documentos_utilizados", []),
            "fluxos_entrada": dados.get("fluxos_entrada", []),
            "fluxos_saida": dados.get("fluxos_saida", []),
            "pontos_atencao": dados.get("pontos_atencao", ""),

            # Etapas inline (schema completo)
            "etapas": etapas_out,

            # Metadados
            "nome_usuario": sm.nome_usuario or "",
            "versao": "1.0",
            "data_criacao": "",

            # Estado do preenchimento
            "campo_atual": self._obter_campo_atual(sm.estado),
            "percentual_conclusao": self._calcular_progresso(sm)
        }

    def _obter_campo_atual(self, estado: EstadoPOP) -> str:
        """Retorna qual campo está sendo preenchido no momento"""
        mapa_campos = {
            EstadoPOP.NOME_USUARIO: "nome_usuario",
            EstadoPOP.AREA_DECIPEX: "area",
            EstadoPOP.ARQUITETURA: "arquitetura",
            EstadoPOP.NOME_PROCESSO: "nome_processo",
            EstadoPOP.ENTREGA_ESPERADA: "entrega_esperada",
            EstadoPOP.DISPOSITIVOS_NORMATIVOS: "dispositivos_normativos",
            EstadoPOP.OPERADORES: "operadores",
            EstadoPOP.SISTEMAS: "sistemas",
            EstadoPOP.FLUXOS: "fluxos",
            EstadoPOP.PONTOS_ATENCAO: "pontos_atencao",
        }
        # Estados de etapa inline → campo "etapas"
        if estado.value.startswith('etapa_'):
            return "etapas"
        return mapa_campos.get(estado, "")

    def _gerar_resumo_pop(self, sm: POPStateMachine) -> str:
        """Gera resumo completo dos dados coletados (FORMULÁRIO POP COMPLETO)"""
        dados = sm.dados_coletados

        # Gerar código CAP se ainda não foi gerado
        if not sm.codigo_cap:
            sm.codigo_cap = self._gerar_codigo_processo(sm)

        resumo = "**📋 RESUMO DO PROCESSO (POP)**\n\n"

        # 1. IDENTIFICAÇÃO
        resumo += f"**🔖 Código CAP:** {sm.codigo_cap}\n"
        resumo += f"**📍 Área:** {sm.area_selecionada['nome']} ({sm.area_selecionada['codigo']})\n"
        resumo += f"**📂 Macroprocesso:** {sm.macro_selecionado}\n"
        resumo += f"**📁 Processo:** {sm.processo_selecionado}\n"
        resumo += f"**📄 Subprocesso:** {sm.subprocesso_selecionado}\n"
        resumo += f"**⚙️ Atividade:** {sm.atividade_selecionada}\n\n"

        # 2. ENTREGA ESPERADA
        resumo += f"**🎯 Entrega Esperada:**\n{dados['entrega_esperada']}\n\n"

        # 3. SISTEMAS
        resumo += f"**💻 Sistemas:**\n{', '.join(dados['sistemas'])}\n\n"

        # 4. NORMAS
        resumo += f"**📚 Normas:**\n{'; '.join(dados['dispositivos_normativos'])}\n\n"

        # 5. OPERADORES
        resumo += f"**👥 Operadores:**\n{'; '.join(dados['operadores'])}\n\n"

        # 6. ENTRADA (De quais áreas recebe insumos)
        if dados.get('fluxos_entrada'):
            resumo += f"**📥 Entrada:**\n{'; '.join(dados['fluxos_entrada'])}\n\n"

        # 7. SAÍDA (Para quais áreas entrega resultados)
        if dados.get('fluxos_saida'):
            resumo += f"**📤 Saída:**\n{'; '.join(dados['fluxos_saida'])}\n\n"

        # 8. DOCUMENTOS
        if dados.get('documentos'):
            resumo += f"**📄 Documentos:**\n{'; '.join(dados['documentos'])}\n\n"

        # 9. PONTOS DE ATENÇÃO (já coletados)
        pontos = dados.get('pontos_atencao', '')
        if pontos and pontos != "Não há pontos especiais de atenção.":
            # Formatar cada linha como bullet com travessão
            linhas = [l.strip() for l in pontos.split('\n') if l.strip()]
            pontos_fmt = '\n'.join(
                l if l.startswith('–') or l.startswith('-') else f"– {l}"
                for l in linhas
            )
            resumo += f"**⚠️ Pontos de Atenção:**\n{pontos_fmt}\n"
        else:
            resumo += "**⚠️ Pontos de Atenção:** nenhum informado\n"

        return resumo

    def receber_dados(self, dados_etapas: dict) -> dict:
        """
        Recebe dados de volta do Helena Etapas (quando concluir)

        Args:
            dados_etapas: Etapas coletadas pelo Helena Etapas

        Returns:
            dict: Dados consolidados do processo completo
        """
        logger.info("Helena POP recebendo dados consolidados do Helena Etapas")

        # TODO: Consolidar dados do POP + Etapas
        # TODO: Gerar documento final
        # TODO: Oferecer próximos passos (fluxograma, riscos, etc.)

        return {
            'sucesso': True,
            'mensagem': 'Processo mapeado com sucesso!',
            'dados_consolidados': dados_etapas
        }
