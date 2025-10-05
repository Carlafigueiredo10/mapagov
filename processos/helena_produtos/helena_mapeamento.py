from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory

def criar_helena_mapeamento():
    """
    Cria Helena como parceira de preenchimento do POP.
    Ela responde de forma empática, clara e motivadora.
    Mantém memória da conversa para dar continuidade real.
    Helena só muda de assunto quando o usuário confirmar que a dúvida foi resolvida.
    """

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

helena_mapeamento = criar_helena_mapeamento()