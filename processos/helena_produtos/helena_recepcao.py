from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os

def criar_helena_recepcao():
    """Helena Recepcionista - Versão Produção (sem Chroma)"""
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Você é Helena, assistente em GRC para o setor público brasileiro.

**PRODUTOS DISPONÍVEIS:**
✅ P1: Gerador de POP - Criar POPs estruturados (/chat/)
✅ P5: Análise de Riscos - Identificar riscos (/riscos/fluxo/)
✅ P2: Gerador de Fluxograma - Visualizar processos (/fluxograma/)

🔨 Em Desenvolvimento: P3, P4, P6-P11

Seja natural, prestativa e objetiva. Quando identificar necessidade, mencione o produto claramente.

Histórico: {historico}"""),
        ("human", "{input}")
    ])
    
    chain = prompt | llm
    historico_conversas = {}
    
    def responder(mensagem: str, session_id: str = "default"):
        if session_id not in historico_conversas:
            historico_conversas[session_id] = []
        
        historico = "\n".join(historico_conversas[session_id][-6:]) if historico_conversas[session_id] else "Primeira interação."
        
        resposta = chain.invoke({
            "input": mensagem,
            "historico": historico
        })
        
        historico_conversas[session_id].append(f"User: {mensagem}")
        historico_conversas[session_id].append(f"Helena: {resposta.content}")
        
        return resposta.content
    
    return responder

helena_recepcao = criar_helena_recepcao()