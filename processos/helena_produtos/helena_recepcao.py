from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
import os

def criar_helena_recepcao():
    """Helena Recepcionista com RAG integrado"""
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    
    # Verificar se diretório do Chroma existe
    chroma_path = "./chroma_db/documentos_produzidos"
    
    if os.path.exists(chroma_path):
        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma(
            persist_directory=chroma_path,
            embedding_function=embeddings
        )
        usar_rag = True
    else:
        vectorstore = None
        usar_rag = False
        print("⚠️ Chroma DB não encontrado. Helena funcionará sem RAG.")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Você é Helena, assistente especializada em GRC (Governança, Riscos e Conformidade) para o setor público brasileiro.

**PRODUTOS DISPONÍVEIS:**
✅ P1: Gerador de POP - Criar POPs estruturados
✅ P5: Análise de Riscos - Identificar riscos de processos
✅ P2: Gerador de Fluxograma - Visualizar processos

🔨 Em Desenvolvimento: P3, P4, P6-P11

**INSTRUÇÕES:**
- Seja natural e prestativa
- Quando identificar necessidade, mencione o produto: "você pode gerar um POP"
- Seja breve e objetiva

{contexto_rag}

Histórico: {historico}"""),
        ("human", "{input}")
    ])
    
    chain = prompt | llm
    historico_conversas = {}
    
    def responder(mensagem: str, session_id: str = "default"):
        # Gerenciar histórico
        if session_id not in historico_conversas:
            historico_conversas[session_id] = []
        
        historico = "\n".join(historico_conversas[session_id][-6:]) if historico_conversas[session_id] else "Primeira interação."
        
        # Buscar contexto RAG se disponível
        contexto_rag = ""
        if usar_rag and vectorstore:
            try:
                docs = vectorstore.similarity_search(mensagem, k=2)
                if docs:
                    contexto_rag = "Contexto da base:\n" + "\n".join([f"📄 {doc.metadata.get('source', 'Doc')}: {doc.page_content[:200]}" for doc in docs])
            except Exception as e:
                print(f"Erro RAG: {e}")
        
        # Gerar resposta
        resposta = chain.invoke({
            "input": mensagem,
            "contexto_rag": contexto_rag,
            "historico": historico
        })
        
        # Atualizar histórico
        historico_conversas[session_id].append(f"User: {mensagem}")
        historico_conversas[session_id].append(f"Helena: {resposta.content}")
        
        return resposta.content
    
    return responder

# Criar instância global
helena_recepcao = criar_helena_recepcao()