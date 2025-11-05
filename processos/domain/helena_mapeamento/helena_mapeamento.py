# ⚡ OTIMIZAÇÃO MEMÓRIA: Lazy loading de LangChain
# Imports movidos para dentro da função

def criar_helena_mapeamento():
    """
    Cria Helena como parceira de preenchimento do POP.
    Ela responde de forma empática, clara e motivadora.
    Mantém memória da conversa para dar continuidade real.
    Ela informa com tom leve de humor que muitas coisas o usuário vai aprender ao longo do processo de mapeamento.
    Helena cuidadosamente conduz o usuário a voltar pro fluxo do mapeamento.
    Helena só muda de assunto quando o usuário confirmar que a dúvida foi resolvida.
    """

    # ⚡ Lazy imports
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    from langchain.chains import LLMChain
    from langchain.memory import ConversationBufferMemory

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.6)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Você é Helena, assistente especialista em mapeamento de processos e POPs. "
         "Seu papel é ser parceira do usuário: clara, paciente, empática e bem-humorada. "
         "O usuário está preenchendo os campos de um POP e você deve ajudá-lo com explicações simples, exemplos práticos e incentivo. "
         "Mantenha foco no campo atual até o usuário confirmar que a dúvida foi resolvida. "
         "Nunca repita a mesma explicação: traga novos exemplos, metáforas ou perguntas de apoio. "
         "Só avance para outro campo se o usuário pedir explicitamente. "
         "Use humor leve e reconhecimento do esforço quando fizer sentido. "
         "No fim de cada resposta, confirme com o usuário: 'Essa etapa ficou clara?' ou 'Podemos seguir?'. "
        ),
        ("human", "{input}")
    ])

    # 🔹 Memória para manter histórico e contexto
    memory = ConversationBufferMemory(return_messages=True)

    # 🔹 Chain combina LLM + prompt + memória
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

    Usa LLM (GPT-4o-mini) para responder livremente perguntas sobre:
    - O que é POP
    - O que é CAP
    - Como funciona o mapeamento
    - Qualquer outra dúvida do usuário

    Mantém conversação até usuário indicar que terminou.
    """

    VERSION = "1.0.0"
    PRODUTO_NOME = "Helena Mapeamento"

    def __init__(self):
        super().__init__()
        self._chain_instance = None  # Lazy loading do LangChain

    def inicializar_estado(self) -> dict:
        """
        Retorna estado inicial para Helena Mapeamento.

        Returns:
            dict: Estado inicial com histórico de mensagens vazio
        """
        return {
            'historico_mensagens': [],
            'contexto': None,  # Contexto da dúvida (ex: "explicacao_pop")
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

        # Lazy loading da chain LangChain
        if self._chain_instance is None:
            self._chain_instance = criar_helena_mapeamento()

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
            'finalizou_duvidas': finalizou,  # Flag para Helena POP
            'progresso': f"{session_data['contador_mensagens']} mensagens",
            'metadados': {
                'contador_mensagens': session_data['contador_mensagens'],
                'contexto': session_data.get('contexto')
            }
        }