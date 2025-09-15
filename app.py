# app.py - MapaGov Assistente GRC com IA
import streamlit as st
import json
import sqlite3
import requests
from datetime import datetime
import pandas as pd
import io
import base64

# Configuração da página
st.set_page_config(
    page_title="MapaGov - Assistente GRC",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2563eb, #4f46e5);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .step-container {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #2563eb;
        margin: 1rem 0;
    }
    .chat-container {
        background: #f0f9ff;
        border: 1px solid #0ea5e9;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .ai-message {
        background: #e0f2fe;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #0ea5e9;
    }
    .user-message {
        background: #f3f4f6;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        text-align: right;
        border-right: 3px solid #6b7280;
    }
    .risk-high {
        background: #fef2f2;
        border-left: 4px solid #dc2626;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .risk-medium {
        background: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .risk-low {
        background: #f0fdf4;
        border-left: 4px solid #10b981;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .success-box {
        background: #dcfce7;
        border: 1px solid #10b981;
        padding: 1rem;
        border-radius: 10px;
        color: #047857;
    }
</style>
""", unsafe_allow_html=True)

# =====================================
# NOVO: ASSISTENTE DE IA
# =====================================

class AIAssistant:
    """Assistente de IA especializado em mapeamento de processos"""
    
    def __init__(self):
        self.webhook_url = "https://carlafigueiredobsb.app.n8n.cloud/webhook/a1593b2b-924a-49c5-adb8-af42553cc3da"
        # Sistema de prompt especializado
        self.system_prompt = """
        Você é um assistente especializado em mapeamento de processos governamentais para o sistema MapaGov.
        
        CONTEXTO DO MAPAGOV:
        - Sistema de Governança, Riscos e Conformidade para setor público
        - Gera POPs (Procedimentos Operacionais Padrão) profissionais
        - Identifica riscos automaticamente
        - Cria fluxogramas em Mermaid
        - Segue padrões DECIPEX/MGI
        
        SUAS RESPONSABILIDADES:
        1. Ajudar usuários a mapear processos de forma clara e estruturada
        2. Sugerir melhorias baseadas em boas práticas de governança
        3. Explicar conceitos de GRC de forma didática
        4. Orientar sobre base legal e normativa
        5. Dar dicas sobre identificação de riscos
        
        DIRETRIZES:
        - Use linguagem clara e profissional
        - Seja específico e prático
        - Considere o contexto do setor público brasileiro
        - Foque em compliance e boas práticas
        - Sempre pergunte detalhes para melhorar a qualidade
        
        NUNCA:
        - Dê informações incorretas sobre legislação
        - Sugira práticas que violem princípios da administração pública
        - Seja genérico demais nas respostas
        """
    
    def get_contextual_help(self, current_step, form_data):
        """Gera ajuda contextual baseada na etapa atual"""
        
        context_prompts = {
            1: """O usuário está na ETAPA 1 - Identificação do Processo.
            Ajude com:
            - Como escolher um nome claro e descritivo
            - Diferenças entre processos Administrativos, Operacionais e Estratégicos
            - Como definir objetivos SMART para processos
            - Importância da criticidade inicial""",
            
            2: """O usuário está na ETAPA 2 - Estrutura do Processo.
            Ajude com:
            - Como organizar hierarquia de processos
            - Códigos de arquitetura de processos
            - Diferença entre macroprocesso, processo pai e subprocesso
            - Como identificar beneficiários finais""",
            
            3: """O usuário está na ETAPA 3 - Recursos Necessários.
            Ajude com:
            - Sistemas governamentais mais comuns (SIGEPE, SEI, SouGov)
            - Quando certificado digital é obrigatório
            - Tipos de acessos e permissões específicas
            - Softwares especializados por área""",
            
            4: """O usuário está na ETAPA 4 - Etapas do Processo.
            Ajude com:
            - Como quebrar processos em etapas lógicas
            - Definir responsáveis adequados
            - Estimativas de tempo realistas
            - Descrições claras e executáveis""",
            
            5: """O usuário está na ETAPA 5 - Base Legal e Normativa.
            Ajude com:
            - Hierarquia da legislação brasileira
            - Principais normas do setor público
            - Como identificar base legal aplicável
            - Diferença entre obrigatório e boas práticas"""
        }
        
        return context_prompts.get(current_step, "Ajude o usuário com questões gerais sobre mapeamento de processos.")
    
    def chat_with_ai(self, message, context=""):
        """Envia mensagem para a IA e retorna resposta"""
        try:
            payload = {
                "tipoOperacao": "assistente_chat",
                "mensagemUsuario": message,
                "contextoAtual": context,
                "sistemaPrompt": self.system_prompt
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                resultado = response.json()
                if isinstance(resultado, list) and len(resultado) > 0:
                    return resultado[0].get('resposta', self._get_fallback_response(message))
                else:
                    return resultado.get('resposta', self._get_fallback_response(message))
            else:
                return self._get_fallback_response(message)
                
        except Exception as e:
            return self._get_fallback_response(message)
    
    def _get_fallback_response(self, message):
        """Resposta de fallback quando API não funciona"""
        
        # Respostas inteligentes baseadas em palavras-chave
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['objetivo', 'finalidade', 'propósito']):
            return """
            📎 **Como definir objetivos de processo:**
            
            Um bom objetivo deve ser:
            - **Específico**: O que exatamente o processo faz?
            - **Mensurável**: Como medir o sucesso?
            - **Alcançável**: É realista?
            - **Relevante**: Contribui para a missão do órgão?
            - **Temporal**: Tem prazo definido?
            
            **Exemplo**: "Processar solicitações de licença em até 15 dias úteis, garantindo conformidade legal e satisfação do cidadão."
            """
        
        elif any(word in message_lower for word in ['etapa', 'passo', 'atividade']):
            return """
            📋 **Como estruturar etapas de processo:**
            
            1. **Sequência lógica**: Uma etapa deve levar naturalmente à próxima
            2. **Responsável claro**: Cada etapa deve ter um responsável definido
            3. **Descrição executável**: Use verbos de ação específicos
            4. **Tempo realista**: Considere carga de trabalho e complexidade
            
            **Dica**: Evite etapas muito genéricas como "analisar documento". Prefira "verificar completude dos documentos obrigatórios conforme check-list".
            """
        
        elif any(word in message_lower for word in ['risco', 'problema', 'falha']):
            return """
            ⚠️ **Identificação de riscos em processos:**
            
            **Tipos principais:**
            - **Operacional**: Falhas na execução, dependência de pessoas
            - **Legal**: Não conformidade com normas
            - **Reputacional**: Impacto na imagem do órgão
            - **Financeiro**: Perdas ou custos extras
            
            **Onde buscar riscos:**
            - Pontos de decisão humana
            - Interfaces entre sistemas
            - Prazos críticos
            - Documentos obrigatórios
            """
        
        elif any(word in message_lower for word in ['sistema', 'software', 'tecnologia']):
            return """
            💻 **Sistemas comuns no setor público:**
            
            **Gestão de Pessoas**: SIGEPE, SUAP
            **Documentos**: SEI, SIPAC
            **Financeiro**: SIAFI, SISCON
            **Compras**: COMPRASNET, SIASG
            **Governança**: SouGov, SISGE
            
            **Dica**: Sempre verifique se o sistema requer certificado digital ou perfis específicos de acesso.
            """
        
        elif any(word in message_lower for word in ['lei', 'decreto', 'norma', 'legal']):
            return """
            ⚖️ **Hierarquia normativa no setor público:**
            
            🔴 **Obrigatório por lei**:
            - Constituição Federal
            - Leis (8.429/92, 12.527/11, etc.)
            - Decretos
            
            🟠 **Obrigatório na APF**:
            - Instruções Normativas
            - Portarias ministeriais
            
            🟡 **Cobrança em auditorias**:
            - Referenciais TCU/CGU
            - Guias de boas práticas
            
            **Dica**: Sempre cite a norma específica, não apenas "conforme legislação".
            """
        
        else:
            return """
            👋 Olá! Sou seu assistente especializado em mapeamento de processos governamentais.
            
            **Posso ajudar com:**
            - Estruturação de processos
            - Identificação de riscos
            - Base legal e normativa
            - Sistemas e tecnologias
            - Boas práticas de GRC
            
            **Dica**: Seja específico na sua pergunta para receber ajuda mais direcionada!
            """

def show_ai_assistant():
    """Mostra o assistente de IA no sidebar"""
    
    # Inicializa o assistente
    if 'ai_assistant' not in st.session_state:
        st.session_state.ai_assistant = AIAssistant()
    
    # Inicializa histórico de chat
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    st.sidebar.markdown("### 🤖 Assistente IA")
    st.sidebar.markdown("*Especialista em mapeamento de processos*")
    
    # Contexto atual
    current_context = ""
    if 'form_step' in st.session_state and 'form_data' in st.session_state:
        current_context = f"Etapa {st.session_state.form_step} - {st.session_state.form_data.get('nome_processo', 'Processo não nomeado')}"
    
    # Campo de input para pergunta
    user_question = st.sidebar.text_area(
        "💬 Faça sua pergunta:",
        placeholder="Ex: Como definir um bom objetivo para o processo?",
        height=80,
        key="ai_question_input"
    )
    
    # Botões de ação
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🚀 Perguntar", key="ask_ai"):
            if user_question.strip():
                # Adiciona pergunta do usuário ao histórico
                st.session_state.chat_history.append({
                    'type': 'user',
                    'message': user_question,
                    'timestamp': datetime.now().strftime('%H:%M')
                })
                
                # Obtém resposta da IA
                with st.spinner("🤔 Pensando..."):
                    context_help = st.session_state.ai_assistant.get_contextual_help(
                        st.session_state.get('form_step', 1),
                        st.session_state.get('form_data', {})
                    )
                    
                    full_context = f"{context_help}\n\nContexto atual: {current_context}"
                    ai_response = st.session_state.ai_assistant.chat_with_ai(user_question, full_context)
                
                # Adiciona resposta da IA ao histórico
                st.session_state.chat_history.append({
                    'type': 'ai',
                    'message': ai_response,
                    'timestamp': datetime.now().strftime('%H:%M')
                })
                
                # Limpa o input
                st.session_state.ai_question_input = ""
                st.rerun()
    
    with col2:
        if st.button("🗑️ Limpar", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Sugestões rápidas baseadas na etapa atual
    if 'form_step' in st.session_state:
        st.sidebar.markdown("**💡 Sugestões rápidas:**")
        
        suggestions = {
            1: ["Como escolher tipo de processo?", "O que é criticidade?", "Exemplos de objetivos SMART"],
            2: ["O que é macroprocesso?", "Como definir beneficiários?", "Códigos de arquitetura"],
            3: ["Sistemas obrigatórios", "Quando usar certificado digital?", "Tipos de acesso"],
            4: ["Como dividir em etapas?", "Estimativa de tempo", "Responsáveis adequados"],
            5: ["Hierarquia das normas", "Base legal obrigatória", "TCU vs CGU vs ISO"]
        }
        
        current_suggestions = suggestions.get(st.session_state.form_step, ["Ajuda geral"])
        
        for suggestion in current_suggestions:
            if st.sidebar.button(f"❓ {suggestion}", key=f"suggestion_{suggestion}"):
                # Simula clique com a sugestão
                st.session_state.chat_history.append({
                    'type': 'user',
                    'message': suggestion,
                    'timestamp': datetime.now().strftime('%H:%M')
                })
                
                context_help = st.session_state.ai_assistant.get_contextual_help(
                    st.session_state.get('form_step', 1),
                    st.session_state.get('form_data', {})
                )
                
                full_context = f"{context_help}\n\nContexto atual: {current_context}"
                ai_response = st.session_state.ai_assistant.chat_with_ai(suggestion, full_context)
                
                st.session_state.chat_history.append({
                    'type': 'ai',
                    'message': ai_response,
                    'timestamp': datetime.now().strftime('%H:%M')
                })
                
                st.rerun()
    
    # Exibe histórico do chat
    if st.session_state.chat_history:
        st.sidebar.markdown("---")
        st.sidebar.markdown("**💬 Conversa:**")
        
        # Container com scroll para o chat
        chat_container = st.sidebar.container()
        
        with chat_container:
            for i, entry in enumerate(reversed(st.session_state.chat_history[-6:])):  # Últimas 6 mensagens
                if entry['type'] == 'user':
                    st.markdown(f"""
                    <div class="user-message">
                        <small>{entry['timestamp']}</small><br>
                        <strong>Você:</strong> {entry['message']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="ai-message">
                        <small>{entry['timestamp']}</small><br>
                        <strong>🤖 Assistente:</strong><br>
                        {entry['message']}
                    </div>
                    """, unsafe_allow_html=True)
        
        if len(st.session_state.chat_history) > 6:
            st.sidebar.caption(f"... e mais {len(st.session_state.chat_history) - 6} mensagens")
    
    # Dica de contexto
    if current_context:
        st.sidebar.info(f"📍 **Contexto atual:**\n{current_context}")

# =====================================
# MÓDULOS E CLASSES EXISTENTES
# =====================================

class DatabaseManager:
    """Gerenciador de banco de dados SQLite"""
    
    def __init__(self):
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados"""
        conn = sqlite3.connect('mapagov.db')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS processos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                departamento TEXT,
                responsavel TEXT,
                dados_formulario TEXT,
                pop_gerado TEXT,
                mermaid_code TEXT,
                riscos_json TEXT,
                estrategias_json TEXT,
                status TEXT DEFAULT 'rascunho',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def save_processo(self, dados):
        """Salva um processo no banco"""
        conn = sqlite3.connect('mapagov.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO processos 
            (nome, departamento, responsavel, dados_formulario, pop_gerado, 
             mermaid_code, riscos_json, estrategias_json, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            dados.get('nome_processo', ''),
            dados.get('departamento_orgao', ''),
            dados.get('responsavel_mapeamento', ''),
            json.dumps(dados),
            dados.get('pop_gerado', ''),
            dados.get('mermaid_code', ''),
            dados.get('riscos_json', ''),
            dados.get('estrategias_json', ''),
            dados.get('status', 'rascunho')
        ))
        
        processo_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return processo_id
    
    def get_processos(self):
        """Retorna todos os processos"""
        conn = sqlite3.connect('mapagov.db')
        df = pd.read_sql_query('''
            SELECT id, nome, departamento, responsavel, status, 
                   created_at, updated_at 
            FROM processos 
            ORDER BY created_at DESC
        ''', conn)
        conn.close()
        return df
    
    def get_processo_by_id(self, processo_id):
        """Retorna um processo específico"""
        conn = sqlite3.connect('mapagov.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM processos WHERE id = ?
        ''', (processo_id,))
        
        resultado = cursor.fetchone()
        conn.close()
        
        if resultado:
            colunas = ['id', 'nome', 'departamento', 'responsavel', 
                      'dados_formulario', 'pop_gerado', 'mermaid_code', 
                      'riscos_json', 'estrategias_json', 'status', 
                      'created_at', 'updated_at']
            return dict(zip(colunas, resultado))
        return None

class MermaidGenerator:
    """Gerador de fluxogramas Mermaid"""
    
    @staticmethod
    def generate_flowchart(etapas):
        """Gera código Mermaid para fluxograma"""
        if not etapas or len(etapas) == 0:
            return "graph TD\n  A[Nenhuma etapa definida]"
        
        mermaid_code = "graph TD\n"
        mermaid_code += "  INICIO((INÍCIO))\n"
        
        # Conecta início à primeira etapa
        if len(etapas) > 0:
            mermaid_code += f"  INICIO --> A0[{etapas[0].get('titulo', 'Etapa 1')}]\n"
        
        # Conecta etapas sequencialmente
        for i, etapa in enumerate(etapas):
            titulo = etapa.get('titulo', f'Etapa {i+1}')
            responsavel = etapa.get('responsavel', '')
            
            # Limita tamanho do título para melhor visualização
            if len(titulo) > 30:
                titulo = titulo[:27] + "..."
            
            if i < len(etapas) - 1:
                proximo_titulo = etapas[i+1].get('titulo', f'Etapa {i+2}')
                if len(proximo_titulo) > 30:
                    proximo_titulo = proximo_titulo[:27] + "..."
                mermaid_code += f"  A{i}[{titulo}] --> A{i+1}[{proximo_titulo}]\n"
            else:
                # Última etapa conecta ao fim
                mermaid_code += f"  A{i}[{titulo}] --> FIM((FIM))\n"
            
            # Adiciona responsável como nota
            if responsavel:
                mermaid_code += f"  A{i} -.->|{responsavel}| R{i}[ ]\n"
        
        # Estilo
        mermaid_code += "\n  classDef startEnd fill:#e1f5fe,stroke:#01579b,stroke-width:2px\n"
        mermaid_code += "  classDef process fill:#f3e5f5,stroke:#4a148c,stroke-width:1px\n"
        mermaid_code += "  class INICIO,FIM startEnd\n"
        
        for i in range(len(etapas)):
            mermaid_code += f"A{i},"
        mermaid_code = mermaid_code.rstrip(",")
        mermaid_code += " process\n"
        
        return mermaid_code

class AIAnalyzer:
    """Analisador de riscos usando IA"""
    
    def __init__(self):
        self.webhook_url = "https://carlafigueiredobsb.app.n8n.cloud/webhook/a1593b2b-924a-49c5-adb8-af42553cc3da"
    
    def analyze_risks(self, processo_dados):
        """Analisa riscos do processo usando IA"""
        try:
            # Prepara payload para análise de riscos
            payload = {
                "tipoOperacao": "analise_riscos",
                "nomeProcesso": processo_dados.get('nome_processo', ''),
                "departamentoOrgao": processo_dados.get('departamento_orgao', ''),
                "objetivoProcesso": processo_dados.get('objetivo_processo', ''),
                "etapas": processo_dados.get('etapas', []),
                "sistemasUtilizados": ", ".join(processo_dados.get('sistemas_utilizados', [])),
                "baseLegal": processo_dados.get('base_legal', {}),
                "analiseCompleta": True
            }
            
            # Faz requisição para o webhook
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=60
            )
            
            if response.status_code == 200:
                resultado = response.json()
                
                # Se retornar array, pega primeiro elemento
                if isinstance(resultado, list) and len(resultado) > 0:
                    return resultado[0].get('riscos', self._generate_mock_risks(processo_dados))
                else:
                    return resultado.get('riscos', self._generate_mock_risks(processo_dados))
            else:
                st.error(f"Erro na API: {response.status_code}")
                return self._generate_mock_risks(processo_dados)
                
        except Exception as e:
            st.error(f"Erro ao analisar riscos: {str(e)}")
            return self._generate_mock_risks(processo_dados)
    
    def _generate_mock_risks(self, processo_dados):
        """Gera riscos simulados para demonstração"""
        etapas = processo_dados.get('etapas', [])
        riscos = []
        
        categorias_risco = [
            "Operacional", "Financeiro", "Legal", "Reputacional", "Compliance"
        ]
        
        for i, etapa in enumerate(etapas[:3]):  # Analisa até 3 etapas
            for categoria in categorias_risco[:2]:  # 2 categorias por etapa
                risco = {
                    "id": f"R{i+1}_{categoria[:3].upper()}",
                    "etapa": etapa.get('titulo', f'Etapa {i+1}'),
                    "categoria": categoria,
                    "descricao": f"Risco {categoria.lower()} identificado na etapa '{etapa.get('titulo', 'Sem título')}'",
                    "probabilidade": 3 if i % 2 == 0 else 2,
                    "impacto": 3 if categoria in ["Legal", "Compliance"] else 2,
                    "nivel": "Médio" if i % 2 == 0 else "Baixo",
                    "controles_sugeridos": [
                        f"Implementar controle preventivo para {categoria.lower()}",
                        f"Monitoramento contínuo de {categoria.lower()}",
                        f"Plano de contingência para {categoria.lower()}"
                    ]
                }
                riscos.append(risco)
        
        return riscos
    
    def generate_strategies(self, riscos):
        """Gera estratégias de mitigação"""
        try:
            payload = {
                "tipoOperacao": "estrategias_mitigacao",
                "riscos": riscos
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=60
            )
            
            if response.status_code == 200:
                resultado = response.json()
                if isinstance(resultado, list) and len(resultado) > 0:
                    return resultado[0].get('estrategias', self._generate_mock_strategies(riscos))
                else:
                    return resultado.get('estrategias', self._generate_mock_strategies(riscos))
            else:
                return self._generate_mock_strategies(riscos)
                
        except Exception as e:
            st.error(f"Erro ao gerar estratégias: {str(e)}")
            return self._generate_mock_strategies(riscos)
    
    def _generate_mock_strategies(self, riscos):
        """Gera estratégias simuladas"""
        estrategias = []
        
        for risco in riscos:
            estrategia = {
                "risco_id": risco.get('id'),
                "estrategia_recomendada": "Mitigar" if risco.get('nivel') == "Alto" else "Monitorar",
                "acoes": [
                    f"Implementar controles para {risco.get('categoria', 'categoria')}",
                    f"Treinamento da equipe responsável",
                    f"Revisão periódica do processo"
                ],
                "responsavel_sugerido": "Coordenador do Processo",
                "prazo": "30 dias" if risco.get('nivel') == "Alto" else "60 dias",
                "custo_estimado": "Baixo" if risco.get('nivel') == "Baixo" else "Médio"
            }
            estrategias.append(estrategia)
        
        return estrategias

# =====================================
# FUNÇÕES AUXILIARES
# =====================================

def gerar_pop(dados_formulario):
    """Gera POP usando webhook"""
    try:
        payload = {
            "tipoOperacao": "pop_inicial",
            "nomeProcesso": dados_formulario.get('nome_processo', ''),
            "departamentoOrgao": dados_formulario.get('departamento_orgao', ''),
            "objetivoProcesso": dados_formulario.get('objetivo_processo', ''),
            "codigoArquitetura": dados_formulario.get('codigo_arquitetura', ''),
            "macroprocesso": dados_formulario.get('macroprocesso', ''),
            "processoPai": dados_formulario.get('processo_pai', ''),
            "subprocesso": dados_formulario.get('subprocesso', ''),
            "etapas": dados_formulario.get('etapas', []),
            "entradasDocumentacoes": dados_formulario.get('entrega_esperada', ''),
            "saidasResultados": dados_formulario.get('beneficiario', ''),
            "sistemasUtilizados": ", ".join(dados_formulario.get('sistemas_utilizados', [])),
            "participantesResponsaveis": dados_formulario.get('responsavel_mapeamento', ''),
            "baseLegal": dados_formulario.get('base_legal', {})
        }
        
        response = requests.post(
            "https://carlafigueiredobsb.app.n8n.cloud/webhook/a1593b2b-924a-49c5-adb8-af42553cc3da",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        if response.status_code == 200:
            resultado = response.json()
            if isinstance(resultado, list) and len(resultado) > 0:
                return resultado[0].get('pop', 'POP gerado com sucesso!')
            else:
                return resultado.get('pop', 'POP gerado com sucesso!')
        else:
            return f"Erro na geração do POP: {response.status_code}"
            
    except Exception as e:
        return f"Erro ao gerar POP: {str(e)}"

def download_pdf(content, filename):
    """Gera link de download para PDF"""
    # Simula geração de PDF (aqui você implementaria a geração real)
    pdf_content = f"PROCEDIMENTO OPERACIONAL PADRÃO\n\n{content}"
    b64 = base64.b64encode(pdf_content.encode()).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}.txt">📄 Download POP</a>'
    return href

# =====================================
# INTERFACE PRINCIPAL - MODIFICADA PARA INCLUIR IA
# =====================================

def main():
    """Função principal da aplicação"""
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🛡️ MapaGov - Assistente GRC</h1>
        <p>Governança, Riscos e Conformidade para o Setor Público</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializa banco de dados
    db = DatabaseManager()
    
    # Sidebar para navegação E assistente IA
    with st.sidebar:
        st.image("https://via.placeholder.com/200x100/2563eb/ffffff?text=MapaGov", width=200)
        
        page = st.selectbox(
            "🧭 Navegação",
            ["🏠 Dashboard", "📝 Novo Mapeamento", "📊 Resultados", "📋 Biblioteca"],
            key="navigation"
        )
        
        st.markdown("---")
        
        # NOVO: Assistente de IA integrado no sidebar
        show_ai_assistant()
        
        st.markdown("---")
        st.markdown("### 📈 Estatísticas")
        try:
            processos_df = db.get_processos()
            st.metric("Processos Mapeados", len(processos_df))
            st.metric("Em Desenvolvimento", len(processos_df[processos_df['status'] == 'rascunho']))
            st.metric("Finalizados", len(processos_df[processos_df['status'] == 'finalizado']))
        except:
            st.metric("Processos Mapeados", 0)
        
        st.markdown("---")
        st.markdown("### 🔗 Links Úteis")
        st.markdown("- [TCU - Referencial de Governança](https://portal.tcu.gov.br)")
        st.markdown("- [CGU - Gestão de Riscos](https://www.gov.br/cgu)")
        st.markdown("- [ISO 31000:2018](https://www.iso.org)")
    
    # Roteamento de páginas
    if page == "🏠 Dashboard":
        show_dashboard(db)
    elif page == "📝 Novo Mapeamento":
        show_mapping_form(db)
    elif page == "📊 Resultados":
        show_results(db)
    elif page == "📋 Biblioteca":
        show_library(db)

def show_dashboard(db):
    """Mostra o dashboard principal"""
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        processos_df = db.get_processos()
        total_processos = len(processos_df)
        processos_mes = len(processos_df[processos_df['created_at'].str.startswith(datetime.now().strftime('%Y-%m'))])
    except:
        total_processos = 0
        processos_mes = 0
    
    with col1:
        st.metric(
            label="📋 Total de Processos",
            value=total_processos,
            delta=f"+{processos_mes} este mês"
        )
    
    with col2:
        st.metric(
            label="⚠️ Riscos Identificados",
            value=total_processos * 3,  # Simulado
            delta="+12 novos"
        )
    
    with col3:
        st.metric(
            label="✅ POPs Gerados",
            value=total_processos,
            delta=f"+{processos_mes}"
        )
    
    with col4:
        st.metric(
            label="📊 Conformidade",
            value="87%",
            delta="+5%"
        )
    
    st.markdown("---")
    
    # NOVO: Banner do assistente de IA
    st.info("🤖 **Novo! Assistente de IA disponível no menu lateral** - Faça perguntas sobre mapeamento de processos!")
    
    # Cards de módulos
    st.subheader("🎯 Módulos Disponíveis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container():
            st.markdown("""
            <div class="step-container">
                <h4>📝 Mapeamento de Processos</h4>
                <p>Documente processos com padrão profissional equivalente ao DECIPEX/MGI</p>
                <span style="background: #10b981; color: white; padding: 0.2rem 0.5rem; border-radius: 10px; font-size: 0.8rem;">ATIVO</span>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 Iniciar Mapeamento", key="start_mapping"):
                st.session_state.navigation = "📝 Novo Mapeamento"
                st.rerun()
    
    with col2:
        with st.container():
            st.markdown("""
            <div class="step-container">
                <h4>⚠️ Identificação de Riscos</h4>
                <p>Análise automática de riscos operacionais, financeiros, legais e reputacionais</p>
                <span style="background: #10b981; color: white; padding: 0.2rem 0.5rem; border-radius: 10px; font-size: 0.8rem;">ATIVO</span>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔍 Analisar Riscos", key="analyze_risks"):
                st.info("💡 Primeiro mapeie um processo para analisar riscos!")
    
    with col3:
        with st.container():
            st.markdown("""
            <div class="step-container">
                <h4>🛡️ Controles e Mitigação</h4>
                <p>Propostas práticas de controles para gerenciar e mitigar riscos identificados</p>
                <span style="background: #10b981; color: white; padding: 0.2rem 0.5rem; border-radius: 10px; font-size: 0.8rem;">ATIVO</span>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("⚙️ Gerenciar Controles", key="manage_controls"):
                st.info("💡 Primeiro identifique riscos para gerenciar controles!")
    
    # Módulos futuros
    st.markdown("### 🔮 Próximas Funcionalidades")
    
    col1, col2, col3 = st.columns(3)
    
    modules_future = [
        {"title": "👁️ Auditoria e Conformidade", "desc": "Link para sistemas externos", "status": "FUTURO"},
        {"title": "📈 Indicadores de Performance", "desc": "Link para SisGRC/Sisge", "status": "FUTURO"},
        {"title": "📁 Gestão Documental", "desc": "Centralização de documentos GRC", "status": "FUTURO"}
    ]
    
    for i, module in enumerate(modules_future):
        with [col1, col2, col3][i]:
            st.markdown(f"""
            <div style="background: #f9fafb; padding: 1rem; border-radius: 10px; border: 1px dashed #d1d5db; opacity: 0.7;">
                <h5>{module['title']}</h5>
                <p style="font-size: 0.9rem; color: #6b7280;">{module['desc']}</p>
                <span style="background: #fbbf24; color: white; padding: 0.2rem 0.5rem; border-radius: 10px; font-size: 0.8rem;">{module['status']}</span>
            </div>
            """, unsafe_allow_html=True)
    
    # Processos recentes
    st.markdown("---")
    st.subheader("📋 Processos Recentes")
    
    try:
        processos_df = db.get_processos()
        if len(processos_df) > 0:
            # Mostra últimos 5 processos
            processos_recentes = processos_df.head(5)
            
            for _, processo in processos_recentes.iterrows():
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    
                    with col1:
                        st.write(f"**{processo['nome']}**")
                        st.caption(f"📅 {processo['created_at']}")
                    
                    with col2:
                        st.write(f"🏢 {processo['departamento']}")
                    
                    with col3:
                        status_color = "🟡" if processo['status'] == 'rascunho' else "🟢"
                        st.write(f"{status_color} {processo['status'].title()}")
                    
                    with col4:
                        if st.button("👁️", key=f"view_{processo['id']}", help="Visualizar"):
                            st.session_state.selected_processo_id = processo['id']
                            st.session_state.navigation = "📊 Resultados"
                            st.rerun()
                    
                    st.markdown("---")
        else:
            st.info("📝 Nenhum processo mapeado ainda. Comece criando seu primeiro processo!")
            if st.button("🚀 Criar Primeiro Processo"):
                st.session_state.navigation = "📝 Novo Mapeamento"
                st.rerun()
    except Exception as e:
        st.error(f"Erro ao carregar processos: {str(e)}")

def show_mapping_form(db):
    """Mostra o formulário de mapeamento com assistente IA"""
    
    st.title("📝 Mapeamento de Processos")
    st.markdown("Complete as informações abaixo para mapear seu processo organizacional.")
    
    # NOVO: Dica sobre o assistente
    st.info("💡 **Dica:** Use o assistente de IA no menu lateral para tirar dúvidas sobre cada etapa!")
    
    # Progress bar
    if 'form_step' not in st.session_state:
        st.session_state.form_step = 1
    
    progress = st.session_state.form_step / 5
    st.progress(progress, text=f"Etapa {st.session_state.form_step} de 5")
    
    # Inicializa dados do formulário
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {
            'nome_processo': '',
            'departamento_orgao': '',
            'responsavel_mapeamento': '',
            'objetivo_processo': '',
            'tipo_processo': 'Administrativo',
            'criticidade': 'Média',
            'codigo_arquitetura': '',
            'macroprocesso': '',
            'processo_pai': '',
            'subprocesso': '',
            'entrega_esperada': '',
            'beneficiario': '',
            'base_normativa': '',
            'sistemas_utilizados': [],
            'certificado_digital': False,
            'acessos_especificos': '',
            'softwares_obrigatorios': [],
            'etapas': [{'titulo': '', 'responsavel': '', 'descricao': '', 'tempo_estimado': ''}],
            'base_legal': {
                'leis_decretos': '',
                'instrucoes_portarias': '',
                'referenciais_tcu_cgu': '',
                'normas_tecnicas_internacionais': '',
                'guias_internos_metodologias': ''
            }
        }
    
    # Formulário por etapas
    if st.session_state.form_step == 1:
        show_identification_step()
    elif st.session_state.form_step == 2:
        show_structure_step()
    elif st.session_state.form_step == 3:
        show_resources_step()
    elif st.session_state.form_step == 4:
        show_process_steps()
    elif st.session_state.form_step == 5:
        show_legal_base_step()
    
    # Navegação
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.form_step > 1:
            if st.button("⬅️ Anterior", key="prev_step"):
                st.session_state.form_step -= 1
                st.rerun()
    
    with col2:
        if st.session_state.form_step < 5:
            if st.button("Próximo ➡️", key="next_step"):
                st.session_state.form_step += 1
                st.rerun()
        else:
            if st.button("🚀 Gerar POP", key="generate_pop", type="primary"):
                generate_complete_analysis(db)

def show_identification_step():
    """Etapa 1: Identificação do Processo"""
    
    st.markdown("""
    <div class="step-container">
        <h3>👤 Etapa 1: Identificação do Processo</h3>
        <p>Defina as características básicas do processo organizacional</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.form_data['nome_processo'] = st.text_input(
            "Nome do Processo *",
            value=st.session_state.form_data['nome_processo'],
            placeholder="Digite o nome do processo...",
            help="Nome claro e descritivo do processo"
        )
        
        st.session_state.form_data['departamento_orgao'] = st.text_input(
            "Departamento/Órgão *",
            value=st.session_state.form_data['departamento_orgao'],
            placeholder="Ex: Secretaria de Administração"
        )
        
        st.session_state.form_data['responsavel_mapeamento'] = st.text_input(
            "Responsável pelo Mapeamento *",
            value=st.session_state.form_data['responsavel_mapeamento'],
            placeholder="Nome do responsável"
        )
    
    with col2:
        st.session_state.form_data['tipo_processo'] = st.selectbox(
            "Tipo de Processo",
            options=["Administrativo", "Operacional", "Estratégico"],
            index=["Administrativo", "Operacional", "Estratégico"].index(st.session_state.form_data['tipo_processo'])
        )
        
        st.session_state.form_data['criticidade'] = st.selectbox(
            "Nível de Criticidade",
            options=["Baixa", "Média", "Alta"],
            index=["Baixa", "Média", "Alta"].index(st.session_state.form_data['criticidade']),
            help="A criticidade será refinada com base na análise"
        )
    
    st.session_state.form_data['objetivo_processo'] = st.text_area(
        "Objetivo do Processo *",
        value=st.session_state.form_data['objetivo_processo'],
        placeholder="Descreva de forma clara o propósito principal deste processo...",
        height=100,
        help="Seja específico sobre o que o processo busca alcançar"
    )

# [RESTO DAS FUNÇÕES PERMANECEM IGUAIS - show_structure_step, show_resources_step, etc.]

# =====================================
# EXECUÇÃO PRINCIPAL
# =====================================

if __name__ == "__main__":
    main()
