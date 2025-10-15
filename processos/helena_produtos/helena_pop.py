# ⚡ OTIMIZAÇÃO MEMÓRIA: LangChain imports movidos para lazy loading
# Os imports pesados agora ocorrem apenas quando HelenaPOP é instanciada
import os
import json
import re
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd

# Import absoluto correto - SEM PONTO
from processos.utils_gerais import BaseLegalSuggestor

# ============================================================================
# CLASSE ARQUITETURA DECIPEX
# ============================================================================

class ArquiteturaDecipex:
    """Carrega e consulta arquitetura de processos da DECIPEX"""
    
    def __init__(self, caminho_csv='documentos_teste/Arquitetura_DECIPEX_mapeada.csv'):
        try:
            self.df = pd.read_csv(caminho_csv)
        except FileNotFoundError:
            print(f"[WARN] Arquivo CSV não encontrado: {caminho_csv}")
            self.df = pd.DataFrame(columns=['Macroprocesso', 'Processo', 'Subprocesso', 'Atividade'])
        except Exception as e:
            print(f"[ERROR] Erro ao carregar CSV: {e}")
            self.df = pd.DataFrame(columns=['Macroprocesso', 'Processo', 'Subprocesso', 'Atividade'])

    def obter_macroprocessos_unicos(self):
        return self.df['Macroprocesso'].unique().tolist()

    def obter_processos_por_macro(self, macro):
        return self.df[self.df['Macroprocesso'] == macro]['Processo'].unique().tolist()

    def obter_subprocessos_por_processo(self, macro, processo):
        filtro = (self.df['Macroprocesso'] == macro) & (self.df['Processo'] == processo)
        return self.df[filtro]['Subprocesso'].unique().tolist()

    def obter_atividades_por_subprocesso(self, macro, processo, subprocesso):
        filtro = (
            (self.df['Macroprocesso'] == macro) &
            (self.df['Processo'] == processo) &
            (self.df['Subprocesso'] == subprocesso)
        )
        return self.df[filtro]['Atividade'].unique().tolist()


# ============================================================================
# CLASSE HELENA POP
# ============================================================================

