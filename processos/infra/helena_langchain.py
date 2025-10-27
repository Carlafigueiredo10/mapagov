from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
import os

class HelenaLangChain:
    def __init__(self):
        # Configurar modelo OpenAI
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Memória da conversa
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Template do prompt da Helena
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """Você é Helena, assistente especializada em Governança, Riscos e Conformidade (GRC) 
            para o setor público brasileiro. Você ajuda servidores públicos a documentar processos, 
            identificar riscos e garantir conformidade normativa."""),
            ("human", "{input}")
        ])
        
        # Criar chain
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            memory=self.memory,
            verbose=True
        )
    
    def processar_mensagem(self, mensagem_usuario):
        """Processa mensagem do usuário"""
        resposta = self.chain.invoke({"input": mensagem_usuario})
        return resposta['text']