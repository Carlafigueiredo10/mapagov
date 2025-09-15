# app.py - MapaGov Assistente GRC
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
    .ai-assistant-box {
        background: #f0f9ff;
        border: 2px solid #0ea5e9;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# =====================================
# MÓDULOS E CLASSES
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
# INTERFACE PRINCIPAL
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
    
    # Sidebar para navegação
    with st.sidebar:
        st.image("https://via.placeholder.com/200x100/2563eb/ffffff?text=MapaGov", width=200)
        
        page = st.selectbox(
            "🧭 Navegação",
            ["🏠 Dashboard", "📝 Novo Mapeamento", "📊 Resultados", "📋 Biblioteca"],
            key="navigation"
        )
        
        st.markdown("---")
        
        # NOVO: Assistente de IA externo
        st.markdown("""
        <div class="ai-assistant-box">
            <h4>🤖 Assistente de IA</h4>
            <p><em>Especialista em mapeamento de processos</em></p>
            <a href="https://chatgpt.com/g/g-68c88d57be788191982f070e61d0072c-mapagov" 
               target="_blank" 
               style="background: #10b981; color: white; padding: 0.5rem 1rem; 
                      text-decoration: none; border-radius: 5px; display: inline-block;">
                💬 Conversar com IA
            </a>
            <br><br>
            <small>Tire dúvidas sobre processos, riscos, normas e muito mais!</small>
        </div>
        """, unsafe_allow_html=True)
        
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
    
    # Banner do assistente de IA
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
    """Mostra o formulário de mapeamento"""
    
    st.title("📝 Mapeamento de Processos")
    st.markdown("Complete as informações abaixo para mapear seu processo organizacional.")
    
    # Dica sobre o assistente
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

def show_structure_step():
    """Etapa 2: Estrutura do Processo"""
    
    st.markdown("""
    <div class="step-container">
        <h3>🏗️ Etapa 2: Estrutura do Processo</h3>
        <p>Organize o processo na arquitetura institucional (opcional)</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 Esta etapa é opcional, mas ajuda na organização hierárquica dos processos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.form_data['codigo_arquitetura'] = st.text_input(
            "Código na Arquitetura",
            value=st.session_state.form_data['codigo_arquitetura'],
            placeholder="Ex: ADM.001.001"
        )
        
        st.session_state.form_data['macroprocesso'] = st.text_input(
            "Macroprocesso",
            value=st.session_state.form_data['macroprocesso'],
            placeholder="Ex: Gestão de Pessoas"
        )
    
    with col2:
        st.session_state.form_data['processo_pai'] = st.text_input(
            "Processo Pai",
            value=st.session_state.form_data['processo_pai'],
            placeholder="Processo hierarquicamente superior"
        )
        
        st.session_state.form_data['subprocesso'] = st.text_input(
            "Subprocesso",
            value=st.session_state.form_data['subprocesso'],
            placeholder="Detalhamento específico"
        )
    
    st.session_state.form_data['entrega_esperada'] = st.text_area(
        "Entrega Esperada da Atividade",
        value=st.session_state.form_data['entrega_esperada'],
        placeholder="Descreva qual é a entrega final esperada deste processo...",
        height=80
    )
    
    st.session_state.form_data['beneficiario'] = st.text_input(
        "Quem se Beneficia do Resultado",
        value=st.session_state.form_data['beneficiario'],
        placeholder="Ex: Cidadãos, servidores, outras unidades organizacionais..."
    )

def show_resources_step():
    """Etapa 3: Recursos Necessários"""
    
    st.markdown("""
    <div class="step-container">
        <h3>⚙️ Etapa 3: Recursos Necessários</h3>
        <p>Identifique sistemas, acessos e ferramentas obrigatórias</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sistemas utilizados
    st.subheader("💻 Sistemas Informatizados")
    
    # Mostra sistemas já adicionados
    if st.session_state.form_data['sistemas_utilizados']:
        st.write("**Sistemas adicionados:**")
        for i, sistema in enumerate(st.session_state.form_data['sistemas_utilizados']):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"• {sistema}")
            with col2:
                if st.button("🗑️", key=f"remove_sistema_{i}", help="Remover"):
                    st.session_state.form_data['sistemas_utilizados'].pop(i)
                    st.rerun()
    
    # Adicionar novo sistema
    col1, col2 = st.columns([4, 1])
    with col1:
        novo_sistema = st.text_input(
            "Adicionar Sistema",
            placeholder="Ex: SIGEPE, SEI, SouGov...",
            key="novo_sistema"
        )
    with col2:
        if st.button("➕ Adicionar", key="add_sistema"):
            if novo_sistema and novo_sistema not in st.session_state.form_data['sistemas_utilizados']:
                st.session_state.form_data['sistemas_utilizados'].append(novo_sistema)
                st.rerun()
    
    # Certificado digital
    st.session_state.form_data['certificado_digital'] = st.checkbox(
        "🔐 Certificado Digital Necessário",
        value=st.session_state.form_data['certificado_digital'],
        help="Marque se o processo requer autenticação com certificado digital"
    )
    
    # Acessos específicos
    st.session_state.form_data['acessos_especificos'] = st.text_area(
        "Acessos Específicos Necessários",
        value=st.session_state.form_data['acessos_especificos'],
        placeholder="Descreva perfis de acesso, permissões especiais, credenciais específicas...",
        height=100
    )

def show_process_steps():
    """Etapa 4: Etapas do Processo"""
    
    st.markdown("""
    <div class="step-container">
        <h3>⏱️ Etapa 4: Etapas do Processo</h3>
        <p>Descreva o fluxo sequencial de atividades (mínimo 1, máximo 20)</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 Descreva cada etapa de forma clara e sequencial. Estas informações serão usadas para gerar o POP profissional.")
    
    # Mostra etapas existentes
    for i, etapa in enumerate(st.session_state.form_data['etapas']):
        with st.expander(f"📋 Etapa {i+1}: {etapa.get('titulo', 'Sem título')}", expanded=i==0):
            col1, col2 = st.columns([5, 1])
            
            with col1:
                # Título da etapa
                etapa['titulo'] = st.text_input(
                    "Título da Etapa",
                    value=etapa.get('titulo', ''),
                    placeholder="Ex: Análise inicial da documentação",
                    key=f"etapa_titulo_{i}"
                )
                
                # Responsável e tempo
                col_resp, col_tempo = st.columns(2)
                
                with col_resp:
                    etapa['responsavel'] = st.selectbox(
                        "Responsável",
                        options=["", "Técnico Especializado", "Coordenador", "Apoio-Gabinete", 
                                "Analista", "Gestor", "Servidor Requisitante", "Secretário/Diretor"],
                        index=0 if not etapa.get('responsavel') else 
                              ["", "Técnico Especializado", "Coordenador", "Apoio-Gabinete", 
                               "Analista", "Gestor", "Servidor Requisitante", "Secretário/Diretor"].index(etapa['responsavel']),
                        key=f"etapa_responsavel_{i}"
                    )
                
                with col_tempo:
                    etapa['tempo_estimado'] = st.text_input(
                        "Tempo Estimado",
                        value=etapa.get('tempo_estimado', ''),
                        placeholder="Ex: 2 dias úteis",
                        key=f"etapa_tempo_{i}"
                    )
                
                # Descrição
                etapa['descricao'] = st.text_area(
                    "Descrição Detalhada da Tarefa",
                    value=etapa.get('descricao', ''),
                    placeholder="Descreva detalhadamente o que deve ser feito nesta etapa...",
                    height=100,
                    key=f"etapa_descricao_{i}"
                )
            
            with col2:
                if len(st.session_state.form_data['etapas']) > 1:
                    if st.button("🗑️", key=f"remove_etapa_{i}", help="Remover etapa"):
                        st.session_state.form_data['etapas'].pop(i)
                        st.rerun()
    
    # Adicionar nova etapa
    if len(st.session_state.form_data['etapas']) < 20:
        if st.button("➕ Adicionar Nova Etapa", key="add_etapa"):
            st.session_state.form_data['etapas'].append({
                'titulo': '', 'responsavel': '', 'descricao': '', 'tempo_estimado': ''
            })
            st.rerun()
    else:
        st.warning("⚠️ Máximo de 20 etapas atingido")

def show_legal_base_step():
    """Etapa 5: Base Legal e Normativa"""
    
    st.markdown("""
    <div class="step-container">
        <h3>⚖️ Etapa 5: Base Legal e Normativa</h3>
        <p>Fundamentação legal categorizada por nível de obrigatoriedade</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 A categorização por cores facilita a identificação do nível de obrigatoriedade")
    
    # Categorias legais
    categorias = [
        {
            'key': 'leis_decretos',
            'emoji': '🔴',
            'title': 'LEIS E DECRETOS',
            'subtitle': 'obrigatórios por força de lei',
            'placeholder': 'Ex: Decreto nº 9.203/2017, Lei 8.429/1992, Art. 37 da CF/88...',
            'examples': ['Decreto nº 9.203/2017', 'Lei 8.429/1992', 'Art. 37 da CF/88']
        },
        {
            'key': 'instrucoes_portarias',
            'emoji': '🟠',
            'title': 'INSTRUÇÕES NORMATIVAS E PORTARIAS',
            'subtitle': 'obrigatórios na APF',
            'placeholder': 'Ex: IN Conjunta MP/CGU nº 01/2016, Portaria CGU nº 910/2018...',
            'examples': ['IN Conjunta MP/CGU nº 01/2016', 'Portaria CGU nº 910/2018']
        },
        {
            'key': 'referenciais_tcu_cgu',
            'emoji': '🟡',
            'title': 'REFERENCIAIS TCU/CGU',
            'subtitle': 'cobrança em auditorias',
            'placeholder': 'Ex: Referencial Básico de Governança TCU, Guia de Gestão de Riscos CGU...',
            'examples': ['Referencial Básico de Governança TCU', 'Guia de Gestão de Riscos CGU']
        },
        {
            'key': 'normas_tecnicas_internacionais',
            'emoji': '🔵',
            'title': 'NORMAS TÉCNICAS INTERNACIONAIS',
            'subtitle': 'boas práticas robustas',
            'placeholder': 'Ex: ISO 31000:2018, COSO ERM 2017, Código IBGC 2023...',
            'examples': ['ISO 31000:2018', 'COSO ERM 2017', 'Código IBGC 2023']
        },
        {
            'key': 'guias_internos_metodologias',
            'emoji': '⚪',
            'title': 'GUIAS INTERNOS E METODOLOGIAS',
            'subtitle': 'nível operacional',
            'placeholder': 'Ex: Guia Prático de Projetos MGI, Metodologias setoriais...',
            'examples': ['Guia Prático de Projetos MGI', 'Metodologias setoriais']
        }
    ]
    
    for categoria in categorias:
        st.markdown(f"""
        **{categoria['emoji']} {categoria['title']}** _{categoria['subtitle']}_
        """)
        
        with st.expander(f"💡 Exemplos de {categoria['title'].lower()}"):
            for exemplo in categoria['examples']:
                st.write(f"• {exemplo}")
        
        st.session_state.form_data['base_legal'][categoria['key']] = st.text_area(
            f"",
            value=st.session_state.form_data['base_legal'][categoria['key']],
            placeholder=categoria['placeholder'],
            height=80,
            key=f"legal_{categoria['key']}"
        )
        
        st.markdown("---")

def generate_complete_analysis(db):
    """Gera análise completa: POP + Fluxograma + Riscos + Estratégias"""
    
    # Validação básica
    if not st.session_state.form_data['nome_processo']:
        st.error("❌ Nome do processo é obrigatório!")
        return
    
    if not st.session_state.form_data['objetivo_processo']:
        st.error("❌ Objetivo do processo é obrigatório!")
        return
    
    if not any(etapa.get('titulo') for etapa in st.session_state.form_data['etapas']):
        st.error("❌ Pelo menos uma etapa com título é obrigatória!")
        return
    
    # Inicia processamento
    with st.spinner("🔄 Gerando análise completa do processo..."):
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 1. Gerar POP
        status_text.text("📝 Gerando POP...")
        progress_bar.progress(0.2)
        
        pop_gerado = gerar_pop(st.session_state.form_data)
        st.session_state.form_data['pop_gerado'] = pop_gerado
        
        # 2. Gerar Fluxograma
        status_text.text("📊 Gerando fluxograma...")
        progress_bar.progress(0.4)
        
        mermaid_gen = MermaidGenerator()
        mermaid_code = mermaid_gen.generate_flowchart(st.session_state.form_data['etapas'])
        st.session_state.form_data['mermaid_code'] = mermaid_code
        
        # 3. Analisar Riscos
        status_text.text("⚠️ Analisando riscos...")
        progress_bar.progress(0.6)
        
        ai_analyzer = AIAnalyzer()
        riscos = ai_analyzer.analyze_risks(st.session_state.form_data)
        st.session_state.form_data['riscos_json'] = json.dumps(riscos)
        
        # 4. Gerar Estratégias
        status_text.text("🛡️ Gerando estratégias de mitigação...")
        progress_bar.progress(0.8)
        
        estrategias = ai_analyzer.generate_strategies(riscos)
        st.session_state.form_data['estrategias_json'] = json.dumps(estrategias)
        
        # 5. Salvar no banco
        status_text.text("💾 Salvando processo...")
        progress_bar.progress(1.0)
        
        processo_id = db.save_processo(st.session_state.form_data)
        st.session_state.current_processo_id = processo_id
        
        progress_bar.empty()
        status_text.empty()
    
    # Sucesso!
    st.markdown("""
    <div class="success-box">
        <h3>🎉 Processo Analisado com Sucesso!</h3>
        <p>POP gerado, fluxograma criado, riscos identificados e estratégias propostas.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("👁️ Ver Resultados", type="primary"):
            st.session_state.navigation = "📊 Resultados"
            st.session_state.selected_processo_id = processo_id
            st.rerun()
    
    with col2:
        if st.button("📝 Novo Processo"):
            # Reset form data
            del st.session_state.form_data
            st.session_state.form_step = 1
            st.rerun()

def show_results(db):
    """Mostra os resultados da análise"""
    
    st.title("📊 Resultados da Análise")
    
    # Selecionar processo
    processos_df = db.get_processos()
    
    if len(processos_df) == 0:
        st.info("📝 Nenhum processo encontrado. Primeiro mapeie um processo!")
        if st.button("🚀 Mapear Novo Processo"):
            st.session_state.navigation = "📝 Novo Mapeamento"
            st.rerun()
        return
    
    # Seleção de processo
    selected_id = st.selectbox(
        "Selecione um processo:",
        options=processos_df['id'].tolist(),
        format_func=lambda x: f"{processos_df[processos_df['id']==x]['nome'].iloc[0]} - {processos_df[processos_df['id']==x]['departamento'].iloc[0]}",
        index=0
    )
    
    # Carrega dados do processo
    processo = db.get_processo_by_id(selected_id)
    
    if not processo:
        st.error("❌ Processo não encontrado!")
        return
    
    # Parse dos dados
    try:
        dados_formulario = json.loads(processo['dados_formulario'])
        riscos = json.loads(processo.get('riscos_json', '[]'))
        estrategias = json.loads(processo.get('estrategias_json', '[]'))
    except:
        st.error("❌ Erro ao carregar dados do processo")
        return
    
    # Tabs para organizar resultados
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📄 POP Gerado", "📊 Fluxograma", "⚠️ Análise de Riscos", 
        "🛡️ Estratégias", "📋 Resumo Executivo"
    ])
    
    # Tab 1: POP
    with tab1:
        st.subheader(f"📄 POP: {processo['nome']}")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("**Procedimento Operacional Padrão Gerado:**")
        
        with col2:
            if st.button("📥 Download PDF"):
                st.download_button(
                    label="📄 Baixar POP",
                    data=processo.get('pop_gerado', 'POP não disponível'),
                    file_name=f"POP_{processo['nome'].replace(' ', '_')}.txt",
                    mime="text/plain"
                )
        
        # Exibe POP
        if processo.get('pop_gerado'):
            st.text_area(
                "Conteúdo do POP:",
                value=processo['pop_gerado'],
                height=400,
                disabled=True
            )
        else:
            st.warning("⚠️ POP não foi gerado para este processo")
    
    # Tab 2: Fluxograma
    with tab2:
        st.subheader("📊 Fluxograma do Processo")
        
        if processo.get('mermaid_code'):
            st.markdown("**Fluxograma Visual:**")
            st.code(processo['mermaid_code'], language='mermaid')
            
            # Botão para copiar código
            if st.button("📋 Copiar Código Mermaid"):
                st.code(processo['mermaid_code'])
        else:
            st.warning("⚠️ Fluxograma não disponível")
    
    # Tab 3: Riscos
    with tab3:
        st.subheader("⚠️ Análise de Riscos Identificados")
        
        if riscos:
            # Métricas de riscos
            col1, col2, col3, col4 = st.columns(4)
            
            riscos_alto = len([r for r in riscos if r.get('nivel', '').lower() == 'alto'])
            riscos_medio = len([r for r in riscos if r.get('nivel', '').lower() == 'médio'])
            riscos_baixo = len([r for r in riscos if r.get('nivel', '').lower() == 'baixo'])
            
            with col1:
                st.metric("Total de Riscos", len(riscos))
            with col2:
                st.metric("🔴 Alto", riscos_alto)
            with col3:
                st.metric("🟡 Médio", riscos_medio)
            with col4:
                st.metric("🟢 Baixo", riscos_baixo)
            
            st.markdown("---")
            
            # Lista de riscos
            for i, risco in enumerate(riscos):
                nivel = risco.get('nivel', 'Médio').lower()
                css_class = f"risk-{nivel}" if nivel in ['high', 'medium', 'low'] else "risk-medium"
                
                # Determina cor do ícone
                if nivel == 'alto' or nivel == 'high':
                    icon = "🔴"
                    css_class = "risk-high"
                elif nivel == 'baixo' or nivel == 'low':
                    icon = "🟢"
                    css_class = "risk-low"
                else:
                    icon = "🟡"
                    css_class = "risk-medium"
                
                st.markdown(f"""
                <div class="{css_class}">
                    <h4>{icon} {risco.get('categoria', 'N/A')} - {risco.get('etapa', 'N/A')}</h4>
                    <p><strong>Descrição:</strong> {risco.get('descricao', 'N/A')}</p>
                    <p><strong>Probabilidade:</strong> {risco.get('probabilidade', 'N/A')}/5 | 
                       <strong>Impacto:</strong> {risco.get('impacto', 'N/A')}/5 | 
                       <strong>Nível:</strong> {risco.get('nivel', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("ℹ️ Nenhum risco identificado ou análise não realizada")
    
    # Tab 4: Estratégias
    with tab4:
        st.subheader("🛡️ Estratégias de Mitigação")
        
        if estrategias:
            for i, estrategia in enumerate(estrategias):
                with st.expander(f"🎯 Estratégia {i+1}: {estrategia.get('risco_id', 'N/A')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Estratégia Recomendada:** {estrategia.get('estrategia_recomendada', 'N/A')}")
                        st.write(f"**Responsável Sugerido:** {estrategia.get('responsavel_sugerido', 'N/A')}")
                    
                    with col2:
                        st.write(f"**Prazo:** {estrategia.get('prazo', 'N/A')}")
                        st.write(f"**Custo Estimado:** {estrategia.get('custo_estimado', 'N/A')}")
                    
                    st.write("**Ações Propostas:**")
                    acoes = estrategia.get('acoes', [])
                    for acao in acoes:
                        st.write(f"• {acao}")
        else:
            st.info("ℹ️ Estratégias não disponíveis")
    
    # Tab 5: Resumo Executivo
    with tab5:
        st.subheader("📋 Resumo Executivo")
        
        # Informações básicas
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Informações Básicas")
            st.write(f"**Nome:** {processo['nome']}")
            st.write(f"**Departamento:** {processo['departamento']}")
            st.write(f"**Responsável:** {processo['responsavel']}")
            st.write(f"**Status:** {processo['status'].title()}")
            
        with col2:
            st.markdown("### 📈 Estatísticas")
            etapas_count = len(dados_formulario.get('etapas', []))
            st.write(f"**Etapas Mapeadas:** {etapas_count}")
            st.write(f"**Riscos Identificados:** {len(riscos)}")
            st.write(f"**Estratégias Propostas:** {len(estrategias)}")
            st.write(f"**Data de Criação:** {processo['created_at']}")
        
        st.markdown("---")
        
        # Próximos passos
        st.markdown("### 🎯 Próximos Passos Recomendados")
        
        if riscos_alto > 0:
            st.error(f"🔴 **URGENTE:** {riscos_alto} riscos críticos identificados - Ação imediata necessária")
        
        if riscos_medio > 0:
            st.warning(f"🟡 **ATENÇÃO:** {riscos_medio} riscos médios - Planejar mitigação")
        
        st.info("💡 **Sugestões:**")
        st.write("1. Revisar e validar o POP gerado")
        st.write("2. Implementar controles para riscos críticos")
        st.write("3. Estabelecer cronograma de revisão periódica")
        st.write("4. Treinar equipe nos novos procedimentos")
        
        # Ações
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✏️ Editar Processo"):
                st.info("🔄 Funcionalidade de edição em desenvolvimento")
        
        with col2:
            if st.button("📤 Exportar Relatório"):
                # Gera relatório completo
                relatorio = f"""
RELATÓRIO EXECUTIVO - MAPEAMENTO DE PROCESSO
=============================================

Processo: {processo['nome']}
Departamento: {processo['departamento']}
Data: {processo['created_at']}

RESUMO:
- Etapas mapeadas: {etapas_count}
- Riscos identificados: {len(riscos)}
- Estratégias propostas: {len(estrategias)}

POP GERADO:
{processo.get('pop_gerado', 'Não disponível')}

RISCOS PRINCIPAIS:
{chr(10).join([f"- {r.get('categoria', 'N/A')}: {r.get('descricao', 'N/A')}" for r in riscos[:5]])}

ESTRATÉGIAS:
{chr(10).join([f"- {e.get('estrategia_recomendada', 'N/A')}" for e in estrategias[:5]])}
"""
                
                st.download_button(
                    label="📄 Download Relatório",
                    data=relatorio,
                    file_name=f"Relatorio_{processo['nome'].replace(' ', '_')}.txt",
                    mime="text/plain"
                )
        
        with col3:
            if st.button("🆕 Novo Processo"):
                st.session_state.navigation = "📝 Novo Mapeamento"
                if 'form_data' in st.session_state:
                    del st.session_state.form_data
                st.session_state.form_step = 1
                st.rerun()

def show_library(db):
    """Mostra a biblioteca de processos"""
    
    st.title("📋 Biblioteca de Processos")
    st.markdown("Gerencie todos os processos mapeados da organização")
    
    try:
        processos_df = db.get_processos()
        
        if len(processos_df) == 0:
            st.info("📝 Nenhum processo na biblioteca ainda.")
            if st.button("🚀 Mapear Primeiro Processo"):
                st.session_state.navigation = "📝 Novo Mapeamento"
                st.rerun()
            return
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filtro_status = st.selectbox(
                "Filtrar por Status",
                options=["Todos"] + list(processos_df['status'].unique())
            )
        
        with col2:
            filtro_dept = st.selectbox(
                "Filtrar por Departamento",
                options=["Todos"] + list(processos_df['departamento'].dropna().unique())
            )
        
        with col3:
            busca = st.text_input(
                "🔍 Buscar por nome",
                placeholder="Digite para buscar..."
            )
        
        # Aplicar filtros
        df_filtrado = processos_df.copy()
        
        if filtro_status != "Todos":
            df_filtrado = df_filtrado[df_filtrado['status'] == filtro_status]
        
        if filtro_dept != "Todos":
            df_filtrado = df_filtrado[df_filtrado['departamento'] == filtro_dept]
        
        if busca:
            df_filtrado = df_filtrado[df_filtrado['nome'].str.contains(busca, case=False, na=False)]
        
        st.markdown("---")
        
        # Métricas da biblioteca
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total", len(processos_df))
        with col2:
            st.metric("Rascunhos", len(processos_df[processos_df['status'] == 'rascunho']))
        with col3:
            st.metric("Finalizados", len(processos_df[processos_df['status'] == 'finalizado']))
        with col4:
            st.metric("Filtrados", len(df_filtrado))
        
        st.markdown("---")
        
        # Lista de processos
        if len(df_filtrado) > 0:
            for _, processo in df_filtrado.iterrows():
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{processo['nome']}**")
                        st.caption(f"📅 Criado em: {processo['created_at']}")
                    
                    with col2:
                        st.write(f"🏢 {processo['departamento']}")
                        st.caption(f"👤 {processo['responsavel']}")
                    
                    with col3:
                        status_color = "🟡" if processo['status'] == 'rascunho' else "🟢"
                        st.write(f"{status_color} {processo['status'].title()}")
                        st.caption(f"📝 Atualizado: {processo['updated_at']}")
                    
                    with col4:
                        if st.button("👁️", key=f"view_lib_{processo['id']}", help="Visualizar"):
                            st.session_state.selected_processo_id = processo['id']
                            st.session_state.navigation = "📊 Resultados"
                            st.rerun()
                    
                    with col5:
                        if st.button("🗑️", key=f"delete_{processo['id']}", help="Excluir"):
                            # Aqui você implementaria a exclusão
                            st.warning("⚠️ Funcionalidade de exclusão em desenvolvimento")
                    
                    st.markdown("---")
        else:
            st.info("🔍 Nenhum processo encontrado com os filtros aplicados.")
            
    except Exception as e:
        st.error(f"Erro ao carregar biblioteca: {str(e)}")

# =====================================
# EXECUÇÃO PRINCIPAL
# =====================================

if __name__ == "__main__":
    main()
