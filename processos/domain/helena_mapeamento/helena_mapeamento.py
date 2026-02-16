# ⚡ OTIMIZAÇÃO MEMÓRIA: Lazy loading de LangChain
# Imports movidos para dentro da função

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Mapeamento de estados para descrição legível do campo atual
CONTEXTO_ESTADOS = {
    'nome_usuario': 'Identificação do usuário',
    'escolha_tipo_explicacao': 'Introdução ao mapeamento de processos',
    'explicacao_longa': 'Explicação detalhada do POP',
    'explicacao': 'Visão geral do mapeamento',
    'pedido_compromisso': 'Compromisso de preenchimento',
    'area_decipex': 'Seleção da área organizacional (DECIPEX)',
    'subarea_decipex': 'Seleção da subárea organizacional',
    'arquitetura': 'Classificação na Arquitetura de Processos (macroprocesso, processo, subprocesso)',
    'confirmacao_arquitetura': 'Confirmação da arquitetura sugerida',
    'selecao_hierarquica': 'Seleção manual da hierarquia de processos',
    'nome_processo': 'Nome da atividade sendo mapeada',
    'entrega_esperada': 'Entrega esperada da atividade',
    'confirmacao_entrega': 'Confirmação da entrega esperada',
    'reconhecimento_entrega': 'Reconhecimento da entrega',
    'dispositivos_normativos': 'Dispositivos normativos (base legal)',
    'transicao_roadtrip': 'Transição para próxima fase',
    'operadores': 'Operadores (perfis responsáveis pela execução)',
    'sistemas': 'Sistemas utilizados na atividade',
    'fluxos': 'Fluxos de entrada e saída',
    'pontos_atencao': 'Pontos de atenção e riscos',
    'revisao_pre_delegacao': 'Revisão antes das etapas',
    'transicao_epica': 'Transição para definição de etapas',
    'selecao_edicao': 'Menu de edição granular',
    'delegacao_etapas': 'Início da definição de etapas',
    'etapa_form': 'Formulário de etapa do processo',
    'etapa_descricao': 'Ação principal da etapa',
    'etapa_operador': 'Responsável pela etapa',
    'etapa_sistemas': 'Sistemas utilizados na etapa',
    'etapa_docs_requeridos': 'Documentos consultados/recebidos na etapa',
    'etapa_docs_gerados': 'Documentos gerados na etapa',
    'etapa_tempo': 'Tempo estimado da etapa',
    'etapa_condicional': 'Decisão condicional na etapa',
    'etapa_tipo_condicional': 'Tipo de decisão condicional',
    'etapa_antes_decisao': 'Ação antes da decisão condicional',
    'etapa_cenarios': 'Cenários da decisão condicional',
    'etapa_subetapas_cenario': 'Subetapas do cenário condicional',
    'etapa_detalhes': 'Verificações/detalhes da etapa',
    'etapa_mais': 'Adicionar mais etapas',
    'etapa_revisao': 'Revisão das etapas',
    'revisao_final': 'Revisão final do POP completo',
    'finalizado': 'POP finalizado',
}

# Cache do prompt em produção
_prompt_cache = None

FALLBACK_PROMPT = (
    "Você é Helena, assistente técnica especializada em mapeamento de processos "
    "administrativos e elaboração de POPs no contexto do serviço público brasileiro. "
    "Ajude o usuário a preencher o campo atual com explicações claras e exemplos práticos."
)


def carregar_prompt_ajuda() -> str:
    """
    Carrega o prompt técnico do arquivo .md.
    Em produção (DEBUG=False): usa cache em memória.
    Em dev (DEBUG=True): sempre relê o arquivo (hot reload).
    Fallback embutido se o arquivo não existir.
    """
    global _prompt_cache

    try:
        from django.conf import settings
        is_debug = settings.DEBUG
    except Exception:
        is_debug = True  # Se não conseguir ler settings, assume dev

    # Cache em produção
    if not is_debug and _prompt_cache:
        return _prompt_cache

    prompt_path = Path(__file__).parent / "prompts" / "helena_ajuda.md"

    try:
        conteudo = prompt_path.read_text(encoding="utf-8")
        # Escapar chaves para LangChain não interpretar como variáveis de template
        conteudo = conteudo.replace("{", "{{").replace("}", "}}")
        _prompt_cache = conteudo
        logger.info(f"[HELENA_AJUDA] Prompt carregado de {prompt_path} ({len(conteudo)} chars)")
        return conteudo
    except Exception as e:
        logger.warning(f"[HELENA_AJUDA] Falha ao carregar prompt de {prompt_path}: {e}. Usando fallback.")
        return FALLBACK_PROMPT