class HelenaPOP:
    """Helena para mapeamento de POPs - versão completa integrada à DECIPEX"""
    
    def __init__(self):
        # ⚡ OTIMIZAÇÃO MEMÓRIA: Lazy loading de LangChain
        # LangChain só é importado se RAG for habilitado (atualmente desabilitado)
        # from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        # from langchain_chroma import Chroma
        # from langchain.prompts import ChatPromptTemplate

        # LLM e RAG desabilitados para melhor performance
        self.vectorstore = None
        
        # Estados da conversa - NOVO FLUXO: nome -> confirma_nome -> pre_explicacao -> explicacao -> area -> ...
        self.estado = "nome"
        self.dados = {}
        self.nome_usuario = ""
        self.nome_temporario = ""  # NOVO: guardar nome antes de confirmar
        self.editando_campo = None  # NOVO: guardar qual campo está sendo editado
        self.area_selecionada = None
        self.macro_selecionado = None
        self.processo_selecionado = None
        self.subprocesso_selecionado = None
        self.atividade_selecionada = None
        self.sistemas_selecionados = []
        self.documentos_processo = []
        self.aguardando_tipo_documento = False  # NOVO: controlar quando aguarda tipo do documento
        self.documento_temporario = ""  # NOVO: guardar documento antes de classificar
        self.etapas_processo = []
        self.detalhes_etapa_atual = []
        self.aguardando_detalhes = False
        self.aguardando_operadores_etapa = False  # NOVO: controlar quando aguarda operadores da etapa
        self.operadores_etapa_atual = []  # NOVO: guardar operadores da etapa atual
        self.aguardando_condicionais = False  # NOVO: controlar quando aguarda condicionais da etapa
        self.aguardando_pergunta_condicionais = False  # NOVO: pergunta se tem condicionais
        self.etapa_tem_condicionais = False  # NOVO: flag se etapa atual tem condicionais
        self.aguardando_tipo_condicional = False  # NOVO: aguarda tipo (binário ou múltiplos)
        self.tipo_condicional = None  # NOVO: 'binario' ou 'multiplos'
        self.aguardando_antes_decisao = False  # NOVO: pergunta o que fazer antes da decisão
        self.antes_decisao = None  # NOVO: texto do que fazer antes da decisão
        self.aguardando_cenarios = False  # NOVO: aguarda definição dos cenários
        self.cenarios_condicionais = []  # NOVO: lista de cenários condicionais
        self.aguardando_subetapas_cenario = False  # NOVO: aguarda subetapas de um cenário específico
        self.cenario_atual_detalhando = None  # NOVO: qual cenário está sendo detalhado (índice)
        self.cenarios_coletados = []  # NOVO: cenários já descritos, aguardando detalhamento
        self.etapa_temporaria = None  # Já existe mas garantindo
        self.modo_tempo_real = False  # NOVO: controlar visualização em tempo real
        self.fluxos_entrada = []
        self.fluxos_saida = []
        self.etapa_atual_campo = 0
        self.conversas = []
        
        # Carregar dados da arquitetura
        self.arquitetura = ArquiteturaDecipex()
        
        # Modo híbrido: além do dropdown no frontend, também mostrar lista numerada no texto
        self.modo_lista_arquitetura_hibrido = True
        
        # Integração base legal
        self.suggestor_base_legal = BaseLegalSuggestor()
        
        # Campos principais a coletar
        self.campos_principais = [
            {
                "nome": "nome_processo",
                "pergunta": "Qual é o nome completo da atividade que você quer mapear?",
                "exemplo": "Ex: Conceder ressarcimento a aposentado civil, Análise de requerimento de auxílio alimentação"
            },
            {
                "nome": "processo_especifico", 
                "pergunta": "A que processo específico esta atividade pertence?",
                "exemplo": "Ex: Gestão de Benefícios de Assistência à Saúde, Gestão de Auxílios Alimentação"
            },
            {
                "nome": "entrega_esperada",
                "pergunta": "Qual é o resultado final desta atividade?",
                "exemplo": "Ex: Auxílio concedido, Requerimento analisado e decidido, Cadastro atualizado"
            },
            {
                "nome": "dispositivos_normativos",
                "pergunta": "Quais são as principais normas que regulam esta atividade?",
                "exemplo": "Ex: Art. 34 da IN SGP/SEDGG/ME nº 97/2022, Lei 8.112/90"
            },
            {
                "nome": "pontos_atencao",
                "pergunta": "⚠️ Há algum ponto especial de atenção ou cuidado nesta atividade?\n\nAlgo que você sempre lembra: \"Ao fazer isso, é importante ter atenção a...\"",
                "exemplo": "Ex: Auditar situação desde centralização, Observar prazos de retroatividade"
            },
            {
                "nome": "operadores",
                "pergunta": "Quem são os responsáveis por executar esta atividade?",
                "exemplo": "Ex: Técnico Especializado, Coordenador, Apoio-gabinete"
            }
        ]

    @property
    def AREAS_DECIPEX(self):
        return {
            1: {"codigo": "CGBEN", "nome": "Coordenação Geral de Benefícios", "prefixo": "1"},
            2: {"codigo": "CGPAG", "nome": "Coordenação Geral de Pagamentos", "prefixo": "2"},
            3: {"codigo": "COATE", "nome": "Coordenação de Atendimento", "prefixo": "3"},
            4: {"codigo": "CGGAF", "nome": "Coordenação Geral de Gestão de Acervos Funcionais", "prefixo": "4"},
            5: {"codigo": "DIGEP", "nome": "Diretoria de Pessoal dos Ex-Territórios", "prefixo": "5"},
            6: {"codigo": "CGRIS", "nome": "Coordenação Geral de Riscos e Controle", "prefixo": "6"},
            7: {"codigo": "CGCAF", "nome": "Coordenação Geral de Gestão de Complementação da Folha", "prefixo": "7"},
            8: {"codigo": "CGECO", "nome": "Coordenação Geral de Extinção e Convênio", "prefixo": "8"}
        }

    @property
    def SISTEMAS_DECIPEX(self):
        return {
            "gestao_pessoal": ["SIAPE", "E-SIAPE", "SIGEPE", "SIGEP - AFD", "E-Pessoal TCU", "SIAPNET", "SIGAC"],
            "documentos": ["SEI", "DOINET", "DOU", "SOUGOV", "PETRVS"],
            "transparencia": ["Portal da Transparência", "CNIS", "Site CGU-PAD", "Sistema de Pesquisa Integrada do TCU", "Consulta CPF RFB"],
            "previdencia": ["SISTEMA COMPREV", "BG COMPREV"],
            "comunicacao": ["TEAMS", "OUTLOOK"],
            "outros": ["DW"]
        }

    @property
    def OPERADORES_DECIPEX(self):
        return [
            "Técnico Especializado",
            "Coordenador de Auxílios", 
            "Coordenador",
            "Apoio-gabinete",
            "Equipe técnica",
            "Outros (especificar)"
        ]

    def processar_mensagem(self, mensagem):
        """Processa mensagem do usuário de acordo com o estado atual"""
        try:
            print(f"\n[DEBUG-PRINCIPAL] processar_mensagem chamada")
            print(f"[DEBUG-PRINCIPAL] Estado: {self.estado}")
            print(f"[DEBUG-PRINCIPAL] aguardando_operadores_etapa = {self.aguardando_operadores_etapa}")
            print(f"[DEBUG-PRINCIPAL] Mensagem: '{mensagem[:100]}'")

            self.conversas.append({
                "usuario": mensagem,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            # Comando especial para preenchimento automático da arquitetura completa (Helena Ajuda Inteligente)
            try:
                comando_json = json.loads(mensagem)
                if isinstance(comando_json, dict) and comando_json.get('acao') == 'preencher_arquitetura_completa':
                    sugestao = comando_json.get('sugestao', {})
                    return self._preencher_arquitetura_completa(sugestao)
            except (json.JSONDecodeError, ValueError):
                pass  # Não é um comando JSON, continuar processamento normal

            # Comando especial para ativar modo tempo real
            if mensagem.lower().strip() in ["tempo real", "visualização tempo real", "modo tempo real", "ativar tempo real"]:
                self.modo_tempo_real = True
                return {
                    "resposta": "🚀 Modo tempo real ativado! A partir de agora você verá as etapas sendo construídas em tempo real.",
                    "tipo_interface": "etapas_tempo_real",
                    "dados_interface": {
                        "etapas": getattr(self, 'etapas_processo', []),
                        "etapa_atual": {
                            "numero": len(getattr(self, 'etapas_processo', [])) + 1 if hasattr(self, 'etapa_temporaria') and self.etapa_temporaria else None,
                            "descricao": getattr(self, 'etapa_temporaria', None),
                            "detalhes": getattr(self, 'detalhes_etapa_atual', []),
                            "operador": getattr(self, 'operadores_etapa_atual', [None])[0] if getattr(self, 'operadores_etapa_atual', []) else None
                        },
                        "estado": self._obter_estado_atual()
                    },
                    "dados_extraidos": {},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "etapas"
                }
                
            # Comando para minimizar tempo real
            if mensagem.lower().strip() == "minimizar_tempo_real":
                self.modo_tempo_real = False
                return {
                    "resposta": "Visualização em tempo real minimizada. Digite 'tempo real' para reativar.",
                    "tipo_interface": "texto",
                    "dados_interface": {},
                    "dados_extraidos": {},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "etapas"
                }
            
            if self.estado == "nome":
                return self._processar_nome(mensagem)
            elif self.estado == "confirma_nome":
                return self._processar_confirma_nome(mensagem)
            elif self.estado == "pre_explicacao":
                return self._processar_pre_explicacao(mensagem)
            elif self.estado == "explicacao":
                return self._processar_explicacao(mensagem)
            elif self.estado == "explicacao_final":
                return self._processar_explicacao_final(mensagem)
            elif self.estado == "selecionar_edicao":
                return self._processar_selecionar_edicao(mensagem)
            elif self.estado == "area":
                return self._processar_area(mensagem)
            elif self.estado == "arquitetura":
                return self._processar_arquitetura(mensagem)
            elif self.estado == "sistemas":
                return self._processar_sistemas(mensagem)
            elif self.estado == "campos":
                return self._processar_campos(mensagem)
            elif self.estado == "documentos":
                return self._processar_documentos(mensagem)
            elif self.estado == "pre_etapas":
                return self._processar_pre_etapas(mensagem)
            elif self.estado == "fluxos_entrada":
                return self._processar_fluxos_entrada(mensagem)
            elif self.estado == "etapas":
                return self._processar_etapas(mensagem)
            elif self.estado == "fluxos_saida":
                return self._processar_fluxos_saida(mensagem)
            elif self.estado == "fluxos":
                return self._processar_fluxos(mensagem)
            elif self.estado == "revisao":
                return self._processar_revisao(mensagem)
            else:
                return self._erro_estado()
                
        except Exception as e:
            print(f"Erro: {e}")
            return {
                "resposta": "Desculpe, ocorreu um erro. Pode repetir sua resposta?",
                "tipo_interface": "texto",
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": self._calcular_progresso(),
                "proximo_estado": self.estado
            }

    # =========================================================================
    # HELPERS INTERNOS
    # =========================================================================
    def _formatar_lista_numerada(self, opcoes):
        """Retorna string enumerada 1) Opção"""
        return "\n".join(f"{i+1}) {op}" for i, op in enumerate(opcoes))

    def _processar_nome(self, mensagem):
        """Captura nome inicial do usuário"""
        msg_limpa = mensagem.strip()
        
        # Heurística: só considerar que o usuário já forneceu o nome se
        # 1) For uma única palavra (sem espaços)
        # 2) Tiver ao menos 2 caracteres alfabéticos
        # 3) Não for uma saudação comum
        # 4) Não tiver pontuação típica de frase
        saudacoes = {"ola", "olá", "oi", "bom", "boa", "hey", "eai", "eae"}
        # Palavras que são respostas de confirmação e NÃO devem virar nome após uma negativa
        confirmacoes = {"sim", "s", "nao", "não", "n", "yes", "no"}
        palavras = msg_limpa.split()
        apenas_uma_palavra = len(palavras) == 1
        palavra = palavras[0] if palavras else ""
        eh_saudacao = palavra.lower() in saudacoes
        tem_pontuacao_frase = bool(re.search(r"[!?.,]", msg_limpa)) or len(palavras) > 1
        eh_nome_candidato = (
            apenas_uma_palavra and
            len(palavra) >= 2 and
            palavra.isalpha() and
            not eh_saudacao and
            not tem_pontuacao_frase and
            palavra.lower() not in confirmacoes
        )

        if eh_nome_candidato:
            self.nome_temporario = palavra.capitalize()
            self.estado = "confirma_nome"
            return {
                "resposta": f"Olá, {self.nome_temporario}! Prazer em te conhecer. Fico feliz que você tenha aceitado essa missão de documentar nossos processos. Antes de continuarmos, me confirma, posso te chamar de {self.nome_temporario} mesmo? (Digite SIM ou NÃO)",
                "tipo_interface": "texto",
                "dados_interface": {},
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": "0/10",
                "proximo_estado": "confirma_nome"
            }

        # Caso contrário, ainda estamos pedindo o nome
        return {
            "resposta": "👋 Olá! Sou a Helena, assistente de IA da DECIPEX especializada em mapeamento de processos.\n\nVou te ajudar a documentar seu procedimento de forma clara e estruturada, pergunta por pergunta.\n\nPara começarmos, qual seu nome?",
            "tipo_interface": "texto",
            "avatar_helena": "/static/img/helena_mapeamento.png",  # Caminho para o frontend
            "dados_interface": {},
            "dados_extraidos": {},
            "conversa_completa": False,
            "progresso": "0/10",
            "proximo_estado": "nome"
        }

    def _processar_confirma_nome(self, mensagem):
        """Confirma se o nome capturado está correto - aceita apenas SIM ou NÃO"""
        resposta_original = mensagem.strip()
        resposta_lower = resposta_original.lower()

        # Normalização simples removendo acentos para comparação
        import unicodedata
        def normalizar(txt):
            return ''.join(c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn')
        resposta_norm = normalizar(resposta_lower)

        # Lista de respostas positivas (SIM)
        respostas_positivas = {"sim", "s", "yes", "uhum", "aham", "isso"}

        # Lista de respostas negativas (NÃO)
        respostas_negativas = {"nao", "no", "n" "jamais"}

        # Evitar que palavras de confirmação sejam tratadas como nome
        palavras_reservadas = respostas_positivas | respostas_negativas | {"não"}

        # Se a resposta for positiva, mantém o nome anterior
        if resposta_norm in respostas_positivas:
            # Apenas confirma, não altera o nome
            self.nome_usuario = self.nome_temporario
            self.estado = "pre_explicacao"
            return {
                "resposta": f"Ótimo então {self.nome_usuario}, antes de seguir preciso explicar algumas coisas ok?",
                "tipo_interface": "texto",
                "dados_interface": {},
                "dados_extraidos": {"nome_usuario": self.nome_usuario},
                "conversa_completa": False,
                "progresso": "1/10",
                "proximo_estado": "pre_explicacao"
            }

        # Se a resposta for negativa, pede novo nome
        elif resposta_norm in respostas_negativas:
            self.nome_temporario = ""
            self.estado = "nome"
            return {
                "resposta": "Ah sim, erros acontecem, vamos recomeçar. Como você gostaria de ser chamado? (Digite apenas o primeiro nome)",
                "tipo_interface": "texto",
                "dados_interface": {},
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": "0/10",
                "proximo_estado": "nome"
            }

        # Se a resposta não for sim/não, assume que o usuário digitou um novo nome
        elif len(resposta_norm) >= 2 and resposta_norm not in palavras_reservadas:
            self.nome_temporario = resposta_norm.split()[0].capitalize()
            self.estado = "confirma_nome"
            return {
                "resposta": f"Entendi, você prefere ser chamado de {self.nome_temporario}? (Digite SIM ou NÃO)",
                "tipo_interface": "texto",
                "dados_interface": {},
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": "0/10",
                "proximo_estado": "confirma_nome"
            }

        # Caso não entenda, pede confirmação novamente
        else:
            return {
                "resposta": f"Não entendi. Digite SIM se posso te chamar de {self.nome_temporario}, ou NÃO se prefere outro nome.",
                "tipo_interface": "texto",
                "dados_interface": {},
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": "0/10",
                "proximo_estado": "confirma_nome"
            }

    def _processar_pre_explicacao(self, mensagem):
        """Aguarda confirmação antes de explicar o processo"""
        resposta_lower = mensagem.lower().strip()
        
        respostas_positivas = [
            "sim", "s", "ok", "pode", "claro", "vamos", "yes", 
            "uhum", "aham", "beleza", "tudo bem", "sigo"
        ]
        
        # Garantir que sempre tem um nome para exibir
        nome_exibir = self.nome_usuario or self.nome_temporario or "você"
        
        if resposta_lower in respostas_positivas:
            self.estado = "explicacao"
            return {
                "resposta": f"Nesse chat eu vou conduzir uma conversa guiada. A intenção é preencher esse formulário de Procedimento Operacional Padrão - POP aí do lado. Tá vendo? Aproveita pra conhecer.\n\nNossa meta é entregar esse POP prontinho. Vamos continuar? (digite sim que seguimos em frente)",
                "tipo_interface": "texto",
                "dados_interface": {},
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": "1/10",
                "proximo_estado": "explicacao"
            }
        else:
            return {
                "resposta": "Sem problemas! Quando você estiver pronto pra ouvir, é só me dizer 'ok' ou 'pode'.",
                "tipo_interface": "texto",
                "dados_interface": {},
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": "1/10",
                "proximo_estado": "pre_explicacao"
            }

    def _processar_explicacao(self, mensagem):
        """Confirma que está tudo claro e pronto para começar"""
        resposta_lower = mensagem.lower().strip()
        
        respostas_positivas = [
            "sim", "s", "pode", "ok", "claro", "vamos", "yes", 
            "uhum", "aham", "beleza", "entendi", "bora", "vamo", "pronta", "pronto"
        ]
        
        # Garantir que sempre tem um nome para exibir
        nome_exibir = self.nome_usuario or self.nome_temporario or "você"
        
        if resposta_lower in respostas_positivas:
            self.estado = "explicacao_final"

            return {
                "resposta": f"Mas {nome_exibir}, se ao olhar o formulário você ficou com dúvida em algum campo, quero te tranquilizar! Essa missão é em dupla e você pode sempre acionar o botão 'Preciso de Ajuda' que eu entro em ação!\n\nDigite sim pra gente continuar.",
                "tipo_interface": "texto",
                "dados_interface": {},
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": "1/10",
                "proximo_estado": "explicacao_final"
            }
        else:
            return {
                "resposta": f"Tudo bem! Só posso seguir quando você me disser 'sim', {nome_exibir}. Quando quiser continuar, é só digitar.",
                "tipo_interface": "texto",
                "dados_interface": {},
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": "1/10",
                "proximo_estado": "explicacao"
            }

    def _processar_selecionar_edicao(self, mensagem):
        """Processa seleção de campo para edição"""
        try:
            campo_num = int(mensagem.strip())
            
            # Mapeamento de número para campo e ação
            if campo_num == 1:
                # Editar área
                self.editando_campo = "area"
                self.estado = "area"
                return {
                    "resposta": f"Vamos alterar sua área. Selecione a nova área:",
                    "tipo_interface": "areas",
                    "dados_interface": {
                        "opcoes_areas": self.AREAS_DECIPEX,
                        "titulo": "Selecione sua área na DECIPEX"
                    },
                    "dados_extraidos": {},
                    "conversa_completa": False,
                    "progresso": "10/10",
                    "proximo_estado": "area"
                }
            
            elif campo_num == 2:
                # Editar arquitetura
                self.editando_campo = "arquitetura"
                self.macro_selecionado = None
                self.processo_selecionado = None
                self.subprocesso_selecionado = None
                self.atividade_selecionada = None
                self.estado = "arquitetura"
                return {
                    "resposta": f"Vamos reposicionar seu processo na arquitetura. Qual o macroprocesso?",
                    "tipo_interface": "dropdown_macro",
                    "dados_interface": {
                        "opcoes": self.arquitetura.obter_macroprocessos_unicos(),
                        "titulo": "Selecione o Macroprocesso"
                    },
                    "dados_extraidos": {},
                    "conversa_completa": False,
                    "progresso": "10/10",
                    "proximo_estado": "arquitetura"
                }
            
            elif campo_num == 3:
                # Editar sistemas
                self.editando_campo = "sistemas"
                self.estado = "sistemas"
                sistemas_atuais = ", ".join(self.sistemas_selecionados) if self.sistemas_selecionados else "Nenhum"
                return {
                    "resposta": f"Sistemas atuais: {sistemas_atuais}\n\nQuais sistemas você utiliza? (Digite os novos sistemas)",
                    "tipo_interface": "sistemas",
                    "dados_interface": {
                        "sistemas_por_categoria": self.SISTEMAS_DECIPEX,
                        "permite_outros": True
                    },
                    "dados_extraidos": {},
                    "conversa_completa": False,
                    "progresso": "10/10",
                    "proximo_estado": "sistemas"
                }
            
            elif campo_num == 4:
                # Editar entrega esperada
                self.editando_campo = "entrega_esperada"
                self.etapa_atual_campo = 2  # índice do campo entrega_esperada
                self.estado = "campos"
                valor_atual = self.dados.get("entrega_esperada", "")
                return {
                    "resposta": f"Valor atual: {valor_atual}\n\nQual é o resultado final desta atividade?",
                    "tipo_interface": "texto",
                    "dados_interface": {},
                    "dados_extraidos": {},
                    "conversa_completa": False,
                    "progresso": "10/10",
                    "proximo_estado": "campos"
                }
            
            elif campo_num == 5:
                # Editar dispositivos normativos
                self.editando_campo = "dispositivos_normativos"
                self.etapa_atual_campo = 3
                self.estado = "campos"
                valor_atual = self.dados.get("dispositivos_normativos", "")
                return {
                    "resposta": f"Valor atual: {valor_atual}\n\nQuais são as principais normas que regulam esta atividade?",
                    "tipo_interface": "texto",
                    "dados_interface": {},
                    "dados_extraidos": {},
                    "conversa_completa": False,
                    "progresso": "10/10",
                    "proximo_estado": "campos"
                }
            
            elif campo_num == 6:
                # Editar pontos de atenção
                self.editando_campo = "pontos_atencao"
                self.etapa_atual_campo = 4
                self.estado = "campos"
                valor_atual = self.dados.get("pontos_atencao", "")
                return {
                    "resposta": f"Valor atual: {valor_atual}\n\n⚠️ Há algum ponto especial de atenção ou cuidado nesta atividade?\n\nAlgo que você sempre lembra: \"Ao fazer isso, é importante ter atenção a...\"\n\nEx: Auditar situação desde centralização, Observar prazos de retroatividade",
                    "tipo_interface": "texto",
                    "dados_interface": {},
                    "dados_extraidos": {},
                    "conversa_completa": False,
                    "progresso": "10/10",
                    "proximo_estado": "campos"
                }

            elif campo_num == 7:
                # Editar operadores
                self.editando_campo = "operadores"
                self.etapa_atual_campo = 5
                self.estado = "campos"
                valor_atual = self.dados.get("operadores", "")
                return {
                    "resposta": f"Valor atual: {valor_atual}\n\nQuem são os responsáveis por executar esta atividade?",
                    "tipo_interface": "operadores",
                    "dados_interface": {
                        "opcoes": self.OPERADORES_DECIPEX
                    },
                    "dados_extraidos": {},
                    "conversa_completa": False,
                    "progresso": "10/10",
                    "proximo_estado": "campos"
                }
            
            elif campo_num == 8:
                # Editar documentos
                self.editando_campo = "documentos_utilizados"
                self.documentos_processo = []
                self.estado = "documentos"
                return {
                    "resposta": f"Vamos redefinir os documentos:",
                    "tipo_interface": "documentos",
                    "dados_interface": {},
                    "dados_extraidos": {},
                    "conversa_completa": False,
                    "progresso": "10/10",
                    "proximo_estado": "documentos"
                }
            
            elif campo_num == 9:
                # Editar etapas
                self.editando_campo = "etapas"
                self.etapas_processo = []
                self.aguardando_detalhes = False
                self.aguardando_operadores_etapa = False
                self.operadores_etapa_atual = []
                self.estado = "etapas"
                return {
                    "resposta": f"Vamos redefinir as etapas. Descreva a primeira etapa:",
                    "tipo_interface": "texto",
                    "dados_interface": {},
                    "dados_extraidos": {},
                    "conversa_completa": False,
                    "progresso": "10/10",
                    "proximo_estado": "etapas"
                }
            
            elif campo_num == 10:
                # Editar fluxos
                self.editando_campo = "fluxos"
                self.fluxos_entrada = []
                self.fluxos_saida = []
                self.estado = "fluxos"
                return {
                    "resposta": "Vamos redefinir os fluxos. Seu processo recebe insumos de outra área da DECIPEX?",
                    "tipo_interface": "fluxos_entrada",
                    "dados_interface": {
                        "opcoes_areas": {k: v for k, v in self.AREAS_DECIPEX.items() if k != self.area_selecionada},
                        "tipo_fluxo": "entrada",
                        "opcoes_extras": [
                            {"id": "area_interna", "label": "Outra área interna da minha coordenação geral", "campo_livre": True},
                            {"id": "area_externa", "label": "Área externa da DECIPEX", "campo_livre": True},
                            {"id": "outra_decipex", "label": "Outra área da DECIPEX não listada", "campo_livre": True}
                        ]
                    },
                    "dados_extraidos": {},
                    "conversa_completa": False,
                    "progresso": "10/10",
                    "proximo_estado": "fluxos"
                }
            
            else:
                raise ValueError("Número inválido")
                
        except:
            return {
                "resposta": "Por favor, digite um número de 1 a 10 para escolher o campo que deseja editar.",
                "tipo_interface": "texto",
                "dados_interface": {},
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": "10/10",
                "proximo_estado": "selecionar_edicao"
            }

    def _processar_explicacao_final(self, mensagem):
        """Confirmação final antes de começar o mapeamento"""
        resposta_lower = mensagem.lower().strip()
        
        respostas_positivas = [
            "sim", "s", "pode", "ok", "claro", "vamos", "yes", 
            "uhum", "aham", "beleza", "entendi", "bora", "vamo", "pode ser"
        ]
        
        # Garantir que sempre tem um nome para exibir
        nome_exibir = self.nome_usuario or self.nome_temporario or "você"
        
        if resposta_lower in respostas_positivas:
            self.estado = "area"
            
            return {
                "resposta": f"Ótimo, {nome_exibir}! Então vamos começar. Em qual área da DECIPEX você trabalha?",
                "tipo_interface": "areas",
                "dados_interface": {
                    "opcoes_areas": self.AREAS_DECIPEX,
                    "titulo": "Selecione sua área na DECIPEX"
                },
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": self._calcular_progresso(),
                "proximo_estado": "area"
            }
        else:
            return {
                "resposta": f"Tudo bem! Só posso seguir quando você me disser 'sim', {nome_exibir}. Quando estiver pronta, é só me dizer.",
                "tipo_interface": "texto",
                "dados_interface": {},
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": "1/10",
                "proximo_estado": "explicacao_final"
            }

    def _processar_area(self, mensagem):
        """Processa seleção de área"""
        try:
            area_id = int(mensagem.strip())
            if area_id in self.AREAS_DECIPEX:
                self.area_selecionada = area_id
                self.dados["area"] = self.AREAS_DECIPEX[area_id]
                
                # Se está editando, voltar para revisão
                if self.editando_campo == "area":
                    self.editando_campo = None
                    self.estado = "revisao"
                    return {
                        "resposta": f"Área atualizada para {self.AREAS_DECIPEX[area_id]['nome']}! Aqui está o resumo atualizado:",
                        "tipo_interface": "revisao",
                        "dados_interface": {
                            "dados_completos": self._gerar_dados_completos_pop(),
                            "codigo_gerado": self._gerar_codigo_processo()
                        },
                        "dados_extraidos": {
                            "area": self.AREAS_DECIPEX[area_id],
                            "macroprocesso": self.macro_selecionado
                        },
                        "conversa_completa": False,
                        "progresso": "10/10",
                        "proximo_estado": "revisao"
                    }
                
                # Fluxo normal
                self.estado = "arquitetura"
                macros = self.arquitetura.obter_macroprocessos_unicos()

                return {
                    "resposta": (
                        f"Perfeito, {self.nome_usuario}! Você trabalha na {self.AREAS_DECIPEX[area_id]['nome']}.\n\n"
                        f"Agora vamos localizar seu **MACROPROCESSO** na arquitetura da DECIPEX. Essa lista já foi levantada anteriormente.\n\n"
                        f"Macroprocesso é a gestão de um aglomerado de processos e atividades. Veja as opções na lista.\n\n"
                        f"Mas se tiver em dúvida em qual macroprocesso sua atividade se encaixa, é só clicar em \"Preciso de Ajuda\" e me contar em detalhes o que você faz e eu te ajudo a definir."
                    ),
                    "tipo_interface": "dropdown_macro",
                    "dados_interface": {
                        "opcoes": macros,
                        "titulo": "Selecione o Macroprocesso"
                    },
                    "dados_extraidos": {"area": self.AREAS_DECIPEX[area_id]},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "arquitetura"
                }
            else:
                raise ValueError("Área inválida")
        except:
            return {
                "resposta": "Por favor, selecione uma área válida da lista.",
                "tipo_interface": "areas",
                "dados_interface": {"opcoes_areas": self.AREAS_DECIPEX},
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": self._calcular_progresso(),
                "proximo_estado": "area"
            }

    def _processar_arquitetura(self, mensagem):
        """Processa navegação hierárquica na arquitetura"""

        print(f"[ARCH] ARQUITETURA: Mensagem='{mensagem}'")
        print(f"[ARCH] ARQUITETURA: Macro={self.macro_selecionado}")
        print(f"[ARCH] ARQUITETURA: Processo={self.processo_selecionado}")
        print(f"[ARCH] ARQUITETURA: Subprocesso={self.subprocesso_selecionado}")
        
        if not self.macro_selecionado:
            entrada = mensagem.strip()
            macros = self.arquitetura.obter_macroprocessos_unicos()
            if entrada.isdigit():
                idx = int(entrada)
                if 1 <= idx <= len(macros):
                    self.macro_selecionado = macros[idx-1]
                else:
                    lista_txt = self._formatar_lista_numerada(macros)
                    return {
                        "resposta": (
                            "Número inválido. Escolha um macroprocesso:\n" +
                            lista_txt + "\nDigite o número ou nome."),
                        "tipo_interface": "dropdown_macro",
                        "dados_interface": {"opcoes": macros, "titulo": "Selecione o Macroprocesso"},
                        "dados_extraidos": {},
                        "conversa_completa": False,
                        "progresso": self._calcular_progresso(),
                        "proximo_estado": "arquitetura"
                    }
            else:
                if entrada in macros:
                    self.macro_selecionado = entrada
                else:
                    lista_txt = self._formatar_lista_numerada(macros)
                    return {
                        "resposta": (
                            "Não reconheci esse macroprocesso. Opções:\n" +
                            lista_txt + "\nDigite o número ou nome."),
                        "tipo_interface": "dropdown_macro",
                        "dados_interface": {"opcoes": macros, "titulo": "Selecione o Macroprocesso"},
                        "dados_extraidos": {},
                        "conversa_completa": False,
                        "progresso": self._calcular_progresso(),
                        "proximo_estado": "arquitetura"
                    }

            processos = self.arquitetura.obter_processos_por_macro(self.macro_selecionado)
            return {
                "resposta": f"Então seu macroprocesso é **{self.macro_selecionado}**. Entendi!\n\nAgora vamos detalhar em mais 3 níveis para localizar exatamente sua atividade:\n\n📍 **Nível 1: PROCESSO**\n\n📍 **Nível 2: SUBPROCESSO**\n\n📍 **Nível 3: ATIVIDADE**\n\nComeçando pelo PROCESSO, selecione abaixo a opção que melhor se encaixa. Se não achar nada parecido com sua atividade temos o campo em aberto para você digitar.",
                "tipo_interface": "dropdown_processo_com_texto_livre",
                "dados_interface": {"opcoes": processos, "permitir_texto_livre": True},
                "dados_extraidos": {"macroprocesso": self.macro_selecionado},
                "conversa_completa": False,
                "progresso": self._calcular_progresso(),
                "proximo_estado": "arquitetura"
            }
        
        elif not self.processo_selecionado:
            entrada = mensagem.strip()
            processos = self.arquitetura.obter_processos_por_macro(self.macro_selecionado)
            if entrada.isdigit():
                idx = int(entrada)
                if 1 <= idx <= len(processos):
                    self.processo_selecionado = processos[idx-1]
                else:
                    lista_proc = self._formatar_lista_numerada(processos)
                    return {
                        "resposta": "Número inválido. Processos:\n" + lista_proc + "\nDigite número ou nome.",
                        "tipo_interface": "dropdown_processo",
                        "dados_interface": {"opcoes": processos},
                        "dados_extraidos": {},
                        "conversa_completa": False,
                        "progresso": self._calcular_progresso(),
                        "proximo_estado": "arquitetura"
                    }
            else:
                # Aceita qualquer texto: da lista ou customizado
                self.processo_selecionado = entrada

            subprocessos = self.arquitetura.obter_subprocessos_por_processo(
                self.macro_selecionado, self.processo_selecionado
            )

            print(f"[SUB] Subprocessos encontrados: {len(subprocessos)} itens")
            print(f"[SUB] Lista: {subprocessos[:3] if subprocessos else 'VAZIA'}")

            if not subprocessos or len(subprocessos) == 0:
                print("[WARN] Nenhum subprocesso encontrado! Pulando para atividade...")
                self.subprocesso_selecionado = "Não informado"
                atividades = self.arquitetura.obter_atividades_por_subprocesso(
                    self.macro_selecionado, self.processo_selecionado, "Não informado"
                )
                lista_ativ = self._formatar_lista_numerada(atividades) if self.modo_lista_arquitetura_hibrido else ""
                texto_lista = f"\n\nAtividades:\n{lista_ativ}\n\nDigite número ou nome." if lista_ativ else ""
                return {
                    "resposta": f"Processo: {self.processo_selecionado}. Não encontrei subprocessos no CSV. Selecione a atividade:{texto_lista}",
                    "tipo_interface": "dropdown_atividade",
                    "dados_interface": {"opcoes": atividades if atividades else []},
                    "dados_extraidos": {"processo": self.processo_selecionado},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "arquitetura"
                }

            nome_exibir = self.nome_usuario or self.nome_temporario or "você"
            return {
                "resposta": f"Processo: **{self.processo_selecionado}**. Pronto!\n\nAgora vamos mais um degrau: **SUBPROCESSO**.\n\nSelecione abaixo a opção que melhor se encaixa. Se não achar nada parecido com sua atividade temos o campo em aberto para você digitar.",
                "tipo_interface": "dropdown_subprocesso_com_texto_livre",
                "dados_interface": {"opcoes": subprocessos, "permitir_texto_livre": True},
                "dados_extraidos": {"processo": self.processo_selecionado},
                "conversa_completa": False,
                "progresso": self._calcular_progresso(),
                "proximo_estado": "arquitetura"
            }
        
        elif not self.subprocesso_selecionado:
            entrada = mensagem.strip()
            subprocessos = self.arquitetura.obter_subprocessos_por_processo(
                self.macro_selecionado, self.processo_selecionado
            )
            if entrada.isdigit():
                idx = int(entrada)
                if 1 <= idx <= len(subprocessos):
                    self.subprocesso_selecionado = subprocessos[idx-1]
                else:
                    lista_sub = self._formatar_lista_numerada(subprocessos)
                    return {
                        "resposta": "Número inválido. Subprocessos:\n" + lista_sub + "\nDigite número ou nome.",
                        "tipo_interface": "dropdown_subprocesso",
                        "dados_interface": {"opcoes": subprocessos},
                        "dados_extraidos": {},
                        "conversa_completa": False,
                        "progresso": self._calcular_progresso(),
                        "proximo_estado": "arquitetura"
                    }
            else:
                # Aceita qualquer texto: da lista ou customizado
                self.subprocesso_selecionado = entrada
            atividades = self.arquitetura.obter_atividades_por_subprocesso(
                self.macro_selecionado, self.processo_selecionado, self.subprocesso_selecionado
            )
            nome_exibir = self.nome_usuario or self.nome_temporario or "você"
            return {
                "resposta": f"Subprocesso: **{self.subprocesso_selecionado}**. Ótimo!\n\n**Último degrau: ATIVIDADE** (o trabalho específico que você executa).\n\nSelecione abaixo a opção que melhor se encaixa. Se não achar nada parecido com sua atividade temos o campo em aberto para você digitar.",
                "tipo_interface": "dropdown_atividade_com_texto_livre",
                "dados_interface": {"opcoes": atividades, "permitir_texto_livre": True},
                "dados_extraidos": {"subprocesso": self.subprocesso_selecionado},
                "conversa_completa": False,
                "progresso": self._calcular_progresso(),
                "proximo_estado": "arquitetura"
            }
        
        else:
            entrada = mensagem.strip()
            atividades = self.arquitetura.obter_atividades_por_subprocesso(
                self.macro_selecionado, self.processo_selecionado, self.subprocesso_selecionado
            )
            if entrada.isdigit() and atividades:
                idx = int(entrada)
                if 1 <= idx <= len(atividades):
                    self.atividade_selecionada = atividades[idx-1]
                else:
                    lista_ativ = self._formatar_lista_numerada(atividades)
                    return {
                        "resposta": "Número inválido. Atividades:\n" + lista_ativ + "\nDigite número ou nome.",
                        "tipo_interface": "dropdown_atividade",
                        "dados_interface": {"opcoes": atividades},
                        "dados_extraidos": {},
                        "conversa_completa": False,
                        "progresso": self._calcular_progresso(),
                        "proximo_estado": "arquitetura"
                    }
            else:
                if atividades and entrada in atividades:
                    self.atividade_selecionada = entrada
                else:
                    # Aceita atividade customizada (caso digitada manualmente)
                    self.atividade_selecionada = entrada
            self.dados["arquitetura"] = {
                "macroprocesso": self.macro_selecionado,
                "processo": self.processo_selecionado,
                "subprocesso": self.subprocesso_selecionado,
                "atividade": self.atividade_selecionada
            }
            
            self.dados["nome_processo"] = self.atividade_selecionada
            self.dados["processo_especifico"] = self.processo_selecionado
            
            codigo_gerado = self._gerar_codigo_processo()
            self.dados["codigo_arquitetura"] = codigo_gerado
            
            # Ir direto para entrega_esperada (índice 2)
            self.etapa_atual_campo = 2
            
            # Se está editando arquitetura, voltar para revisão
            if self.editando_campo == "arquitetura":
                self.editando_campo = None
                self.estado = "revisao"
                return {
                    "resposta": f"Arquitetura atualizada! Nova localização: {self.atividade_selecionada}. Aqui está o resumo atualizado:",
                    "tipo_interface": "revisao",
                    "dados_interface": {
                        "dados_completos": self._gerar_dados_completos_pop(),
                        "codigo_gerado": codigo_gerado
                    },
                    "dados_extraidos": {
                        "arquitetura": self.dados["arquitetura"],
                        "codigo_arquitetura": codigo_gerado
                    },
                    "conversa_completa": False,
                    "progresso": "10/10",
                    "proximo_estado": "revisao"
                }
            
            # Fluxo normal - ir para entrega esperada
            self.estado = "campos"

            # Tentar gerar sugestão de resultado final com IA
            sugestao_ia = self._sugerir_resultado_final_com_ia()

            if sugestao_ia:
                # Se conseguiu gerar sugestão, mostrar ao usuário
                return {
                    "resposta": f"Perfeito! Mapeamos sua atividade: {self.atividade_selecionada}.\n\nAgora vamos pra uma parte importante. Qual o resultado final dessa atividade?\n\nPense no que é entregue quando o processo termina. Por exemplo: Auxílio concedido, Requerimento analisado, Cadastro atualizado, Irregularidade apurada, Pagamento corrigido, Formulário protocolado.\n\nQual é o resultado final desta atividade?",
                    "tipo_interface": "texto",
                    "dados_interface": {
                        "sugestao_ia": sugestao_ia,
                        "contexto": "resultado_final"
                    },
                    "dados_extraidos": {
                        "arquitetura": self.dados["arquitetura"],
                        "macroprocesso": self.macro_selecionado,
                        "nome_processo": self.atividade_selecionada,
                        "processo_especifico": self.processo_selecionado,
                        "codigo_processo": codigo_gerado,
                        "codigo_arquitetura": codigo_gerado
                    },
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "campos"
                }
            else:
                # Fallback caso a IA falhe
                return {
                    "resposta": f"Perfeito! Mapeamos sua atividade: {self.atividade_selecionada}.\n\nAgora vamos pra uma parte importante. Qual o resultado final dessa atividade?\n\nPense no que é entregue quando o processo termina. Por exemplo: Auxílio concedido, Requerimento analisado, Cadastro atualizado, Irregularidade apurada, Pagamento corrigido, Formulário protocolado.\n\nQual é o resultado final desta atividade?",
                    "tipo_interface": "texto",
                    "dados_interface": {},
                    "dados_extraidos": {
                        "arquitetura": self.dados["arquitetura"],
                        "macroprocesso": self.macro_selecionado,
                        "nome_processo": self.atividade_selecionada,
                        "processo_especifico": self.processo_selecionado,
                        "codigo_processo": codigo_gerado,
                        "codigo_arquitetura": codigo_gerado
                    },
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "campos"
                }

    def _processar_sistemas(self, mensagem):
        """Processa seleção de sistemas"""
        sistemas_texto = mensagem.strip()
        
        if sistemas_texto.lower() in ["não sei", "nenhum", "não utilizo"]:
            self.sistemas_selecionados = []
        else:
            separadores = [',', ';']
            for sep in separadores:
                if sep in sistemas_texto:
                    sistemas_texto = sistemas_texto.replace(sep, ',')
                    break
            
            sistemas_lista = [s.strip() for s in sistemas_texto.split(',')]
            
            todos_sistemas = []
            for categoria in self.SISTEMAS_DECIPEX.values():
                todos_sistemas.extend(categoria)
            
            sistemas_encontrados = []
            sistemas_outros = []
            
            for sistema in sistemas_lista:
                encontrado = False
                for sistema_conhecido in todos_sistemas:
                    if sistema.lower() in sistema_conhecido.lower() or sistema_conhecido.lower() in sistema.lower():
                        if sistema_conhecido not in sistemas_encontrados:
                            sistemas_encontrados.append(sistema_conhecido)
                        encontrado = True
                        break
                
                if not encontrado and len(sistema) > 2:
                    sistemas_outros.append(sistema)
            
            self.sistemas_selecionados = sistemas_encontrados + sistemas_outros

        self.dados["sistemas"] = self.sistemas_selecionados
        
        # Se está editando sistemas, voltar para revisão
        if self.editando_campo == "sistemas":
            self.editando_campo = None
            self.estado = "revisao"
            return {
                "resposta": f"Sistemas atualizados! Aqui está o resumo atualizado:",
                "tipo_interface": "revisao",
                "dados_interface": {
                    "dados_completos": self._gerar_dados_completos_pop(),
                    "codigo_gerado": self._gerar_codigo_processo()
                },
                "dados_extraidos": {"sistemas": self.sistemas_selecionados},
                "conversa_completa": False,
                "progresso": "10/10",
                "proximo_estado": "revisao"
            }
        
        # Fluxo normal
        self.estado = "campos"
        
        print(f"[SYS] SISTEMAS PROCESSADOS: Estado agora é '{self.estado}'")
        print(f"[SYS] SISTEMAS: {self.sistemas_selecionados}")
        
        # Após sistemas, ir para dispositivos_normativos (índice 3)
        self.etapa_atual_campo = 3
        campo_atual = self.campos_principais[self.etapa_atual_campo]
        
        resposta_sistemas = f"Sistemas registrados: {', '.join(self.sistemas_selecionados) if self.sistemas_selecionados else 'Nenhum sistema específico'}.\n\n"
        
        # Verificar se o próximo campo é dispositivos_normativos para sugerir base legal
        if campo_atual["nome"] == "dispositivos_normativos":
            sugestoes = self._sugerir_base_legal_contextual()
            
            if sugestoes:
                return {
                    "resposta": f"{resposta_sistemas}{campo_atual['pergunta']}",
                    "tipo_interface": "normas",
                    "dados_interface": {
                        "sugestoes": sugestoes,
                        "campo_livre": True,
                        "multipla_selecao": True
                    },
                    "dados_extraidos": {"sistemas": self.sistemas_selecionados},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "campos"
                }
        
        return {
            "resposta": f"{resposta_sistemas}{campo_atual['pergunta']} {campo_atual['exemplo']}",
            "tipo_interface": "texto",
            "dados_interface": {},
            "dados_extraidos": {"sistemas": self.sistemas_selecionados},
            "conversa_completa": False,
            "progresso": self._calcular_progresso(),
            "proximo_estado": "campos"
        }

    def _processar_campos(self, mensagem):
        """Processa coleta de campos principais com validação"""
        print(f"\n{'='*80}")
        print(f"[FIELDS] PROCESSAR CAMPOS")
        print(f"   Etapa atual: {self.etapa_atual_campo}/{len(self.campos_principais)}")
        
        if self.etapa_atual_campo < len(self.campos_principais):
            campo_atual = self.campos_principais[self.etapa_atual_campo]
            print(f"   Campo atual: {campo_atual['nome']}")
        
        print(f"{'='*80}\n")
        
        if self.etapa_atual_campo < len(self.campos_principais):
            campo_atual = self.campos_principais[self.etapa_atual_campo]
            
            msg_lower = mensagem.lower().strip()
            
            # ✅ CORREÇÃO: Removido bloco duplicado de return que causava o bug
            # Apenas validação de "não sei" permanece
            if msg_lower in ["não sei", "nao sei", "não lembro", "nao lembro", "ajuda", "help"]:
                return {
                    "resposta": f"Entendo que pode ser difícil. Vou te ajudar com exemplos:\n\n{campo_atual['exemplo']}\n\nTente descrever mesmo que de forma simples. Se realmente não souber, pode digitar 'pular' para avançar.",
                    "tipo_interface": "texto",
                    "dados_interface": {},
                    "dados_extraidos": {},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "campos"
                }
            
            if msg_lower == "pular":
                self.dados[campo_atual["nome"]] = "Não informado"
            else:
                self.dados[campo_atual["nome"]] = mensagem.strip()

            # ✅ NOVO: Se acabou de coletar operadores, ir para fluxos_entrada
            if campo_atual["nome"] == "operadores":
                self.estado = "fluxos_entrada"
                return {
                    "resposta": f"Ótimo! Operadores registrados.\n\nAgora vamos começar a falar do seu processo. **De onde ele vem?** Ou seja, como ele chega até você?",
                    "tipo_interface": "fluxos_entrada",
                    "dados_interface": {},
                    "dados_extraidos": {campo_atual["nome"]: self.dados[campo_atual["nome"]]},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "fluxos_entrada"
                }

            self.etapa_atual_campo += 1
            
            # NOVO: Se acabou de coletar entrega_esperada (índice 2), ir para sistemas
            if campo_atual["nome"] == "entrega_esperada":
                self.estado = "sistemas"
                return {
                    "resposta": f"Anotado! {mensagem[:50]}{'...' if len(mensagem) > 50 else ''}\n\nAgora vamos selecionar quais sistemas são usados durante o processo:",
                    "tipo_interface": "sistemas",
                    "dados_interface": {
                        "sistemas_por_categoria": self.SISTEMAS_DECIPEX,
                        "permite_outros": True
                    },
                    "dados_extraidos": {campo_atual["nome"]: self.dados[campo_atual["nome"]]},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "sistemas"
                }
            
            if self.etapa_atual_campo < len(self.campos_principais):
                proximo_campo = self.campos_principais[self.etapa_atual_campo]
                
                # Se está editando um campo específico, voltar para revisão
                if self.editando_campo:
                    self.editando_campo = None
                    self.estado = "revisao"
                    return {
                        "resposta": f"Campo atualizado! Aqui está o resumo:",
                        "tipo_interface": "revisao",
                        "dados_interface": {
                            "dados_completos": self._gerar_dados_completos_pop(),
                            "codigo_gerado": self._gerar_codigo_processo()
                        },
                        "dados_extraidos": {campo_atual["nome"]: self.dados[campo_atual["nome"]]},
                        "conversa_completa": False,
                        "progresso": "10/10",
                        "proximo_estado": "revisao"
                    }
                
                if proximo_campo["nome"] == "operadores":
                    return {
                        "resposta": f"Anotado! {mensagem[:50]}{'...' if len(mensagem) > 50 else ''}\n\n{proximo_campo['pergunta']}",
                        "tipo_interface": "operadores",
                        "dados_interface": {
                            "opcoes": self.OPERADORES_DECIPEX
                        },
                        "dados_extraidos": {campo_atual["nome"]: self.dados[campo_atual["nome"]]},
                        "conversa_completa": False,
                        "progresso": self._calcular_progresso(),
                        "proximo_estado": "operadores_para_fluxos"  # ← MUDANÇA: próximo vai para fluxos_entrada
                    }
                
                elif proximo_campo["nome"] == "dispositivos_normativos":
                    sugestoes = self._sugerir_base_legal_contextual()
                    
                    if sugestoes:
                        return {
                            "resposta": f"Anotado! {mensagem[:50]}{'...' if len(mensagem) > 50 else ''}\n\n{proximo_campo['pergunta']}",
                            "tipo_interface": "normas",
                            "dados_interface": {
                                "sugestoes": sugestoes,
                                "campo_livre": True,
                                "multipla_selecao": True
                            },
                            "dados_extraidos": {campo_atual["nome"]: self.dados[campo_atual["nome"]]},
                            "conversa_completa": False,
                            "progresso": self._calcular_progresso(),
                            "proximo_estado": "campos"
                        }
                    else:
                        resposta = f"Anotado! {mensagem[:50]}{'...' if len(mensagem) > 50 else ''}\n\n{proximo_campo['pergunta']} {proximo_campo['exemplo']}"
                elif proximo_campo["nome"] == "pontos_atencao":
                    # Mensagem personalizada para pontos de atenção
                    nome_exibir = self.nome_usuario or self.nome_temporario or "você"
                    resposta = f"Anotado! Os Dispositivos Normativos já estão no item 2 do POP.\n\nAgora, {nome_exibir}, pense um pouco e me diga: há algo que você sempre lembra: \"Ao fazer isso, é importante ter atenção a...\" algo que você colocar no POP como - Pontos Gerais de Atenção na Atividade?\n\n{proximo_campo['exemplo']}"
                else:
                    resposta = f"Anotado! {mensagem[:50]}{'...' if len(mensagem) > 50 else ''}\n\n{proximo_campo['pergunta']} {proximo_campo['exemplo']}"

                return {
                    "resposta": resposta,
                    "tipo_interface": "texto",
                    "dados_interface": {},
                    "dados_extraidos": {campo_atual["nome"]: self.dados[campo_atual["nome"]]},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "campos"
                }
            else:
                # Transição motivacional antes das etapas
                self.estado = "pre_etapas"
                nome_exibir = self.nome_usuario or self.nome_temporario or "você"
                return {
                    "resposta": f"Perfeito, {nome_exibir}! Já temos: a identificação da sua atividade, os dispositivos normativos, os sistemas utilizados e os operadores envolvidos. Muita coisa!\n\nMas agora entramos na parte principal, no coração do mapeamento.\n\nPronto pra isso?",
                    "tipo_interface": "texto",
                    "dados_interface": {
                        "botoes": ["Sim", "Não"]
                    },
                    "dados_extraidos": {campo_atual["nome"]: self.dados[campo_atual["nome"]]},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "pre_etapas"
                }
        else:
            return self._erro_estado()

    def _processar_documentos(self, mensagem):
        """
        Processa lista estruturada de documentos.
        Espera receber JSON com lista de documentos estruturados.

        Estrutura esperada:
        [
            {
                "tipo_documento": "Formulário",
                "tipo_uso": "Gerado",
                "obrigatorio": true,
                "descricao": "Requerimento de auxílio",
                "sistema": null
            },
            ...
        ]
        """
        try:
            import json

            # Tentar parsear como JSON (lista estruturada)
            if mensagem.strip().startswith('['):
                documentos_lista = json.loads(mensagem.strip())
            else:
                # Fallback: string simples (compatibilidade)
                documentos_lista = [{"descricao": mensagem.strip()}]

            if documentos_lista and len(documentos_lista) > 0:
                self.documentos_processo = documentos_lista
                self.dados["documentos_utilizados"] = documentos_lista

                # Se está editando documentos, voltar para revisão
                if self.editando_campo == "documentos_utilizados":
                    self.editando_campo = None
                    self.estado = "revisao"
                    return {
                        "resposta": f"Documentos atualizados! ({len(documentos_lista)} documento(s)). Aqui está o resumo:",
                        "tipo_interface": "revisao",
                        "dados_interface": {
                            "dados_completos": self._gerar_dados_completos_pop(),
                            "codigo_gerado": self._gerar_codigo_processo()
                        },
                        "dados_extraidos": {"documentos_utilizados": documentos_lista},
                        "conversa_completa": False,
                        "progresso": "10/10",
                        "proximo_estado": "revisao"
                    }

                # NOVO: Documentos vêm depois de etapas, então vai para fluxos
                self.estado = "fluxos_entrada"
                return {
                    "resposta": f"Ótimo! Registrei {len(documentos_lista)} documento(s). Agora vamos aos FLUXOS DE ENTRADA.",
                    "tipo_interface": "fluxos_entrada",
                    "dados_interface": {},
                    "dados_extraidos": {"documentos_utilizados": documentos_lista},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "fluxos_entrada"
                }
            else:
                return {
                    "resposta": "Por favor, adicione pelo menos um documento antes de continuar.",
                    "tipo_interface": "documentos",
                    "dados_interface": {},
                    "dados_extraidos": {},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "documentos"
                }

        except json.JSONDecodeError as e:
            print(f"[ERRO] Falha ao processar documentos como JSON: {e}")
            return {
                "resposta": "Erro ao processar documentos. Por favor, tente novamente.",
                "tipo_interface": "documentos",
                "dados_interface": {},
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": self._calcular_progresso(),
                "proximo_estado": "documentos"
            }

    def _processar_pre_etapas(self, mensagem):
        """Transição motivacional antes de mapear as etapas"""
        msg_lower = mensagem.lower().strip()
        nome_exibir = self.nome_usuario or self.nome_temporario or "você"

        # Aceitar várias formas de "sim"
        respostas_positivas = ["sim", "s", "yes", "y", "ok", "vamos", "bora", "claro", "com certeza", "pronto"]

        if any(resp in msg_lower for resp in respostas_positivas):
            # Avançar para etapas
            self.estado = "etapas"
            return {
                "resposta": f"Então agora vamos mapear as etapas do processo, {nome_exibir}! Me diga agora a **Etapa 1**: a primeira coisa que você faz ao começar sua atividade.",
                "tipo_interface": "texto",
                "dados_interface": {},
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": self._calcular_progresso(),
                "proximo_estado": "etapas"
            }
        else:
            # Se disse não ou algo confuso, encorajar
            return {
                "resposta": f"Entendo que pode parecer desafiador, {nome_exibir}, mas não se preocupe! Vou te guiar passo a passo.\n\nVocê está indo muito bem até aqui. Vamos continuar?",
                "tipo_interface": "texto",
                "dados_interface": {
                    "botoes": ["Sim, vamos lá!", "Preciso de ajuda"]
                },
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": self._calcular_progresso(),
                "proximo_estado": "pre_etapas"
            }

    def _processar_fluxos_entrada(self, mensagem):
        """Processa fluxos de entrada do processo com nova interface"""
        resposta_lower = mensagem.lower().strip()

        # Aceitar "não sei" ou "pular"
        if resposta_lower in ["nao_sei", "não sei", "pular", "skip"]:
            self.fluxos_entrada = []
            self.dados["fluxos_entrada"] = []
        else:
            # Tentar parsear JSON estruturado vindo da interface
            try:
                resposta_json = json.loads(mensagem)
                if isinstance(resposta_json, dict):
                    # Estrutura: { origens_selecionadas: [...], outras_origens: "..." }
                    origens = resposta_json.get("origens_selecionadas", [])
                    outras = resposta_json.get("outras_origens")

                    # Montar lista de fluxos de entrada
                    fluxos_lista = []
                    for origem in origens:
                        fluxo_texto = origem["tipo"]
                        if origem.get("especificacao"):
                            fluxo_texto += f": {origem['especificacao']}"
                        fluxos_lista.append(fluxo_texto)

                    if outras:
                        fluxos_lista.append(outras)

                    self.fluxos_entrada = fluxos_lista
                    self.dados["fluxos_entrada"] = fluxos_lista
                else:
                    # Fallback: texto livre
                    self.fluxos_entrada = [mensagem]
                    self.dados["fluxos_entrada"] = [mensagem]
            except json.JSONDecodeError:
                # Fallback: texto livre
                self.fluxos_entrada = [mensagem]
                self.dados["fluxos_entrada"] = [mensagem]

        # Avançar para pre_etapas
        self.estado = "pre_etapas"
        nome_exibir = self.nome_usuario or self.nome_temporario or "você"

        return {
            "resposta": f"Perfeito, {nome_exibir}! Já temos: a identificação da sua atividade, os dispositivos normativos, os sistemas utilizados, os operadores envolvidos e de onde o processo vem. Muita coisa!\n\nMas agora entramos na parte principal, no coração do mapeamento.\n\nPronto pra isso?",
            "tipo_interface": "texto",
            "dados_interface": {
                "botoes": ["Sim", "Não"]
            },
            "dados_extraidos": {"fluxos_entrada": self.fluxos_entrada},
            "conversa_completa": False,
            "progresso": self._calcular_progresso(),
            "proximo_estado": "pre_etapas"
        }

    def _processar_fluxos_saida(self, mensagem):
        """Processa fluxos de saída do processo com nova interface"""
        resposta_lower = mensagem.lower().strip()

        # Aceitar "não sei" ou "pular"
        if resposta_lower in ["nao_sei", "não sei", "pular", "skip"]:
            self.fluxos_saida = []
            self.dados["fluxos_saida"] = []
        else:
            # Tentar parsear JSON estruturado vindo da interface
            try:
                resposta_json = json.loads(mensagem)
                if isinstance(resposta_json, dict):
                    # Estrutura: { destinos_selecionados: [...], outros_destinos: "..." }
                    destinos = resposta_json.get("destinos_selecionados", [])
                    outros = resposta_json.get("outros_destinos")

                    # Montar lista de fluxos de saída
                    fluxos_lista = []
                    for destino in destinos:
                        fluxo_texto = destino["tipo"]
                        if destino.get("especificacao"):
                            fluxo_texto += f": {destino['especificacao']}"
                        fluxos_lista.append(fluxo_texto)

                    if outros:
                        fluxos_lista.append(outros)

                    self.fluxos_saida = fluxos_lista
                    self.dados["fluxos_saida"] = fluxos_lista
                else:
                    # Fallback: texto livre
                    self.fluxos_saida = [mensagem]
                    self.dados["fluxos_saida"] = [mensagem]
            except json.JSONDecodeError:
                # Fallback: texto livre
                self.fluxos_saida = [mensagem]
                self.dados["fluxos_saida"] = [mensagem]

        # Avançar para documentos
        self.estado = "documentos"

        return {
            "resposta": f"Ótimo! Agora vamos aos **DOCUMENTOS UTILIZADOS** nesta atividade.",
            "tipo_interface": "documentos",
            "dados_interface": {},
            "dados_extraidos": {"fluxos_saida": self.fluxos_saida},
            "conversa_completa": False,
            "progresso": self._calcular_progresso(),
            "proximo_estado": "documentos"
        }

    def _processar_etapas(self, mensagem):
        """Processa coleta dinâmica de etapas com detalhamento hierárquico"""
        resposta_lower = mensagem.lower().strip()

        # DEBUG: Mostrar estado logo no início
        print(f"\n[DEBUG-INICIO] _processar_etapas chamada com mensagem: '{mensagem[:50]}'")
        print(f"[DEBUG-INICIO] aguardando_operadores_etapa = {self.aguardando_operadores_etapa}")
        print(f"[DEBUG-INICIO] aguardando_pergunta_condicionais = {self.aguardando_pergunta_condicionais}")
        print(f"[DEBUG-INICIO] aguardando_detalhes = {self.aguardando_detalhes}")
        
        # Se está aguardando resposta sobre condicionais
        if self.aguardando_pergunta_condicionais:
            resposta_condicionais = mensagem.lower().strip()
            numero_etapa = len(self.etapas_processo) + 1

            # 🔒 PROTEÇÃO: Se a mensagem parece ser de operador (não é sim/não/ajuda), ignorar este bloco
            # Isso evita que cliques duplicados (timeout/retry) interpretem o operador como "não"
            respostas_validas = ['sim', 's', 'yes', 'tem', 'possui', 'não', 'nao', 'no', 'n',
                                'ajuda', 'não entendi', 'nao entendi', 'ajuda helena', 'explicar', '?',
                                'entendi', 'continuar', 'ok', 'entendi continuar', 'entendido', 'voltar']

            if resposta_condicionais not in respostas_validas:
                print(f"[DEBUG-PROTEÇÃO] Mensagem '{mensagem}' não é resposta de condicionais válida. Ignorando este bloco.")
                # Não processar - deixar cair no próximo bloco (operadores de etapa)
                # NÃO FAZ RETURN - continua para o próximo if

            # Opção: Usuário voltou da tela de ajuda (entendeu a explicação)
            # Deve voltar para a pergunta original: tem condicionais?
            elif resposta_condicionais in ['entendi', 'continuar', 'ok', 'entendi continuar', 'entendido', 'voltar']:
                # NÃO zerar aguardando_pergunta_condicionais - manter True para voltar à pergunta
                return {
                    "resposta": f"Ótimo! Agora que você entendeu, vamos voltar à pergunta:\n\n**A Etapa {numero_etapa} '{self.etapa_temporaria}' tem decisões/condições?**",
                    "tipo_interface": "condicionais",
                    "dados_interface": {
                        "numero_etapa": numero_etapa,
                        "descricao_etapa": self.etapa_temporaria
                    },
                    "dados_extraidos": {},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "etapas"
                }

            # Opção: Pedir ajuda à Helena
            elif resposta_condicionais in ['ajuda', 'não entendi', 'nao entendi', 'ajuda helena', 'explicar', '?']:
                from .helena_mapeamento import helena_mapeamento

                prompt_ajuda = f"""O usuário está mapeando a etapa: "{self.etapa_temporaria}"
Executada por: {self.operadores_etapa_atual[0] if self.operadores_etapa_atual else 'não especificado'}

Ele não entendeu o que são 'etapas com condições/decisões'.

Explique de forma clara e prática:
1. O que é uma etapa LINEAR (sem condições)
2. O que é uma etapa COM CONDIÇÕES (com decisões)
3. Dê 2-3 exemplos práticos do setor público

Use exemplos simples como:
- Analisar documentação (completa/incompleta)
- Verificar valor (aprovação automática/análise manual)
- Conferir elegibilidade (apto/inapto)

Seja objetiva e termine perguntando: "A etapa '{self.etapa_temporaria}' tem esse tipo de decisão/condição?"
"""

                explicacao_helena = helena_mapeamento(prompt_ajuda)

                # Voltar a aguardar resposta sobre condicionais
                self.aguardando_pergunta_condicionais = True

                return {
                    "resposta": explicacao_helena,
                    "tipo_interface": "condicionais_ajuda",
                    "dados_interface": {
                        "numero_etapa": numero_etapa,
                        "descricao_etapa": self.etapa_temporaria
                    },
                    "dados_extraidos": {},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "etapas"
                }

            # Opção: SIM, tem condicionais
            elif resposta_condicionais in ['sim', 's', 'yes', 'tem', 'possui']:
                self.aguardando_pergunta_condicionais = False
                self.etapa_tem_condicionais = True
                self.aguardando_tipo_condicional = True

                resposta_base = {
                    "resposta": f"Ótimo! A Etapa {numero_etapa} tem condições/decisões.\n\nQuantos cenários possíveis existem nessa decisão?",
                    "tipo_interface": "tipo_condicional",
                    "dados_interface": {
                        "numero_etapa": numero_etapa,
                        "opcoes": [
                            {"id": "binario", "label": "2 cenários (Sim/Não, Aprovado/Reprovado, Completo/Incompleto, etc)"},
                            {"id": "multiplos", "label": "Múltiplos cenários (3 ou mais opções diferentes)"}
                        ]
                    },
                    "dados_extraidos": {"tem_condicionais": True},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "etapas"
                }
                return self._criar_resposta_com_tempo_real(resposta_base)

            # Opção: NÃO, etapa linear (apenas se for resposta válida de "não")
            elif resposta_condicionais in ['não', 'nao', 'no', 'n']:
                self.aguardando_pergunta_condicionais = False
                self.etapa_tem_condicionais = False
                self.aguardando_detalhes = True
                resposta_base = {
                    "resposta": f"Entendido. Etapa {numero_etapa} é linear (sem condições).\n\nAgora vamos aos detalhes/passos dessa etapa. Qual o primeiro detalhe?",
                    "tipo_interface": "texto",
                    "dados_interface": {},
                    "dados_extraidos": {"tem_condicionais": False},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "etapas"
                }
                return self._criar_resposta_com_tempo_real(resposta_base)

        # Se está aguardando tipo de condicional (binário ou múltiplos)
        if self.aguardando_tipo_condicional:
            tipo_escolhido = mensagem.lower().strip()
            numero_etapa = len(self.etapas_processo) + 1
            self.aguardando_tipo_condicional = False

            if tipo_escolhido in ['binario', 'binário', '2', 'dois', '2 cenarios', '2 cenários']:
                self.tipo_condicional = 'binario'
            elif tipo_escolhido in ['multiplos', 'múltiplos', 'multiplo', 'múltiplo', '3', 'tres', 'três', 'mais']:
                self.tipo_condicional = 'multiplos'
            else:
                # Se não entender, assume binário
                self.tipo_condicional = 'binario'

            # Agora pergunta o que acontece ANTES da decisão
            self.aguardando_antes_decisao = True

            return {
                "resposta": f"Certo! Vamos definir os cenários.\n\nAntes de tomar a decisão, o que deve ser feito?\n\nExemplo: 'Conferir documentação', 'Analisar valor do pedido', 'Verificar elegibilidade'\n\nO que deve ser feito ANTES da decisão?",
                "tipo_interface": "texto",
                "dados_interface": {
                    "numero_etapa": numero_etapa,
                    "tipo_condicional": self.tipo_condicional,
                    "placeholder": "Ex: Conferir se a documentação está completa"
                },
                "dados_extraidos": {"tipo_condicional": self.tipo_condicional},
                "conversa_completa": False,
                "progresso": self._calcular_progresso(),
                "proximo_estado": "etapas"
            }

        # Se está aguardando o que fazer antes da decisão
        if self.aguardando_antes_decisao:
            self.antes_decisao = mensagem.strip()
            self.aguardando_antes_decisao = False
            numero_etapa = len(self.etapas_processo) + 1

            # Ir direto para cenários (documentos serão coletados depois)
            self.aguardando_cenarios = True

            # Pegar lista de etapas já criadas para sugestão
            etapas_criadas = [{"id": f"etapa_{e['numero']}", "label": e['descricao']} for e in self.etapas_processo]

            if self.tipo_condicional == 'binario':
                return {
                    "resposta": f"Perfeito! Antes da decisão: '{self.antes_decisao}'\n\n💡 *Lembre-se: na próxima fase vamos listar os documentos necessários, não esqueça!*\n\nAgora defina os 2 cenários:",
                    "tipo_interface": "cenarios_binario",
                    "dados_interface": {
                        "numero_etapa": numero_etapa,
                        "antes_decisao": self.antes_decisao,
                        "etapas_disponiveis": etapas_criadas
                    },
                    "dados_extraidos": {"antes_decisao": self.antes_decisao},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "etapas"
                }
            else:  # multiplos
                return {
                    "resposta": f"Perfeito! Antes da decisão: '{self.antes_decisao}'\n\n💡 *Lembre-se: na próxima fase vamos listar os documentos necessários, não esqueça!*\n\nQuantos cenários existem?",
                    "tipo_interface": "cenarios_multiplos_quantidade",
                    "dados_interface": {
                        "numero_etapa": numero_etapa,
                        "antes_decisao": self.antes_decisao,
                        "etapas_disponiveis": etapas_criadas
                    },
                    "dados_extraidos": {"antes_decisao": self.antes_decisao},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "etapas"
                }

        # ========== NOVO FLUXO: Coletar descrições dos cenários primeiro ==========
        if self.aguardando_cenarios:
            import json
            try:
                # Espera JSON com APENAS as descrições dos cenários
                cenarios_data = json.loads(mensagem)
                numero_etapa = len(self.etapas_processo) + 1

                # Salvar cenários coletados (apenas descrições, sem subetapas ainda)
                cenarios_descritos = cenarios_data.get("cenarios", [])

                # Armazenar cenários para próxima fase
                self.cenarios_coletados = []
                for i, cenario in enumerate(cenarios_descritos, 1):
                    # Numeração hierárquica: 1.1.1, 1.1.2, 1.1.3...
                    numero_cenario = f"{numero_etapa}.1.{i}"
                    self.cenarios_coletados.append({
                        "numero": numero_cenario,
                        "descricao": cenario.get("descricao", ""),
                        "subetapas": []  # Será preenchido depois
                    })

                # Agora vamos detalhar o PRIMEIRO cenário
                self.aguardando_cenarios = False
                self.aguardando_subetapas_cenario = True
                self.cenario_atual_detalhando = 0  # Índice do cenário sendo detalhado

                primeiro_cenario = self.cenarios_coletados[0]

                return {
                    "resposta": f"Cenários registrados! Agora vamos detalhar cada um.",
                    "tipo_interface": "subetapas_cenario",
                    "dados_interface": {
                        "numero_cenario": primeiro_cenario['numero'],
                        "descricao_cenario": primeiro_cenario['descricao'],
                        "todos_cenarios": self.cenarios_coletados,
                        "cenario_atual_index": 0
                    },
                    "dados_extraidos": {"cenarios_coletados": self.cenarios_coletados},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "etapas"
                }

            except Exception as e:
                print(f"[ERRO] Erro ao processar cenários: {e}")
                import traceback
                traceback.print_exc()
                return {
                    "resposta": f"Desculpe, houve um erro ao processar os cenários. Por favor, tente novamente ou descreva de forma mais simples.",
                    "tipo_interface": "texto",
                    "dados_interface": {},
                    "dados_extraidos": {},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "etapas"
                }

        # ========== NOVO: Aguardando subetapas de um cenário específico ==========
        if self.aguardando_subetapas_cenario:
            numero_etapa = len(self.etapas_processo) + 1
            cenario_atual = self.cenarios_coletados[self.cenario_atual_detalhando]

            # Se usuário digitou "pular", não adiciona subetapas
            if mensagem.lower().strip() in ['pular', 'skip', 'não', 'nao', 'sem subetapas']:
                # Não adiciona subetapas, deixa lista vazia
                pass
            else:
                # Processar subetapas (uma por linha)
                subetapas_texto = mensagem.strip().split('\n')
                for i, subetapa_desc in enumerate(subetapas_texto, 1):
                    if subetapa_desc.strip():
                        # Numeração hierárquica: 1.1.1.1, 1.1.1.2, 1.1.1.3...
                        numero_subetapa = f"{cenario_atual['numero']}.{i}"
                        cenario_atual['subetapas'].append({
                            "numero": numero_subetapa,
                            "descricao": subetapa_desc.strip()
                        })

            # Verificar se há mais cenários para detalhar
            self.cenario_atual_detalhando += 1

            if self.cenario_atual_detalhando < len(self.cenarios_coletados):
                # Ainda há cenários para detalhar
                proximo_cenario = self.cenarios_coletados[self.cenario_atual_detalhando]
                return {
                    "resposta": f"Subetapas registradas!",
                    "tipo_interface": "subetapas_cenario",
                    "dados_interface": {
                        "numero_cenario": proximo_cenario['numero'],
                        "descricao_cenario": proximo_cenario['descricao'],
                        "todos_cenarios": self.cenarios_coletados,
                        "cenario_atual_index": self.cenario_atual_detalhando
                    },
                    "dados_extraidos": {},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "etapas"
                }
            else:
                # Todos os cenários foram detalhados! Agora salvar a etapa completa
                self.aguardando_subetapas_cenario = False

                # Construir etapa completa com hierarquia
                etapa = {
                    "numero": str(numero_etapa),
                    "descricao": self.etapa_temporaria,
                    "operador": self.operadores_etapa_atual[0] if self.operadores_etapa_atual else "Não especificado",
                    "tipo": "condicional",
                    "tipo_condicional": self.tipo_condicional,
                    "antes_decisao": {
                        "numero": f"{numero_etapa}.1",
                        "descricao": self.antes_decisao
                    },
                    "cenarios": self.cenarios_coletados  # Já tem número, descricao e subetapas
                }

                self.etapas_processo.append(etapa)

                # Limpar estados
                self.etapa_tem_condicionais = False
                self.tipo_condicional = None
                self.antes_decisao = None
                self.cenarios_coletados = []
                self.cenario_atual_detalhando = None
                self.operadores_etapa_atual = []
                self.etapa_temporaria = None

                return {
                    "resposta": f"Etapa {numero_etapa} completa com hierarquia!\n\nHá mais alguma etapa? (Digite a próxima etapa ou 'não' para finalizar)",
                    "tipo_interface": "texto",
                    "dados_interface": {},
                    "dados_extraidos": {"etapa_adicionada": etapa},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "etapas"
                }

        # Se está aguardando operador da etapa
        print(f"[DEBUG] aguardando_operadores_etapa = {self.aguardando_operadores_etapa}")
        if self.aguardando_operadores_etapa:
            print(f"[DEBUG] ENTROU NO IF DE OPERADORES! Mensagem: '{mensagem}'")
            self.operadores_etapa_atual = [mensagem.strip()]
            self.aguardando_operadores_etapa = False
            numero_etapa = len(self.etapas_processo) + 1

            # Agora pergunta sobre condicionais ANTES dos detalhes
            self.aguardando_pergunta_condicionais = True
            print(f"[DEBUG] Setando aguardando_pergunta_condicionais = True")
            resposta_base = {
                "resposta": f"Operador definido para Etapa {numero_etapa}: {mensagem.strip()}\n\nAgora vamos verificar se esta etapa tem decisões condicionais:",
                "tipo_interface": "condicionais",
                "dados_interface": {
                    "numero_etapa": numero_etapa
                },
                "dados_extraidos": {"operador_etapa": mensagem.strip()},
                "conversa_completa": False,
                "progresso": self._calcular_progresso(),
                "proximo_estado": "etapas"
            }
            print(f"[DEBUG] Retornando resposta_base com tipo_interface = condicionais")
            return self._criar_resposta_com_tempo_real(resposta_base)
        
        if len(mensagem.strip()) < 10 and resposta_lower not in ["não", "nao", "não há mais", "sim", "s"]:
            return {
                "resposta": f"Por favor, descreva a etapa de forma mais completa (mínimo 10 caracteres). Exemplo do POP anexo: 'Analisar requerimentos Sigepe de Plano de Saúde Particular'",
                "tipo_interface": "texto",
                "dados_interface": {},
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": self._calcular_progresso(),
                "proximo_estado": "etapas"
            }
        
        if not self.aguardando_detalhes:
            if resposta_lower in ["não", "nao", "não há mais", "fim", "finalizar"]:
                if self.etapas_processo:
                    self.dados["etapas"] = self.etapas_processo
                    
                    # Se está editando etapas, voltar para revisão
                    if self.editando_campo == "etapas":
                        self.editando_campo = None
                        self.estado = "revisao"
                        return {
                            "resposta": f"Etapas atualizadas! Aqui está o resumo:",
                            "tipo_interface": "revisao",
                            "dados_interface": {
                                "dados_completos": self._gerar_dados_completos_pop(),
                                "codigo_gerado": self._gerar_codigo_processo()
                            },
                            "dados_extraidos": {"etapas": self.etapas_processo},
                            "conversa_completa": False,
                            "progresso": "10/10",
                            "proximo_estado": "revisao"
                        }
                    
                    # ✅ NOVO: Após etapas, ir para FLUXOS_SAIDA
                    self.estado = "fluxos_saida"
                    return {
                        "resposta": "Ótimo! Etapas mapeadas. E agora, **para onde vai o resultado do seu trabalho?** Para qual área você entrega ou encaminha?",
                        "tipo_interface": "fluxos_saida",
                        "dados_interface": {},
                        "dados_extraidos": {"etapas": self.etapas_processo},
                        "conversa_completa": False,
                        "progresso": self._calcular_progresso(),
                        "proximo_estado": "fluxos_saida"
                    }
                else:
                    return {
                        "resposta": "Você precisa informar pelo menos uma etapa. Descreva a primeira etapa:",
                        "tipo_interface": "texto",
                        "dados_interface": {},
                        "dados_extraidos": {},
                        "conversa_completa": False,
                        "progresso": self._calcular_progresso(),
                        "proximo_estado": "etapas"
                    }
            
            self.etapa_temporaria = mensagem.strip()
            self.detalhes_etapa_atual = []
            self.aguardando_detalhes = True

            # Primeiro pergunta quem executa a etapa
            self.aguardando_operadores_etapa = True
            print(f"[DEBUG-SETANDO] aguardando_operadores_etapa setado para TRUE. Etapa: {mensagem.strip()[:50]}")
            numero_etapa = len(self.etapas_processo) + 1
            
            return {
                "resposta": f"Etapa {numero_etapa} registrada. Vamos detalhar essa etapa.",
                "tipo_interface": "operadores_etapa",
                "dados_interface": {
                    "opcoes": self.OPERADORES_DECIPEX,
                    "numero_etapa": numero_etapa
                },
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": self._calcular_progresso(),
                "proximo_estado": "etapas"
            }
        
        else:
            if resposta_lower in ["não", "nao", "não há mais", "fim"]:
                numero_etapa = len(self.etapas_processo) + 1
                self.aguardando_detalhes = False
                
                # Verificar se tem condicionais para mostrar interface adequada
                if self.etapa_tem_condicionais:
                    self.aguardando_condicionais = True
                    return {
                        "resposta": f"Etapa {numero_etapa} - detalhes pré-decisão finalizados! Agora defina os cenários condicionais:",
                        "tipo_interface": "condicionais_etapa",
                        "dados_interface": {
                            "numero_etapa": numero_etapa,
                            "descricao_etapa": self.etapa_temporaria,
                            "detalhes": self.detalhes_etapa_atual,
                            "operador": self.operadores_etapa_atual[0] if self.operadores_etapa_atual else "Não especificado",
                            "opcoes_operadores": self.OPERADORES_DECIPEX
                        },
                        "dados_extraidos": {},
                        "conversa_completa": False,
                        "progresso": self._calcular_progresso(),
                        "proximo_estado": "etapas"
                    }
                else:
                    # Finalizar etapa sem condicionais
                    etapa = {
                        "numero": numero_etapa,
                        "descricao": self.etapa_temporaria,
                        "detalhes": self.detalhes_etapa_atual,
                        "operador": self.operadores_etapa_atual[0] if self.operadores_etapa_atual else "Não especificado"
                    }
                    self.etapas_processo.append(etapa)
                    self.detalhes_etapa_atual = []
                    self.operadores_etapa_atual = []
                    self.etapa_tem_condicionais = False
                    
                    return {
                        "resposta": f"Etapa {numero_etapa} completa!\n\nHá mais alguma etapa? (Digite a próxima etapa ou 'não' para finalizar)",
                        "tipo_interface": "texto",
                        "dados_interface": {},
                        "dados_extraidos": {"etapa_adicionada": etapa},
                        "conversa_completa": False,
                        "progresso": self._calcular_progresso(),
                        "proximo_estado": "etapas"
                    }
            else:
                numero_detalhe = f"{len(self.etapas_processo) + 1}.{len(self.detalhes_etapa_atual) + 1}"
                detalhe = f"{numero_detalhe} {mensagem.strip()}"
                self.detalhes_etapa_atual.append(detalhe)
                
                return {
                    "resposta": f"Detalhe registrado: {detalhe[:60]}{'...' if len(detalhe) > 60 else ''}\n\nHá mais algum detalhe dessa etapa? (Digite o próximo detalhe ou 'não' para finalizar detalhes)",
                    "tipo_interface": "texto",
                    "dados_interface": {},
                    "dados_extraidos": {"detalhe_adicionado": detalhe},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "etapas"
                }

    def _processar_fluxos(self, mensagem):
        """Processa fluxos entre áreas com opções extras"""
        resposta_lower = mensagem.lower().strip()
        
        if resposta_lower.startswith('area_interna:') or resposta_lower.startswith('area_externa:') or resposta_lower.startswith('outra_decipex:'):
            partes = mensagem.split(':', 1)
            tipo_especial = partes[0]
            texto_livre = partes[1].strip() if len(partes) > 1 else ""
            
            fluxo_especial = {
                "tipo": tipo_especial,
                "descricao": texto_livre
            }
        
        if 'fluxos_entrada' not in self.dados:
            if resposta_lower in ["sim", "s", "há", "ha", "recebe", "sim recebe"]:
                self.fluxos_entrada = []
            else:
                self.fluxos_entrada = []
            
            self.dados["fluxos_entrada"] = self.fluxos_entrada
            
            return {
                "resposta": "Entendido! E seu processo entrega resultados para outra área da DECIPEX?",
                "tipo_interface": "fluxos_saida",
                "dados_interface": {
                    "opcoes_areas": {k: v for k, v in self.AREAS_DECIPEX.items() if k != self.area_selecionada},
                    "tipo_fluxo": "saida",
                    "opcoes_extras": [
                        {"id": "area_interna", "label": "Outra área interna da minha coordenação geral", "campo_livre": True},
                        {"id": "area_externa", "label": "Área externa da DECIPEX", "campo_livre": True},
                        {"id": "outra_decipex", "label": "Outra área da DECIPEX não listada", "campo_livre": True}
                    ]
                },
                "dados_extraidos": {"fluxos_entrada": self.fluxos_entrada},
                "conversa_completa": False,
                "progresso": self._calcular_progresso(),
                "proximo_estado": "fluxos"
            }
        
        else:
            if resposta_lower in ["sim", "s", "há", "ha", "entrega", "sim entrega"]:
                self.fluxos_saida = []
            else:
                self.fluxos_saida = []
            
            self.dados["fluxos_saida"] = self.fluxos_saida
            
            # Se está editando fluxos, voltar para revisão
            if self.editando_campo == "fluxos":
                self.editando_campo = None
                self.estado = "revisao"
                return {
                    "resposta": f"Fluxos atualizados! Aqui está o resumo:",
                    "tipo_interface": "revisao",
                    "dados_interface": {
                        "dados_completos": self._gerar_dados_completos_pop(),
                        "codigo_gerado": self._gerar_codigo_processo()
                    },
                    "dados_extraidos": {"fluxos_saida": self.fluxos_saida},
                    "conversa_completa": False,
                    "progresso": "10/10",
                    "proximo_estado": "revisao"
                }
            
            # Fluxo normal
            self.estado = "revisao"
            
            return {
                "resposta": f"Excelente, {self.nome_usuario}! Coletei todas as informações. Vou gerar o código do processo e mostrar um resumo para sua revisão.",
                "tipo_interface": "revisao",
                "dados_interface": {
                    "dados_completos": self._gerar_dados_completos_pop(),
                    "codigo_gerado": self._gerar_codigo_processo()
                },
                "dados_extraidos": {"fluxos_saida": self.fluxos_saida},
                "conversa_completa": True,
                "progresso": "10/10",
                "proximo_estado": "revisao"
            }

    def _processar_revisao(self, mensagem):
        """Processa revisão final"""
        resposta_lower = mensagem.lower().strip()
        
        if resposta_lower in ["gerar", "pdf", "finalizar", "ok", "está bom", "finalizar pop"]:
            return {
                "resposta": f"POP criado com sucesso, {self.nome_usuario}! Preparando dados para geração do PDF profissional...",
                "tipo_interface": "final",
                "dados_interface": {
                    "pop_completo": self._gerar_dados_completos_pop(),
                    "codigo": self._gerar_codigo_processo()
                },
                "dados_extraidos": self._gerar_dados_completos_pop(),
                "conversa_completa": True,
                "progresso": "10/10",
                "proximo_estado": "completo"
            }
        elif resposta_lower in ["editar", "edit", "alterar", "corrigir", "mudar"]:
            # Mostrar lista de campos editáveis
            self.estado = "selecionar_edicao"
            
            campos_editaveis = {
                "1": {"campo": "area", "label": "Área da DECIPEX"},
                "2": {"campo": "arquitetura", "label": "Localização na arquitetura (Macro/Processo/Subprocesso/Atividade)"},
                "3": {"campo": "sistemas", "label": "Sistemas utilizados"},
                "4": {"campo": "entrega_esperada", "label": "Entrega esperada/Resultado final"},
                "5": {"campo": "dispositivos_normativos", "label": "Normas e dispositivos legais"},
                "6": {"campo": "operadores", "label": "Responsáveis pela execução"},
                "7": {"campo": "pontos_atencao", "label": "Pontos de atenção"},
                "8": {"campo": "documentos_utilizados", "label": "Documentos necessários"},
                "9": {"campo": "etapas", "label": "Etapas do processo"},
                "10": {"campo": "fluxos", "label": "Fluxos de entrada e saída"}
            }
            
            return {
                "resposta": f"Qual campo você gostaria de editar, {self.nome_usuario}? Digite o número:",
                "tipo_interface": "selecao_edicao",
                "dados_interface": {
                    "campos_editaveis": campos_editaveis
                },
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": "10/10",
                "proximo_estado": "selecionar_edicao"
            }
        else:
            return {
                "resposta": f"Você pode digitar 'editar' para alterar algum campo ou 'finalizar' para gerar o PDF.",
                "tipo_interface": "revisao",
                "dados_interface": {
                    "dados_completos": self._gerar_dados_completos_pop(),
                    "editavel": True
                },
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": "10/10",
                "proximo_estado": "revisao"
            }

    def _sugerir_base_legal_contextual(self) -> List[Dict[str, Any]]:
        """Sugere base legal baseada no contexto coletado"""
        try:
            contexto = {
                "nome_processo": self.dados.get("nome_processo", ""),
                "area_codigo": self.AREAS_DECIPEX.get(self.area_selecionada, {}).get("codigo", ""),
                "sistemas": self.sistemas_selecionados,
                "objetivo": self.dados.get("entrega_esperada", "")
            }

            sugestoes = self.suggestor_base_legal.sugerir_base_legal(contexto)
            return sugestoes[:3]

        except Exception as e:
            print(f"Erro ao sugerir base legal: {e}")
            return []

    def _sugerir_resultado_final_com_ia(self) -> str:
        """
        Usa Helena Mapeamento (IA) para sugerir o resultado final da atividade
        baseado no contexto coletado até o momento
        """
        try:
            from .helena_mapeamento import helena_mapeamento

            # Montar contexto estruturado
            area_nome = self.AREAS_DECIPEX.get(self.area_selecionada, {}).get("nome", "")

            prompt_contexto = f"""Com base nas informações abaixo, sugira em 1 frase objetiva qual seria o RESULTADO FINAL ou ENTREGA ESPERADA desta atividade:

Área: {area_nome}
Macroprocesso: {self.macro_selecionado}
Processo: {self.processo_selecionado}
Subprocesso: {self.subprocesso_selecionado}
Atividade: {self.atividade_selecionada}

Responda apenas com o resultado final, sem explicações adicionais.
Exemplos de respostas válidas:
- "Auxílio-saúde concedido ou indeferido"
- "Requerimento analisado e decisão proferida"
- "Cadastro atualizado no sistema"
- "Irregularidade apurada e registrada"
"""

            sugestao = helena_mapeamento(prompt_contexto)

            # Limpar resposta (remover aspas, pontos desnecessários, perguntas da Helena)
            sugestao = sugestao.strip().strip('"').strip("'").strip()

            # Remover perguntas comuns da Helena Mapeamento que podem aparecer no final
            perguntas_remover = [
                "Essa etapa ficou clara?",
                "Podemos seguir?",
                "Ficou claro?",
                "Entendeu?",
                "Tudo certo?",
                "Alguma dúvida?"
            ]

            for pergunta in perguntas_remover:
                if pergunta in sugestao:
                    sugestao = sugestao.replace(pergunta, "").strip()

            # Remover pontos de interrogação finais
            sugestao = sugestao.rstrip('?').strip()

            # Remover espaços extras
            sugestao = ' '.join(sugestao.split())

            print(f"[IA] Sugestão de resultado final: {sugestao}")
            return sugestao

        except Exception as e:
            print(f"[ERRO] Falha ao sugerir resultado final com IA: {e}")
            import traceback
            traceback.print_exc()
            return ""

    def _formatar_sugestoes_base_legal(self, sugestoes: List[Dict[str, Any]]) -> str:
        """Formata sugestões de base legal para exibição"""
        return ""

    def _consultar_rag_exemplos(self, campo):
        """Consulta RAG quando usuário não sabe responder"""
        if not self.vectorstore:
            return {
                "resposta": f"Para o campo '{campo}', você pode me dar qualquer informação que souber. Mesmo que seja parcial, podemos construir juntos!",
                "tipo_interface": "texto",
                "dados_interface": {},
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": self._calcular_progresso(),
                "proximo_estado": self.estado
            }
        
        try:
            area_nome = self.AREAS_DECIPEX[self.area_selecionada]["nome"] if self.area_selecionada else ""
            query = f"{campo} {area_nome} DECIPEX processos"
            docs = self.vectorstore.similarity_search(query, k=3)
            
            exemplos = self._extrair_exemplos(docs, campo)
            
            return {
                "resposta": f"Com base em processos similares da {area_nome}, geralmente temos exemplos como: {exemplos}. Seu processo é similar a algum destes?",
                "tipo_interface": "texto",
                "dados_interface": {"fonte": "RAG", "exemplos": exemplos},
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": self._calcular_progresso(),
                "proximo_estado": self.estado
            }
        except Exception as e:
            return {
                "resposta": f"Vou te ajudar com o campo '{campo}'. Me conte o que você sabe, mesmo que seja pouco!",
                "tipo_interface": "texto",
                "dados_interface": {},
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": self._calcular_progresso(),
                "proximo_estado": self.estado
            }

    def _extrair_exemplos(self, docs, campo):
        """Extrai exemplos relevantes dos documentos RAG"""
        exemplos = []
        for doc in docs:
            content = doc.page_content.lower()
            if campo.lower() in content:
                linhas = content.split('\n')
                for linha in linhas:
                    if campo.lower() in linha and len(linha.strip()) > 10:
                        exemplos.append(linha.strip()[:100])
                        break
        
        return exemplos[:3] if exemplos else ["Processo de análise", "Procedimento de cadastro", "Atividade de controle"]

    def _gerar_codigo_processo(self):
        """Gera código baseado na área e estrutura hierárquica
        Formato: PREFIXO.MACRO.PROCESSO.SUBPROCESSO.ATIVIDADE
        Valida se código já existe no banco de dados
        """
        if not self.area_selecionada:
            return "X.X.X.X.X"

        prefixo = self.AREAS_DECIPEX[self.area_selecionada]["prefixo"]

        try:
            # Tentar buscar código no CSV primeiro
            filtro = (
                (self.arquitetura.df['Macroprocesso'] == self.macro_selecionado) &
                (self.arquitetura.df['Processo'] == self.processo_selecionado) &
                (self.arquitetura.df['Subprocesso'] == self.subprocesso_selecionado) &
                (self.arquitetura.df['Atividade'] == self.atividade_selecionada)
            )
            linha = self.arquitetura.df[filtro]

            if 'Codigo' in self.arquitetura.df.columns and not linha.empty:
                codigo_csv = linha['Codigo'].iloc[0]
                # Validar se código não está duplicado no banco
                if not self._codigo_existe_no_banco(codigo_csv):
                    return codigo_csv
            elif 'codigo' in self.arquitetura.df.columns and not linha.empty:
                codigo_csv = linha['codigo'].iloc[0]
                if not self._codigo_existe_no_banco(codigo_csv):
                    return codigo_csv
        except:
            pass

        # Gerar código baseado em índices
        try:
            macros = self.arquitetura.obter_macroprocessos_unicos()
            idx_macro = macros.index(self.macro_selecionado) + 1 if self.macro_selecionado in macros else 1

            processos = self.arquitetura.obter_processos_por_macro(self.macro_selecionado)
            idx_processo = processos.index(self.processo_selecionado) + 1 if self.processo_selecionado in processos else 1

            subprocessos = self.arquitetura.obter_subprocessos_por_processo(self.macro_selecionado, self.processo_selecionado)
            idx_subprocesso = subprocessos.index(self.subprocesso_selecionado) + 1 if self.subprocesso_selecionado in subprocessos else 1

            atividades = self.arquitetura.obter_atividades_por_subprocesso(self.macro_selecionado, self.processo_selecionado, self.subprocesso_selecionado)
            idx_atividade = atividades.index(self.atividade_selecionada) + 1 if self.atividade_selecionada in atividades else 1

            codigo_base = f"{prefixo}.{idx_macro}.{idx_processo}.{idx_subprocesso}.{idx_atividade}"

            # Validar se código já existe, incrementar se necessário
            codigo_final = codigo_base
            sufixo = 1
            while self._codigo_existe_no_banco(codigo_final):
                # Adicionar sufixo para evitar duplicata
                codigo_final = f"{codigo_base}-{sufixo}"
                sufixo += 1
                if sufixo > 50:  # Limite de segurança
                    break

            return codigo_final
        except:
            return f"{prefixo}.1.1.1.1"

    def _codigo_existe_no_banco(self, codigo):
        """Verifica se código já existe no banco de dados"""
        try:
            from ..models import POP
            return POP.objects.filter(
                codigo_processo=codigo,
                is_deleted=False
            ).exists()
        except:
            # Se houver erro na consulta, não bloquear a geração
            return False

    def _preencher_arquitetura_completa(self, sugestao):
        """Preenche todos os campos da arquitetura de uma vez (Helena Ajuda Inteligente)"""
        print(f"[HELENA-AJUDA] Preenchendo arquitetura completa: {sugestao}")

        # Preencher todos os campos da arquitetura
        self.macro_selecionado = sugestao.get('macroprocesso', '')
        self.processo_selecionado = sugestao.get('processo', '')
        self.subprocesso_selecionado = sugestao.get('subprocesso', '')
        self.atividade_selecionada = sugestao.get('atividade', '')

        # Salvar nos dados
        self.dados["arquitetura"] = {
            "macroprocesso": self.macro_selecionado,
            "processo": self.processo_selecionado,
            "subprocesso": self.subprocesso_selecionado,
            "atividade": self.atividade_selecionada
        }

        self.dados["nome_processo"] = self.atividade_selecionada
        self.dados["processo_especifico"] = self.processo_selecionado

        # Gerar código
        codigo_gerado = self._gerar_codigo_processo()
        self.dados["codigo_arquitetura"] = codigo_gerado

        # Resultado final sugerido - SALVAR AUTOMATICAMENTE
        resultado_sugerido = sugestao.get('resultado_final', '')
        self.dados["entrega_esperada"] = resultado_sugerido

        # Mudar estado para "sistemas" (pular o resultado final, já foi preenchido)
        self.estado = "sistemas"

        # Retornar mensagem de sucesso + interface de sistemas
        return {
            "resposta": f"Perfeito! Preenchemos toda a arquitetura e geramos o CPF do seu processo (código na arquitetura):\n\n📋 Macroprocesso: {self.macro_selecionado}\n📋 Processo: {self.processo_selecionado}\n📋 Subprocesso: {self.subprocesso_selecionado}\n📋 Atividade: {self.atividade_selecionada}\n📋 Código: {codigo_gerado}\n🎯 Resultado Final: {resultado_sugerido}\n\n✅ Parabéns, essa etapa é muito importante!\n\nAgora me conta: quais sistemas você utiliza nessa atividade?",
            "tipo_interface": "sistemas",
            "dados_interface": {"sistemas_por_categoria": self.SISTEMAS_DECIPEX},
            "dados_extraidos": {
                "area": self.AREAS_DECIPEX[self.area_selecionada],
                "macroprocesso": self.macro_selecionado,
                "processo": self.processo_selecionado,
                "processo_especifico": self.processo_selecionado,
                "subprocesso": self.subprocesso_selecionado,
                "atividade": self.atividade_selecionada,
                "nome_processo": self.atividade_selecionada,
                "codigo_processo": codigo_gerado,
                "entrega_esperada": resultado_sugerido
            },
            "conversa_completa": False,
            "progresso": self._calcular_progresso(),
            "proximo_estado": "sistemas"
        }

    def _gerar_dados_completos_pop(self):
        """Organiza todos os dados coletados"""
        return {
            "nome_usuario": self.nome_usuario,
            "area": self.dados.get("area", {}),
            "macroprocesso": self.macro_selecionado,
            "sistemas": self.dados.get("sistemas", []),
            "codigo_processo": self._gerar_codigo_processo(),
            "nome_processo": self.dados.get("nome_processo", ""),
            "processo_especifico": self.dados.get("processo_especifico", ""),
            "entrega_esperada": self.dados.get("entrega_esperada", ""),
            "operadores": self.dados.get("operadores", ""),
            "dispositivos_normativos": self.dados.get("dispositivos_normativos", ""),
            "documentos_utilizados": self.dados.get("documentos_utilizados", []),
            "pontos_atencao": self.dados.get("pontos_atencao", ""),
            "etapas": self.etapas_processo,
            "fluxos_entrada": self.fluxos_entrada,
            "fluxos_saida": self.fluxos_saida,
            "data_criacao": datetime.now().strftime("%d/%m/%Y %H:%M")
        }

    def _gerar_pop_completo(self):
        """Gera documento POP formatado - RETORNA DICT para PDFGenerator"""
        return self._gerar_dados_completos_pop()

    def _calcular_progresso(self):
        """Calcula progresso atual da conversa"""
        total_etapas = 10
        etapas_concluidas = 0
        
        if self.nome_usuario:
            etapas_concluidas += 1
        if self.area_selecionada:
            etapas_concluidas += 1
        if self.sistemas_selecionados is not None:
            etapas_concluidas += 1
        
        etapas_concluidas += self.etapa_atual_campo
        
        if self.documentos_processo:
            etapas_concluidas += 1
        if self.etapas_processo:
            etapas_concluidas += 1
        if hasattr(self, 'fluxos_entrada'):
            etapas_concluidas += 1
        if self.estado == "revisao":
            etapas_concluidas = 10
            
        return f"{min(etapas_concluidas, total_etapas)}/10"

    def _obter_estado_atual(self):
        """Obtém descrição textual do estado atual"""
        if self.aguardando_operadores_etapa:
            return "aguardando_operadores_etapa"
        elif self.aguardando_pergunta_condicionais:
            return "aguardando_pergunta_condicionais"  
        elif self.aguardando_condicionais:
            return "aguardando_condicionais"
        elif self.aguardando_detalhes:
            return "aguardando_detalhes"
        else:
            return "aguardando_etapa"

    def _criar_resposta_com_tempo_real(self, resposta_padrao):
        """Cria resposta com interface tempo real quando modo ativo, senão resposta padrão"""
        if not self.modo_tempo_real:
            return resposta_padrao
            
        # Adicionar dados tempo real à resposta padrão
        resposta_padrao["dados_tempo_real"] = {
            "etapas": getattr(self, 'etapas_processo', []),
            "etapa_atual": {
                "numero": len(getattr(self, 'etapas_processo', [])) + 1 if hasattr(self, 'etapa_temporaria') and self.etapa_temporaria else None,
                "descricao": getattr(self, 'etapa_temporaria', None),
                "detalhes": getattr(self, 'detalhes_etapa_atual', []),
                "operador": getattr(self, 'operadores_etapa_atual', [None])[0] if getattr(self, 'operadores_etapa_atual', []) else None
            },
            "estado": self._obter_estado_atual()
        }
        
        # Se está no estado de etapas, usar interface tempo real
        if (self.estado == "etapas" or self.aguardando_operadores_etapa or 
            self.aguardando_pergunta_condicionais or self.aguardando_condicionais or 
            self.aguardando_detalhes):
            resposta_padrao["tipo_interface"] = "etapas_tempo_real"
            resposta_padrao["dados_interface"] = resposta_padrao["dados_tempo_real"]
            
        return resposta_padrao

    def _erro_estado(self):
        """Retorna erro de estado"""
        return {
            "resposta": "Ops! Algo deu errado. Vamos recomeçar?",
            "tipo_interface": "texto",
            "dados_interface": {},
            "dados_extraidos": {},
            "conversa_completa": False,
            "progresso": self._calcular_progresso(),
            "proximo_estado": "nome"
        }

    def obter_dados_pop(self):
        """Retorna dados coletados para o formulário"""
        return self._gerar_dados_completos_pop()

    def obter_progresso(self):
        """Retorna detalhes do progresso atual"""
        dados = self._gerar_dados_completos_pop()
        campos_preenchidos = sum(1 for k, v in dados.items() if v and k != "data_criacao")
        
        return {
            "campos_preenchidos": campos_preenchidos,
            "total_campos": 10,
            "percentual": int((campos_preenchidos / 10) * 100),
            "estado_atual": self.estado,
            "completo": self.estado == "revisao"
        }

    def reiniciar_conversa(self):
        """Reinicia a conversa do zero"""
        self.__init__()
        
    def obter_codigo_gerado(self):
        """Retorna o código gerado para o processo"""
        return self._gerar_codigo_processo()