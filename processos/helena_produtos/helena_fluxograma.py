from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferWindowMemory
import os
import json

class HelenaFluxograma:
    """Helena especializada em extrair processos para gerar fluxogramas visuais"""
    
    CAMPOS_FLUXOGRAMA = {
        "nome_processo": {"valor": None, "estado": None},
        "etapas": {"valor": [], "estado": None},  # Lista de etapas
        "decisoes": {"valor": [], "estado": None},  # Pontos de decisão (sim/não)
        "responsaveis": {"valor": {}, "estado": None},  # Quem faz cada etapa
        "sistemas": {"valor": [], "estado": None},  # Sistemas usados
        "tempo_medio": {"valor": None, "estado": None}  # Duração estimada
    }
    
    def __init__(self, dados_pdf=None):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=5
        )
        
        # Se receber dados do PDF, preencher automaticamente
        if dados_pdf:
            self._importar_dados_pdf(dados_pdf)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """Você é Helena, especialista em mapear processos para criar fluxogramas visuais.
            
            Seu objetivo: extrair a sequência de etapas, decisões e responsáveis de um processo.
            
            CAMPOS NECESSÁRIOS:
            1. nome_processo - Nome do processo
            2. etapas - Lista sequencial de passos (início → fim)
            3. decisoes - Pontos onde há bifurcação (sim/não, aprovado/rejeitado)
            4. responsaveis - Quem executa cada etapa
            5. sistemas - Sistemas utilizados em cada etapa
            6. tempo_medio - Quanto tempo leva o processo completo
            
            REGRAS:
            - Identifique a sequência lógica das etapas
            - Marque pontos de decisão claramente
            - Pergunte 1-2 itens por vez
            - Confirme entendimento antes de avançar
            
            FORMATO DE RESPOSTA (JSON):
            {{
                "resposta": "sua mensagem",
                "campo_preenchido": "campo ou null",
                "valor": "valor extraído",
                "progresso": "X/6",
                "completo": false
            }}"""),
            ("human", "{input}")
        ])
        
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            memory=self.memory,
            verbose=True
        )
        
        self.dados_coletados = self.CAMPOS_FLUXOGRAMA.copy()
    
    def _importar_dados_pdf(self, dados_pdf):
        """Importa dados extraídos do PDF do POP"""
        # Nome do processo
        if dados_pdf.get('atividade') or dados_pdf.get('titulo'):
            self.dados_coletados['nome_processo']['valor'] = dados_pdf.get('atividade') or dados_pdf.get('titulo')
            self.dados_coletados['nome_processo']['estado'] = 'confirmado'
        
        # Sistemas utilizados
        if dados_pdf.get('sistemas'):
            self.dados_coletados['sistemas']['valor'] = dados_pdf.get('sistemas')
            self.dados_coletados['sistemas']['estado'] = 'confirmado'
        
        # Responsáveis/Operadores
        if dados_pdf.get('operadores'):
            self.dados_coletados['responsaveis']['valor'] = {op: "A definir" for op in dados_pdf.get('operadores')}
            self.dados_coletados['responsaveis']['estado'] = 'pendente'
        
        # Nota: etapas e decisões precisam ser extraídas por conversa com Helena
    
    def processar_mensagem(self, mensagem_usuario):
        """Processa mensagem e extrai dados do fluxograma"""
        try:
            resposta = self.chain.invoke({"input": mensagem_usuario})
            resposta_texto = resposta['text']
            
            try:
                dados = json.loads(resposta_texto)
                
                if dados.get('campo_preenchido') and dados.get('valor'):
                    campo = dados['campo_preenchido']
                    if campo in self.dados_coletados:
                        self.dados_coletados[campo]['valor'] = dados['valor']
                        self.dados_coletados[campo]['estado'] = 'confirmado'
                
                confirmados = sum(1 for v in self.dados_coletados.values() if v['estado'] == 'confirmado')
                
                return {
                    "resposta": dados.get('resposta', resposta_texto),
                    "dados_extraidos": {dados['campo_preenchido']: dados['valor']} if dados.get('campo_preenchido') else {},
                    "conversa_completa": confirmados == 6,
                    "progresso": f"{confirmados}/6",
                    "tipo_resposta": "FILL" if dados.get('campo_preenchido') else "ASK"
                }
                
            except json.JSONDecodeError:
                return {
                    "resposta": resposta_texto,
                    "dados_extraidos": {},
                    "conversa_completa": False,
                    "progresso": "0/6",
                    "tipo_resposta": "ASK"
                }
                
        except Exception as e:
            return {
                "resposta": f"Erro: {str(e)}",
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": "0/6",
                "tipo_resposta": "ERROR"
            }
    
    def gerar_mermaid(self):
        """Gera código Mermaid para fluxograma visual"""
        dados = {k: v['valor'] for k, v in self.dados_coletados.items() if v['estado'] == 'confirmado'}
        
        mermaid = "graph TD\n"
        mermaid += f"    A[Início: {dados.get('nome_processo', 'Processo')}]\n"
        
        # Adicionar etapas
        etapas = dados.get('etapas', [])
        for i, etapa in enumerate(etapas, start=1):
            letra = chr(65 + i)  # B, C, D...
            mermaid += f"    {letra}[{etapa}]\n"
        
        # Conectar etapas
        for i in range(len(etapas)):
            letra_atual = chr(65 + i)
            letra_prox = chr(65 + i + 1)
            mermaid += f"    {letra_atual} --> {letra_prox}\n"
        
        return mermaid