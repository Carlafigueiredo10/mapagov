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
)

# Tentativa de importar BaseLegalSuggestorDECIPEx (opcional)
try:
    from processos.base_legal_decipex import BaseLegalSuggestorDECIPEx
    BASE_LEGAL_DISPONIVEL = True
except ImportError:
    BASE_LEGAL_DISPONIVEL = False

logger = logging.getLogger(__name__)

logger.info("helena_pop.py carregado (v2.0)")


# ============================================================================
# CONSTANTES - Palavras-chave para detecção de intenção
# ============================================================================

PALAVRAS_CONFIRMACAO = frozenset([
    'sim', 's', 'pode', 'ok', 'claro', 'entendi', 'beleza', 'tudo',
    'concordo', 'confirmar', 'correto', 'certo', 'continuar', 'vamos',
    'seguir', 'próximo', 'conte', 'contigo', 'melhor', 'farei', 'junto',
    'tudo certo', 'ja entendi', 'já entendi', 'ok_entendi'
])
PALAVRAS_NEGACAO = frozenset(['não', 'nao', 'n', 'nenhum', 'não há', 'nao ha', 'não tem', 'nao tem', 'sem pontos', 'pular', 'skip'])
PALAVRAS_DUVIDAS = frozenset(['duvida', 'dúvida', 'duvidas', 'dúvidas', 'mais duvidas', 'mais dúvidas', 'tenho duvidas', 'tenho dúvidas'])
PALAVRAS_DETALHES = frozenset(['detalhada', 'longa', 'detalhes', 'completa', 'detalhe'])
PALAVRAS_OBJETIVA = frozenset(['objetiva', 'curta', 'rápida', 'rapida', 'resumida'])
PALAVRAS_EDICAO = frozenset(['editar', 'edit', 'corrigir', 'alterar', 'mudar', 'ajustar', 'arrumar', 'manual'])
PALAVRAS_PAUSA = frozenset(['pausa', 'pausar', 'esperar', 'depois', 'mais tarde', 'aguardar'])
PALAVRAS_CANCELAR = frozenset(['cancelar', 'voltar', 'sair'])
PALAVRAS_MAIS_PERGUNTA = frozenset(['mais_pergunta', 'mais', 'pergunta', 'tenho mais'])


# ============================================================================
# ENUMS - Estados da Conversa
# ============================================================================

