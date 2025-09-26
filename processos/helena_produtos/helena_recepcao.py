from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate

def criar_helena_recepcao():
    """
    Helena Recepcionista com RAG integrado
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    
    # Carregar vectorstore
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma(
        persist_directory="./chroma_db/documentos_produzidos",
        embedding_function=embeddings
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Você é Helena, assistente especializada em GRC (Governança, Riscos e Conformidade) para o setor público brasileiro.

Seu papel é:
1. Entender a necessidade do usuário através de conversa natural
2. Consultar a base de conhecimento quando necessário
3. Orientar para o produto correto do MapaGov

Produtos disponíveis:
- P1: Gerador de POP (Procedimento Operacional Padrão)
- P2: Gerador de Fluxograma
- P3: Dossiê PDF Completo
- P4: Dashboard de Controle

Contexto da base de conhecimento:
{contexto}

Seja natural, prestativa e objetiva. Se não souber algo, seja honesta."""),
        ("human", "{input}")
    ])
    
    chain = prompt | llm
    
    def responder(mensagem: str, historico: list = None):
        # Buscar contexto relevante no RAG
        docs = vectorstore.similarity_search(mensagem, k=2)
        contexto = "\n\n".join([f"📄 {doc.metadata['source']}: {doc.page_content[:300]}" for doc in docs])
        
        resposta = chain.invoke({
            "input": mensagem,
            "contexto": contexto if docs else "Nenhum documento relevante encontrado."
        })
        
        return resposta.content
    
    return responder

# Criar instância global
helena_recepcao = criar_helena_recepcao()