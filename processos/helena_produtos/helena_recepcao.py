# ⚡ OTIMIZAÇÃO MEMÓRIA E CONCORRÊNCIA
from dotenv import load_dotenv
from collections import defaultdict, deque
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import logging

load_dotenv()

# 🔍 Setup básico de logging para produção
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def criar_helena_recepcao():
    """Helena Recepcionista - Produção otimizada com histórico leve e lazy loading seguro."""

    # ⚡ Lazy load das dependências e modelo
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """Você é Helena, recepcionista virtual especializada em GRC para o setor público brasileiro.

**SEU PAPEL:**
Você é uma RECEPCIONISTA, não uma executora. Sua função é:
1. Dar boas-vindas e entender a necessidade do usuário
2. DIRECIONAR o usuário para o produto correto
3. Responder dúvidas GERAIS sobre GRC (conceitos, normas, orientações)

❌ NÃO execute tarefas técnicas (mapear processos, criar POPs, analisar riscos etc.)
✅ SEMPRE redirecione o usuário ao produto adequado.

**PRODUTOS DISPONÍVEIS:**
- 🧩 P1: Gerador de POP → "Acesse o Gerador de POP para começar!"
- 🧠 P5: Análise de Riscos → "Vá para Análise de Riscos!"
- 🔄 P2: Gerador de Fluxograma → "Use o Gerador de Fluxograma!"

Em desenvolvimento: P3 (Dashboard), P4 (Conformidade), P6–P11.

**EXEMPLOS:**
User: "Quero mapear meu processo de análise de benefícios"
Helena: "Perfeito! Use o **Gerador de POP**. Lá eu te guio passo a passo! 🎯"

User: "Como identifico riscos no meu setor?"
Helena: "Para isso, use o produto **Análise de Riscos**. Clique no card correspondente no menu! 📊"

Histórico: {historico}
"""),
        ("human", "{input}")
    ])

    chain = prompt | llm
    historico_conversas = defaultdict(lambda: deque(maxlen=6))

    def responder(mensagem: str, session_id: str = "default"):
        try:
            # 📊 Log entrada (analytics)
            session_short = session_id[:8] if len(session_id) > 8 else session_id
            msg_preview = mensagem[:60] + ('...' if len(mensagem) > 60 else '')
            logging.info(f"[Helena Recepção] IN  [{session_short}...] {msg_preview}")

            historico = "\n".join(historico_conversas[session_id]) or "Primeira interação."
            resposta = chain.invoke({"input": mensagem, "historico": historico})

            historico_conversas[session_id].append(f"User: {mensagem}")
            historico_conversas[session_id].append(f"Helena: {resposta.content}")

            # 📊 Log saída (analytics)
            resp_preview = resposta.content[:60] + ('...' if len(resposta.content) > 60 else '')
            logging.info(f"[Helena Recepção] OUT [{session_short}...] {resp_preview}")

            return resposta.content

        except Exception as e:
            session_short = session_id[:8] if len(session_id) > 8 else session_id
            logging.error(f"[Helena Recepção] ERR [{session_short}...] {type(e).__name__}: {str(e)}")
            return "⚠️ Ocorreu um problema temporário. Pode tentar novamente em instantes?"

    return responder


# ⚡ LAZY INSTANCE: apenas quando usada
_helena_recepcao_instance = None

def helena_recepcao(mensagem: str, session_id: str = "default"):
    """Função wrapper para lazy loading da instância Helena Recepção"""
    global _helena_recepcao_instance
    if _helena_recepcao_instance is None:
        _helena_recepcao_instance = criar_helena_recepcao()
    return _helena_recepcao_instance(mensagem, session_id)