class EstadoPOP(str, Enum):
    """Estados da máquina de estados para coleta do POP"""
    # BOAS_VINDAS removido - começa direto em NOME_USUARIO (evita duplicação)
    NOME_USUARIO = "nome_usuario"
    CONFIRMA_NOME = "confirma_nome"
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
        self.nome_temporario = ""
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

    def to_dict(self) -> Dict[str, Any]:
        """Serializa o state machine para JSON"""
        return {
            'estado': self.estado.value,
            'nome_usuario': self.nome_usuario,
            'nome_temporario': self.nome_temporario,
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
            'estado_helena_mapeamento': self.estado_helena_mapeamento
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'POPStateMachine':
        """Deserializa o state machine do JSON"""
        sm = cls()
        sm.estado = EstadoPOP(data.get('estado', EstadoPOP.NOME_USUARIO.value))  # ✅ FIX: default para NOME_USUARIO
        sm.nome_usuario = data.get('nome_usuario', '')
        sm.nome_temporario = data.get('nome_temporario', '')
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
        self._normas_sugeridas = set()

        # Lazy loading do pipeline de busca
        self._pipeline_instance = None

    # ========================================================================
    # HELPER - Detecção de Intenção
    # ========================================================================

    def _detectar_intencao(self, msg: str, tipo: str) -> bool:
        """
        Detecta intenção do usuário baseado em palavras-chave.

        Args:
            msg: Texto do usuário (deve estar em lowercase)
            tipo: 'confirmacao', 'negacao', 'duvidas', 'detalhes', 'objetiva',
                  'edicao', 'pausa', 'cancelar', 'mais_pergunta'

        Returns:
            True se alguma palavra-chave do tipo foi encontrada na mensagem
        """
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
        return any(palavra in msg for palavra in palavras)

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

        elif sm.estado == EstadoPOP.CONFIRMA_NOME:
            resposta, novo_sm = self._processar_confirma_nome(mensagem, sm)

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

        elif sm.estado == EstadoPOP.SELECAO_EDICAO:
            resposta, novo_sm = self._processar_selecao_edicao(mensagem, sm)

        elif sm.estado == EstadoPOP.DELEGACAO_ETAPAS:
            resposta, novo_sm = self._processar_delegacao_etapas(mensagem, sm)

        else:
            resposta = "Estado desconhecido. Vamos recomeçar?"
            novo_sm = POPStateMachine()

        # Calcular progresso
        progresso = self._calcular_progresso(novo_sm)
        progresso_detalhado = self.obter_progresso(novo_sm)

        # Verificar se deve sugerir mudança de contexto
        sugerir_contexto = None
        if novo_sm.estado == EstadoPOP.DELEGACAO_ETAPAS or novo_sm.concluido:
            sugerir_contexto = 'etapas'

        # 🎯 Inicializar variáveis de interface (serão preenchidas abaixo)
        tipo_interface = None
        dados_interface = None

        # Criar metadados_extra base (ou usar o que veio dos handlers)
        if not metadados_extra:
            metadados_extra = {}

        metadados_extra['progresso_detalhado'] = progresso_detalhado

        # Transição automática para HelenaEtapas quando POP finalizado
        if novo_sm.concluido:
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

        # Badge de conquista na transição épica
        if novo_sm.estado == EstadoPOP.TRANSICAO_EPICA:
            metadados_extra['badge'] = {
                'tipo': 'fase_previa_completa',
                'emoji': '🏆',
                'titulo': 'Fase Prévia Concluída!',
                'descricao': 'Você mapeou toda a estrutura básica do processo',
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

        elif novo_sm.estado == EstadoPOP.CONFIRMA_NOME:
            # Interface com 2 botões: Pode sim / Não, prefiro outro nome
            tipo_interface = 'confirmacao_dupla'
            dados_interface = {
                'botao_confirmar': 'Pode sim, Helena.',
                'botao_editar': 'Não, prefiro ser chamado de outro nome.',
                'valor_confirmar': 'sim',
                'valor_editar': 'não'
            }

        elif novo_sm.estado == EstadoPOP.ESCOLHA_TIPO_EXPLICACAO:
            # 🆕 Interface com 2 botões: Explicação detalhada / Explicação objetiva
            tipo_interface = 'confirmacao_dupla'
            dados_interface = {
                'botao_confirmar': '📘 Explicação detalhada',
                'botao_editar': '⚡ Explicação objetiva',
                'valor_confirmar': 'detalhada',
                'valor_editar': 'objetiva'
            }

        elif novo_sm.estado == EstadoPOP.EXPLICACAO_LONGA:
            # 🆕 Interface após explicação longa: Sim entendi / Não, tenho dúvidas
            tipo_interface = 'confirmacao_dupla'
            dados_interface = {
                'botao_confirmar': '🔹 Sim, vamos continuar!',
                'botao_editar': '🔹 Não, ainda tenho dúvidas',
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
            # Interface épica com botão pulsante e opção de pausa
            tipo_interface = 'transicao_epica'
            dados_interface = {
                'botao_principal': {
                    'texto': '🚀 VAMOS COMEÇAR!',
                    'classe': 'botao-pulsante-centro',
                    'tamanho': 'grande',
                    'cor': '#4CAF50',
                    'animacao': 'pulse',
                    'valor_enviar': 'VAMOS'
                },
                'botao_secundario': {
                    'texto': 'Preciso de uma pausa',
                    'classe': 'link-discreto',
                    'posicao': 'abaixo',
                    'valor_enviar': 'PAUSA'
                },
                'mostrar_progresso': True,
                'progresso_texto': 'Identificação concluída!',
                'background_especial': True
            }

        elif novo_sm.estado == EstadoPOP.RECONHECIMENTO_ENTREGA:
            # Gamificação após entrega esperada
            tipo_interface = 'caixinha_reconhecimento'
            dados_interface = {
                'nome_usuario': novo_sm.nome_usuario or 'você'
            }

        elif novo_sm.estado == EstadoPOP.DELEGACAO_ETAPAS:
            # Interface de transição com troféu e auto-redirect
            tipo_interface = 'transicao'
            dados_interface = {
                'proximo_modulo': 'etapas',
                'mostrar_trofeu': True,
                'mensagem_trofeu': 'Primeira Fase Concluída!',
                'auto_redirect': True,
                'delay_ms': 2000
            }

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
            # Interface rica de normas com IA
            sugestoes = self._sugerir_base_legal_contextual(novo_sm)
            grupos_normas = {}
            if self.suggestor_base_legal:
                try:
                    grupos_normas = self.suggestor_base_legal.obter_grupos_normas()
                except:
                    pass

            tipo_interface = 'normas'
            dados_interface = {
                'sugestoes': sugestoes,
                'grupos': grupos_normas,
                'campo_livre': True,
                'multipla_selecao': True,
                'texto_introducao': (
                    f"**1️⃣** Primeiro, pelo que eu entendi da sua atividade eu **sugeri normas pelo grau de aderência**. (Você concordar ou não, ok?)\n\n"
                    f"**2️⃣** Se vir que ainda faltam normas **você pode expandir e explorar a biblioteca completa de todas as normas** organizadas por categoria\n\n"
                    f"**3️⃣** Aqui minha forte recomendação: **Conversar com minha parceira do Sigepe Legis IA** (link abaixo). "
                    f"Ela pode te ajudar a buscar outras normas que talvez você nem saiba que existem, e aí é só copiar o trecho e colar aqui.\n\n"
                    f"**4️⃣** E lembrando que **você sempre pode adicionar norma manualmente** caso lembre de alguma norma que nem eu, nem a Legis encontramos."
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

        return self.criar_resposta(
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
            # É um nome válido - ir para confirmação
            sm.nome_temporario = palavra.capitalize()
            sm.estado = EstadoPOP.CONFIRMA_NOME
            resposta = (
                f"Olá, {sm.nome_temporario}! Prazer em te conhecer.\n\n"
                "Fico feliz que você tenha aceitado essa missão de documentar nossos processos.\n\n"
                f"**Antes de continuarmos, me confirma, posso te chamar de {sm.nome_temporario} mesmo?**"
            )
            return resposta, sm

        # ✅ FIX: Se mensagem não é nome válido, apenas pedir clarificação
        # NUNCA repetir boas-vindas completas (frontend já mostrou)
        resposta = "Desculpe, não entendi. Pode me dizer seu nome? (Digite apenas o primeiro nome)"
        return resposta, sm

    def _gerar_explicacao_longa_com_delay(self) -> str:
        """
        Gera mensagem de explicação longa com delays progressivos.

        Quebra a mensagem em 4 partes com delays de 1500ms entre elas:
        1. Introdução empática (imediata)
        2. Explicação do contexto (após 1500ms)
        3. Detalhamento das etapas (após 1500ms)
        4. Fechamento motivacional (após 1500ms)

        Returns:
            str: Mensagem com tags [DELAY:1500] para processamento no frontend
        """
        return (
            f"Opa, você quer mais detalhes? 😊[DELAY:1500]"
            f"Eu amei, porque adoro conversar![DELAY:1500]"
            f"Então vamos com calma, que eu te explico tudo direitinho.\n\n"
            f"Nesse chat, a gente vai mapear a sua atividade:\n\n"
            f"aquilo que você faz todos os dias (ou quase), a rotina real do seu trabalho.\n\n"
            f"A ideia é preencher juntos o formulário de Procedimento Operacional Padrão, o famoso POP, "
            f"que tá aí do lado 👉\n"
            f"Dá uma olhadinha! Nossa meta é deixar esse POP prontinho, claro e útil pra todo mundo que "
            f"trabalha com você. ✅[DELAY:1500]"
            f"\n\nEu vou te perguntar:\n"
            f"🧭 em qual área você atua,\n"
            f"🧩 te ajudar com a parte mais burocrática — macroprocesso, processo, subprocesso e atividade,\n"
            f"📘 e criar o \"CPF\" do seu processo (a gente chama de CAP, Código na Arquitetura do Processo).\n\n"
            f"Depois, vamos falar sobre os sistemas que você usa e as normas que regem sua atividade.\n"
            f"Nessa parte, vou até te apresentar minha amiga do Sigepe Legis IA — ela é especialista em achar "
            f"a norma certa no meio de tanta lei e portaria 🤖📜[DELAY:1500]"
            f"\n\nPor fim, vem a parte mais detalhada: você vai me contar passo a passo o que faz no dia a dia.\n\n"
            f"Pode parecer demorado, mas pensa assim: quanto melhor você mapear agora, menos retrabalho vai "
            f"ter depois — e o seu processo vai ficar claro, seguro e fácil de ensinar pra quem chegar novo. 💪\n\n"
            f"Tudo certo até aqui?"
        )

    def _processar_confirma_nome(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa confirmação do nome e vai direto para escolha de tipo de explicação"""
        msg_lower = mensagem.lower().strip()

        if self._detectar_intencao(msg_lower, 'confirmacao'):
            sm.nome_usuario = sm.nome_temporario
            sm.estado = EstadoPOP.ESCOLHA_TIPO_EXPLICACAO

            resposta = (
                f"Ótimo então, {sm.nome_usuario}. 😊\n\n"
                f"Antes de seguir, preciso te explicar rapidinho como tudo vai funcionar.\n\n"
                f"Você prefere:\n\n"
                f"🕐 **que eu fale de forma objetiva**, ou\n"
                f"💬 **uma explicação mais detalhada**\n\n"
                f"sobre o que vamos fazer daqui pra frente?"
            )
        else:
            sm.estado = EstadoPOP.NOME_USUARIO
            resposta = "Sem problemas! Como você prefere que eu te chame?"

        return resposta, sm

    def _processar_escolha_tipo_explicacao(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa escolha entre explicação curta ou longa"""
        msg_lower = mensagem.lower().strip()

        # Explicação detalhada/longa
        if self._detectar_intencao(msg_lower, 'detalhes'):
            sm.estado = EstadoPOP.EXPLICACAO_LONGA
            resposta = self._gerar_explicacao_longa_com_delay()
            return resposta, sm

        # Explicação objetiva/curta (fluxo atual)
        elif self._detectar_intencao(msg_lower, 'objetiva'):
            sm.estado = EstadoPOP.EXPLICACAO
            sm.tipo_interface = 'confirmacao_explicacao'
            sm.dados_interface = {
                'botoes': [
                    {'label': 'Sim', 'valor': 'sim', 'tipo': 'primary'},
                    {'label': 'Não, quero mais detalhes', 'valor': 'detalhes', 'tipo': 'secondary'}
                ]
            }
            resposta = (
                f"Nesse chat eu vou conduzir uma conversa guiada. A intenção é preencher esse formulário "
                f"de Procedimento Operacional Padrão - POP aí do lado. Tá vendo? Aproveita pra conhecer.\n\n"
                f"Nossa meta é entregar esse POP prontinho. Vamos continuar?"
            )
            return resposta, sm

        # Não entendeu
        else:
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
                f"Mas olha, {sm.nome_usuario}\n\n"
                f"Antes da gente seguir, quero te tranquilizar e te fazer um pedido rápido.\n\n"
                f"1️⃣ é totalmente normal ter dúvidas! No fim desse processo você vai poder revisar e ajustar tudo, "
                f"e ainda pode pedir pra alguém da equipe dar uma olhada junto.\n\n"
                f"2️⃣ eu sei que esse trabalho exige paciência. Então vai com calma, sem pressa: quanto mais detalhe "
                f"você deixar registrado agora, menos retrabalho vai ter lá na frente.\n\n"
                f"Posso contar contigo pra fazer isso com carinho? 💛"
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
                f"🔹 **Sim, vamos continuar!** - para continuar\n"
                f"🔹 **Não, ainda tenho dúvidas** - para eu te explicar melhor"
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
                f"Mas olha, {sm.nome_usuario}\n\n"
                f"Antes da gente seguir, quero te tranquilizar e te fazer um pedido rápido.\n\n"
                f"1️⃣ é totalmente normal ter dúvidas! No fim desse processo você vai poder revisar e ajustar tudo, "
                f"e ainda pode pedir pra alguém da equipe dar uma olhada junto.\n\n"
                f"2️⃣ eu sei que esse trabalho exige paciência. Então vai com calma, sem pressa: quanto mais detalhe "
                f"você deixar registrado agora, menos retrabalho vai ter lá na frente.\n\n"
                f"Posso contar contigo pra fazer isso com carinho? 💛"
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
            'botao_confirmar': 'Ok, já entendi',
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
                f"Mas olha, {sm.nome_usuario}\n\n"
                f"Antes da gente seguir, quero te tranquilizar e te fazer um pedido rápido.\n\n"
                f"1️⃣ é totalmente normal ter dúvidas! No fim desse processo você vai poder revisar e ajustar tudo, "
                f"e ainda pode pedir pra alguém da equipe dar uma olhada junto.\n\n"
                f"2️⃣ eu sei que esse trabalho exige paciência. Então vai com calma, sem pressa: quanto mais detalhe "
                f"você deixar registrado agora, menos retrabalho vai ter lá na frente.\n\n"
                f"Posso contar contigo pra fazer isso com carinho? 💛"
            )
        # Se escolheu "Não, quero mais detalhes" - vai para EXPLICACAO_LONGA
        elif 'detalhes' in msg_lower or 'detalhe' in msg_lower or ('não' in msg_lower or 'nao' in msg_lower):
            sm.estado = EstadoPOP.EXPLICACAO_LONGA
            resposta = self._gerar_explicacao_longa_com_delay()
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
                f"Uau! 🌟\n"
                f"**PARCERIA CONFIRMADA!** Tô super animada 😄\n\n"
                f"E agora oficialmente começamos nossa jornada de mapeamento.\n\n"
                f"Sei que dá trabalho, mas cada detalhe que você registrar hoje vai poupar horas (ou até dias!) "
                f"de dúvida no futuro. Pra você e pra sua equipe.\n\n"
                f"Esse é o tipo de esforço que vira legado dentro da DECIPEX. 🚀"
            )
            return resposta, sm
        else:
            # Se não entendeu, repete a pergunta
            resposta = (
                f"Desculpe, não entendi.\n\n"
                f"Posso contar contigo pra fazer isso com carinho? 💛"
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

        # Buscar sugestões de normas
        sugestoes = self._sugerir_base_legal_contextual(sm)

        resposta = (
            f"Agora, quais são as principais normas que regulam esta atividade?\n\n"
            f"Como são muitas normas, eu achei melhor criar quatro formas de adicionar:\n\n"
            f"💡 **Seleção inteligente disponível abaixo!**"
        )

        return resposta, sm

    def _processar_dispositivos_normativos(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa coleta de dispositivos normativos e vai para reconhecimento"""
        # Separar por vírgula ou quebra de linha (ou aceitar JSON de seleção)
        dados = self._parse_json_seguro(mensagem)
        if isinstance(dados, list):
            normas = dados
        else:
            normas = [n.strip() for n in mensagem.replace('\n', ',').split(',') if n.strip()]

        sm.dados_coletados['dispositivos_normativos'] = normas

        # 🎯 Mudar estado para TRANSICAO_ROADTRIP
        sm.estado = EstadoPOP.TRANSICAO_ROADTRIP

        # 🔥 FIX: Limpar tipo_interface antigo (evita fallback para interface de normas)
        sm.tipo_interface = None
        sm.dados_interface = None

        logger.info(f"🚗 [ROADTRIP] Estado mudado para TRANSICAO_ROADTRIP. Interface será mostrada junto com a mensagem.")

        nome = sm.nome_usuario or "você"
        resposta = (
            f"👏 Perfeito, {nome}!\n\n"
            f"As normas são como as placas da estrada: mostram a direção certa pra sua atividade seguir segura e consistente. 🚦"
        )

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
            f"Agora que você já está ligado na sinalização, vamos falar sobre os motoristas dessa jornada: "
            f"as pessoas que fazem essa atividade acontecer no dia a dia.\n\n"
            f"Por favor, **selecione abaixo quem executa diretamente, quem revisa, quem apoia… "
            f"e também quem prepara o terreno antes que o processo chegue até você.**\n\n"
            f"💡 Ei!!! Você faz parte!\n"
            f"Lembre de se incluir também!\n\n"
            f"As opções estão logo abaixo, mas se eu esqueci alguém pode digitar."
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

        # Salvar e avançar para DISPOSITIVOS_NORMATIVOS
        sm.dados_coletados['sistemas'] = sistemas
        sm.estado = EstadoPOP.DISPOSITIVOS_NORMATIVOS

        # Buscar sugestões de normas
        sugestoes = self._sugerir_base_legal_contextual(sm)
        grupos_normas = {}
        if self.suggestor_base_legal:
            try:
                grupos_normas = self.suggestor_base_legal.obter_grupos_normas()
            except:
                pass

        # Interface de normas
        sm.tipo_interface = 'normas'
        sm.dados_interface = {
            'sugestoes': sugestoes,
            'grupos': grupos_normas,
            'campo_livre': True,
            'multipla_selecao': True,
            'texto_introducao': (
                f"Registrei {len(sistemas)} sistema(s).\n\n"
                f"Agora vamos falar sobre as normas legais e guias que orientam essa atividade."
            )
        }

        nome = sm.nome_usuario or "você"
        resposta = (
            f"Agora vamos falar sobre as normas legais, normativos e guias que orientam essa atividade. ⚖️\n\n"
            f"Aqui abaixo, eu já separei as principais normas que levantei."
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
                    fluxos = [f.strip() for f in mensagem.replace('\n', ',').split('|') if f.strip()]
                sm.dados_coletados['fluxos_entrada'] = fluxos

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
                'canais_atendimento': canais_atendimento
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
                    fluxos = [f.strip() for f in mensagem.replace('\n', ',').split(',') if f.strip()]
                sm.dados_coletados['fluxos_saida'] = fluxos

            # Ir para PONTOS_ATENCAO (fluxo completo: PONTOS → REVISAO → TRANSICAO_EPICA)
            sm.estado = EstadoPOP.PONTOS_ATENCAO
            sm.tipo_interface = None
            sm.dados_interface = {}

            nome = sm.nome_usuario or "você"

            resposta = (
                f"Ótimo! Registrei {len(sm.dados_coletados['fluxos_saida'])} fluxo(s) de saída. ✅\n\n"
                f"Agora me diga: **Há algum ponto de atenção especial** neste processo?\n\n"
                f"Por exemplo:\n"
                f"• Prazo crítico que não pode atrasar\n"
                f"• Documentos que devem ter atenção redobrada\n"
                f"• Etapas que costumam gerar dúvidas\n\n"
                f"Digite os pontos de atenção ou escreva **'nenhum'** se não houver."
            )

        return resposta, sm

    def _processar_pontos_atencao(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Processa pontos de atenção (último campo antes da revisão)

        Após coletar, vai para REVISAO_PRE_DELEGACAO
        """
        msg_lower = mensagem.lower().strip()
        nome = sm.nome_usuario or "você"

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
            f"Perfeito, {nome}! Seu POP está completo!\n\n"
            f"{resumo}\n\n"
            f"**Deseja alterar algo ou podemos seguir para as etapas detalhadas?**\n\n"
            f"• Digite **'tudo certo'** ou **'seguir'** para continuar\n"
            f"• Digite **'editar'** se quiser alterar algum campo"
        )

        # Interface com botões
        sm.tipo_interface = 'confirmacao_dupla'
        sm.dados_interface = {
            'botao_confirmar': 'Tudo certo, pode seguir ✅',
            'botao_editar': 'Deixa eu arrumar uma coisa ✏️',
            'valor_confirmar': 'SEGUIR',
            'valor_editar': 'EDITAR'
        }

        return resposta, sm

    def _processar_revisao_pre_delegacao(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        REVISÃO 2 - Pré-delegação

        Permite editar 9 campos ou seguir para etapas
        """
        msg_lower = mensagem.lower().strip()
        nome = sm.nome_usuario or "você"

        # Se confirmar/seguir → TRANSICAO_EPICA
        if self._detectar_intencao(msg_lower, 'confirmacao'):
            sm.estado = EstadoPOP.TRANSICAO_EPICA
            sm.tipo_interface = None
            sm.dados_interface = {}

            progresso = self.obter_progresso(sm)
            percentual = progresso['percentual']

            resposta = (
                f"## 🎯 **AGORA ENTRAMOS NO CORAÇÃO DO PROCESSO**\n\n"
                f"A próxima fase é a **mais importante e detalhada**: vamos mapear **CADA ETAPA** da sua atividade!\n\n"
                f"Para cada etapa, vou perguntar:\n"
                f"📝 O que você faz\n"
                f"👤 Quem executa\n"
                f"📚 Qual norma fundamenta\n"
                f"💻 Qual sistema utiliza\n"
                f"📄 Quais documentos usa/gera\n\n"
                f"**⏱️ Tempo estimado:** 15-20 minutos\n\n"
                f"**💡 Dica importante:**\n"
                f"Esta é a parte mais demorada, então que tal:\n"
                f"☕ Pegar um café ou água\n"
                f"🚶 Dar uma esticada nas pernas\n"
                f"🚽 Ir ao banheiro se precisar\n"
                f"📋 Ter em mãos exemplos reais do processo\n\n"
                f"Quando estiver pronto e confortável, digite **'VAMOS'** para começarmos! 🚀\n"
                f"Ou digite **'PAUSA'** se preferir continuar depois."
            )

            return resposta, sm

        # Se editar → SELECAO_EDICAO com 9 campos
        elif self._detectar_intencao(msg_lower, 'edicao'):
            sm.estado = EstadoPOP.SELECAO_EDICAO
            sm.tipo_interface = 'selecao_edicao'
            sm._voltou_de_revisao = True  # Flag para saber que veio da revisão

            # 9 CAMPOS EDITÁVEIS (CAP é imutável)
            campos_editaveis = {
                "1": {"campo": "entrega_esperada", "label": "Entrega Esperada"},
                "2": {"campo": "sistemas", "label": "Sistemas Utilizados"},
                "3": {"campo": "dispositivos_normativos", "label": "Dispositivos Normativos"},
                "4": {"campo": "operadores", "label": "Operadores"},
                "5": {"campo": "fluxos_entrada", "label": "Fluxos de Entrada"},
                "6": {"campo": "etapas", "label": "Tarefas/Etapas (será editado depois)"},
                "7": {"campo": "fluxos_saida", "label": "Fluxos de Saída"},
                "8": {"campo": "documentos", "label": "Documentos"},
                "9": {"campo": "pontos_atencao", "label": "Pontos de Atenção"}
            }

            sm.dados_interface = {
                'campos_editaveis': campos_editaveis
            }

            resumo = self._gerar_resumo_pop(sm)

            resposta = (
                f"## 🔧 **EDIÇÃO DE CAMPOS**\n\n"
                f"{resumo}\n\n"
                f"**Qual campo você gostaria de editar, {nome}?**\n\n"
                f"1️⃣ Entrega Esperada\n"
                f"2️⃣ Sistemas Utilizados\n"
                f"3️⃣ Dispositivos Normativos\n"
                f"4️⃣ Operadores\n"
                f"5️⃣ Fluxos de Entrada\n"
                f"6️⃣ Tarefas/Etapas (será editado depois no Helena Etapas)\n"
                f"7️⃣ Fluxos de Saída\n"
                f"8️⃣ Documentos\n"
                f"9️⃣ Pontos de Atenção\n\n"
                f"Digite o **número** do campo ou **'cancelar'** para voltar."
            )

            return resposta, sm

        else:
            # Não entendeu - repetir pergunta
            resposta = (
                f"Não entendi, {nome}.\n\n"
                f"Digite **'tudo certo'** para seguir ou **'editar'** para alterar algum campo."
            )
            return resposta, sm

    def _processar_transicao_epica(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Estado de transição épica - Celebra conquistas e prepara para etapas detalhadas

        Inclui:
        - Troféu/badge de conquista animado
        - Mensagem motivacional humanizada
        - Dicas práticas de preparação (café, banheiro, etc.)
        - Estimativa de tempo realista
        - Opção de pausa com salvamento automático
        - Interface dinâmica com botões pulsantes
        """
        msg_lower = mensagem.lower().strip()
        nome = sm.nome_usuario

        if self._detectar_intencao(msg_lower, 'pausa') or self._detectar_intencao(msg_lower, 'negacao'):
            # Usuário quer pausar - mensagem humanizada com resumo
            resposta = (
                f"Sem problema, {nome}! 😊\n\n"
                "Entendo perfeitamente. Mapear processos requer concentração e tempo.\n\n"
                "**✅ Seus dados foram salvos** e você pode continuar quando quiser.\n\n"
                "📌 **Para retomar:** É só dizer 'continuar mapeamento'\n\n"
                "**Dicas para o mapeamento de etapas:**\n"
                "📝 Tenha exemplos reais do processo em mãos\n"
                "📋 Pense em todas as decisões e caminhos alternativos\n"
                "⏱️ Reserve 20-30 minutos sem interrupções\n"
                "☕ Esteja confortável e descansado\n\n"
                "Até breve! Estarei aqui quando você voltar. 👋"
            )
            # Não muda o estado, fica esperando
            return resposta, sm

        elif self._detectar_intencao(msg_lower, 'confirmacao'):
            # Usuário confirmou - avançar para delegação com troféu
            sm.estado = EstadoPOP.DELEGACAO_ETAPAS

            resposta = (
                f"🏆 **PRIMEIRA FASE CONCLUÍDA!** 🏆\n\n"
                f"{nome}, você está indo muito bem!\n\n"
                f"Agora a Helena especializada em etapas vai te guiar no detalhamento operacional.\n\n"
                f"**Iniciando mapeamento de etapas...** 🎯"
            )

            return resposta, sm

        else:
            # Primeira visita ou mensagem não reconhecida - mostrar transição épica COMPLETA
            progresso = self.obter_progresso(sm)
            percentual = progresso['percentual']

            resposta = (
                f"## 🎯 **AGORA ENTRAMOS NO CORAÇÃO DO PROCESSO**\n\n"
                f"A próxima fase é a **mais importante e detalhada**: vamos mapear **CADA ETAPA** da sua atividade!\n\n"
                f"Para cada etapa, vou perguntar:\n"
                f"📝 O que você faz\n"
                f"👤 Quem executa\n"
                f"📚 Qual norma fundamenta\n"
                f"💻 Qual sistema utiliza\n"
                f"📄 Quais documentos usa/gera\n\n"
                f"**⏱️ Tempo estimado:** 15-20 minutos\n\n"
                f"**💡 Dica importante:**\n"
                f"Esta é a parte mais demorada, então que tal:\n"
                f"☕ Pegar um café ou água\n"
                f"🚶 Dar uma esticada nas pernas\n"
                f"🚽 Ir ao banheiro se precisar\n"
                f"📋 Ter em mãos exemplos reais do processo\n\n"
                f"Quando estiver pronto e confortável, digite **'VAMOS'** para começarmos! 🚀\n"
                f"Ou digite **'PAUSA'** se preferir continuar depois."
            )

            return resposta, sm

    def _processar_selecao_edicao(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Sistema de Edição Granular - permite editar qualquer campo coletado

        Menu interativo com todas as opções editáveis numeradas.
        Usuário seleciona número e volta ao estado correspondente.
        """
        msg_lower = mensagem.lower().strip()

        # Verificar se é cancelamento
        if self._detectar_intencao(msg_lower, 'cancelar') or msg_lower == 'não':
            # Verificar se veio da revisão
            if hasattr(sm, '_voltou_de_revisao') and sm._voltou_de_revisao:
                sm._voltou_de_revisao = False
                sm.estado = EstadoPOP.REVISAO_PRE_DELEGACAO
                return "Ok, voltando para revisão! Digite 'tudo certo' para seguir ou 'editar' para alterar outro campo.", sm
            else:
                sm.estado = EstadoPOP.TRANSICAO_EPICA
                return "Ok, voltando ao fluxo principal! Digite 'VAMOS' quando estiver pronto.", sm

        # Mapear opções de edição para estados
        opcoes_edicao = {
            '1': ('Nome do Processo', EstadoPOP.NOME_PROCESSO),
            '2': ('Entrega Esperada', EstadoPOP.ENTREGA_ESPERADA),
            '3': ('Dispositivos Normativos', EstadoPOP.DISPOSITIVOS_NORMATIVOS),
            '4': ('Operadores', EstadoPOP.OPERADORES),
            '5': ('Sistemas', EstadoPOP.SISTEMAS),
            '6': ('Fluxos Entrada/Saída', EstadoPOP.FLUXOS),
        }

        # Se primeira visita, mostrar menu
        if not hasattr(sm, '_primeira_edicao') or sm._primeira_edicao:
            sm._primeira_edicao = False

            resumo = self._gerar_resumo_pop(sm)

            resposta = (
                f"## 🔧 **EDIÇÃO GRANULAR DE CAMPOS**\n\n"
                f"{resumo}\n\n"
                f"**Qual campo deseja editar?**\n\n"
                f"1️⃣ Nome do Processo\n"
                f"2️⃣ Entrega Esperada\n"
                f"3️⃣ Dispositivos Normativos\n"
                f"4️⃣ Operadores\n"
                f"5️⃣ Sistemas\n"
                f"6️⃣ Documentos de Entrada\n"
                f"7️⃣ Documentos de Saída\n"
                f"8️⃣ Fluxos Entrada/Saída\n\n"
                f"Digite o **número** do campo que deseja editar, ou **'CANCELAR'** para voltar."
            )

            sm.tipo_interface = 'selecao_numero'
            sm.dados_interface = {
                'titulo': 'Selecione o campo para editar',
                'opcoes': list(opcoes_edicao.keys()),
                'labels': [v[0] for v in opcoes_edicao.values()]
            }

            return resposta, sm

        # Processar seleção
        escolha = mensagem.strip()

        if escolha in opcoes_edicao:
            campo_nome, novo_estado = opcoes_edicao[escolha]
            sm.estado = novo_estado

            resposta = f"✏️ Editando **{campo_nome}**...\n\nPor favor, forneça o novo valor:"
            return resposta, sm
        else:
            resposta = (
                "❌ Opção inválida!\n\n"
                "Por favor, digite um número de **1 a 8** ou **'CANCELAR'**."
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
    # HELPERS
    # ========================================================================

    def _sugerir_base_legal_contextual(self, sm: POPStateMachine) -> list:
        """Sugere base legal baseada no contexto coletado (IA completa)"""
        try:
            if not self.suggestor_base_legal:
                return []

            # Montar contexto rico
            area_info = sm.area_selecionada or {}
            contexto = {
                "nome_processo": sm.dados_coletados.get("nome_processo", ""),
                "area_codigo": area_info.get("codigo", ""),
                "area_nome": area_info.get("nome", ""),
                "sistemas": sm.dados_coletados.get("sistemas", []),
                "objetivo": sm.dados_coletados.get("entrega_esperada", ""),
                "macroprocesso": sm.macro_selecionado or "",
                "processo": sm.processo_selecionado or "",
                "subprocesso": sm.subprocesso_selecionado or "",
                "atividade": sm.atividade_selecionada or ""
            }

            # Chamar BaseLegalSuggestorDECIPEx com contexto completo
            sugestoes = self.suggestor_base_legal.sugerir_base_legal(contexto)

            # Filtrar sugestões já usadas (anti-repetição)
            sugestoes_novas = []
            for sug in sugestoes:
                norma_id = sug.get('norma', '') if isinstance(sug, dict) else str(sug)
                if norma_id not in self._normas_sugeridas:
                    sugestoes_novas.append(sug)
                    self._normas_sugeridas.add(norma_id)

            # Retornar top 5 sugestões novas
            return sugestoes_novas[:5] if sugestoes_novas else []

        except Exception as e:
            logger.error(f"Erro ao sugerir base legal contextual: {e}")
            return []

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
        """Calcula progresso da coleta baseado em campos preenchidos."""
        d = sm.dados_coletados
        campos = [
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
        preenchidos = sum(1 for c in campos if c)
        return f"{preenchidos}/{len(campos)}"

    def obter_progresso(self, sm: POPStateMachine) -> dict:
        """Retorna detalhes completos do progresso atual."""
        d = sm.dados_coletados
        campos = [
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
        preenchidos = sum(1 for _, v in campos if v)
        faltantes = [nome for nome, v in campos if not v]
        total = len(campos)
        percentual = int((preenchidos / total) * 100)

        return {
            "campos_preenchidos": preenchidos,
            "total_campos": total,
            "percentual": percentual,
            "estado_atual": sm.estado.value,
            "campos_faltantes": faltantes,
            "completo": sm.estado == EstadoPOP.DELEGACAO_ETAPAS or percentual == 100
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

        return {
            # Identificação
            "codigo_cap": codigo_cap,
            "codigo_processo": codigo_cap,  # ✅ Alias para frontend
            "area": {
                "nome": area_info.get("nome", ""),
                "codigo": area_info.get("codigo", "")
            },
            "macroprocesso": sm.macro_selecionado or "",
            "processo": sm.processo_selecionado or "",
            "processo_especifico": sm.processo_selecionado or "",  # ✅ Alias para frontend
            "subprocesso": sm.subprocesso_selecionado or "",
            "atividade": sm.atividade_selecionada or "",

            # Dados coletados
            "nome_processo": dados.get("nome_processo", "") or sm.atividade_selecionada or "",  # ✅ Fallback para atividade
            "entrega_esperada": dados.get("entrega_esperada", ""),
            "dispositivos_normativos": dados.get("dispositivos_normativos", []),
            # ✅ FIX: Manter operadores como LISTA (igual sistemas)
            "operadores": dados.get("operadores", []),
            "sistemas": dados.get("sistemas", []),
            "documentos": dados.get("documentos", []),
            "fluxos_entrada": dados.get("fluxos_entrada", []),
            "fluxos_saida": dados.get("fluxos_saida", []),
            "pontos_atencao": dados.get("pontos_atencao", ""),

            # Metadados
            "nome_usuario": sm.nome_usuario or "",
            "versao": "1.0",
            "data_criacao": "",  # Frontend preenche

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
        resumo += f"**🎯 Entrega Esperada:** {dados['entrega_esperada']}\n\n"

        # 3. SISTEMAS
        resumo += f"**💻 Sistemas:** {', '.join(dados['sistemas'])}\n\n"

        # 4. NORMAS
        resumo += f"**📚 Normas:** {', '.join(dados['dispositivos_normativos'])}\n\n"

        # 5. OPERADORES
        resumo += f"**👥 Operadores:** {', '.join(dados['operadores'])}\n\n"

        # 6. ENTRADA (De quais áreas recebe insumos)
        if dados.get('fluxos_entrada'):
            resumo += f"**📥 Entrada:** {', '.join(dados['fluxos_entrada'])}\n\n"

        # 7. SAÍDA (Para quais áreas entrega resultados)
        if dados.get('fluxos_saida'):
            resumo += f"**📤 Saída:** {', '.join(dados['fluxos_saida'])}\n\n"

        # 8. DOCUMENTOS
        if dados.get('documentos'):
            resumo += f"**📄 Documentos:** {', '.join(dados['documentos'])}\n\n"

        resumo += "**✅ Etapas:** Serão coletadas por Helena Etapas\n"
        resumo += "**⚠️ Pontos de Atenção:** Serão coletados após as etapas\n"

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