def criar_helena_mapeamento(contexto_campo: str = ""):
    """
    Cria Helena como assistente técnica de apoio ao mapeamento de processos.
    Carrega prompt do arquivo .md e injeta contexto dinâmico do campo atual.
    """

    # ⚡ Lazy imports
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    from langchain.chains import LLMChain
    from langchain.memory import ConversationBufferMemory

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4, request_timeout=30)

    # Carregar prompt base do .md
    system_text = carregar_prompt_ajuda()

    # Injetar contexto dinâmico do campo atual
    if contexto_campo:
        # Escapar chaves no contexto também
        contexto_safe = contexto_campo.replace("{", "{{").replace("}", "}}")
        system_text += f"\n\n--- CONTEXTO ATUAL ---\n{contexto_safe}\n--- FIM DO CONTEXTO ---"

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_text),
        ("human", "{input}")
    ])

    memory = ConversationBufferMemory(return_messages=True)

    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        memory=memory
    )

    def responder(mensagem: str):
        resposta = chain.run(input=mensagem)
        return resposta

    return responder

# ⚡ LAZY LOADING: Instância criada sob demanda
_helena_mapeamento_instance = None

def helena_mapeamento(mensagem: str):
    """Função wrapper para lazy loading da instância Helena Mapeamento"""
    global _helena_mapeamento_instance
    if _helena_mapeamento_instance is None:
        _helena_mapeamento_instance = criar_helena_mapeamento()
    return _helena_mapeamento_instance(mensagem)


# ============================================================================
# CLASSE BASEHELENA PARA INTEGRAÇÃO COM HELENA CORE
# ============================================================================

from processos.domain.base import BaseHelena
from typing import Dict, Any


class HelenaMapeamento(BaseHelena):
    """
    Helena Mapeamento - Produto conversacional para tirar dúvidas sobre processos.

    Usa LLM (GPT-4o-mini) com conhecimento técnico completo sobre POP, CAP,
    campos do formulário e etapas. Recebe contexto dinâmico do campo atual.
    """

    VERSION = "2.0.0"
    PRODUTO_NOME = "Helena Mapeamento"

    def __init__(self, contexto_campo: str = ""):
        super().__init__()
        self._chain_instance = None  # Lazy loading do LangChain
        self._contexto_campo = contexto_campo

    def inicializar_estado(self) -> dict:
        """
        Retorna estado inicial para Helena Mapeamento.

        Returns:
            dict: Estado inicial com histórico de mensagens vazio
        """
        return {
            'historico_mensagens': [],
            'contexto': None,
            'nome_usuario': None,
            'contador_mensagens': 0,
            'finalizou': False
        }

    def processar(self, mensagem: str, session_data: dict) -> dict:
        """
        Processa mensagem delegando para LLM.

        Args:
            mensagem: Pergunta/dúvida do usuário
            session_data: Estado atual com histórico

        Returns:
            dict: Resposta com novo estado e flag de finalização
        """
        self.validar_mensagem(mensagem)
        self.validar_session_data(session_data)

        # Lazy loading da chain LangChain (com contexto do campo atual)
        if self._chain_instance is None:
            self._chain_instance = criar_helena_mapeamento(self._contexto_campo)

        # Processar mensagem com LLM
        resposta_llm = self._chain_instance(mensagem)

        # Atualizar histórico
        session_data['historico_mensagens'].append({
            'role': 'user',
            'content': mensagem
        })
        session_data['historico_mensagens'].append({
            'role': 'assistant',
            'content': resposta_llm
        })
        session_data['contador_mensagens'] += 1

        # Detectar se usuário quer finalizar
        msg_lower = mensagem.lower().strip()
        finalizou = any(palavra in msg_lower for palavra in [
            'entendi', 'obrigad', 'valeu', 'ok agora', 'ficou claro',
            'vamos seguir', 'podemos continuar', 'seguir', 'continuar'
        ])

        # Após 5+ mensagens, perguntar se pode finalizar
        if session_data['contador_mensagens'] >= 5 and not session_data['finalizou']:
            finalizou = True

        session_data['finalizou'] = finalizou

        return {
            'resposta': resposta_llm,
            'novo_estado': session_data,
            'finalizou_duvidas': finalizou,
            'progresso': f"{session_data['contador_mensagens']} mensagens",
            'metadados': {
                'contador_mensagens': session_data['contador_mensagens'],
                'contexto': session_data.get('contexto')
            }
        }
