from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
import os
import json
import re
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd

# Import absoluto correto - SEM PONTO
from processos.utils import BaseLegalSuggestor

# ============================================================================
# CLASSE ARQUITETURA DECIPEX
# ============================================================================

class ArquiteturaDecipex:
    """Carrega e consulta arquitetura de processos da DECIPEX"""
    
    def __init__(self, caminho_csv='documentos_teste/Arquitetura_DECIPEX_mapeada.csv'):
        try:
            self.df = pd.read_csv(caminho_csv)
        except FileNotFoundError:
            print(f"⚠️  Arquivo CSV não encontrado: {caminho_csv}")
            self.df = pd.DataFrame(columns=['Macroprocesso', 'Processo', 'Subprocesso', 'Atividade'])
        except Exception as e:
            print(f"❌ Erro ao carregar CSV: {e}")
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
        self.fluxos_entrada = []
        self.fluxos_saida = []
        self.etapa_atual_campo = 0
        self.conversas = []
        
        # Carregar dados da arquitetura
        self.arquitetura = ArquiteturaDecipex()
        
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
                "nome": "operadores",
                "pergunta": "Quem são os responsáveis por executar esta atividade?",
                "exemplo": "Ex: Técnico Especializado, Coordenador, Apoio-gabinete"
            },
            {
                "nome": "pontos_atencao",
                "pergunta": "Há algum ponto especial de atenção ou cuidado nesta atividade?",
                "exemplo": "Ex: Auditar situação desde centralização, Observar prazos de retroatividade"
            }
        ]

    @property
    def AREAS_DECIPEX(self):
        return {
            1: {"codigo": "CGBEN", "nome": "Coordenação de Benefícios", "prefixo": "1"},
            2: {"codigo": "CGPAG", "nome": "Coordenação de Pagamentos", "prefixo": "2"},
            3: {"codigo": "COATE", "nome": "Coordenação de Atendimento", "prefixo": "3"},
            4: {"codigo": "CGGAF", "nome": "Coordenação de Gestão Administrativa", "prefixo": "4"},
            5: {"codigo": "DIGEP", "nome": "Diretoria de Pessoal dos Ex-Territórios", "prefixo": "5"},
            6: {"codigo": "CGRIS", "nome": "Coordenação de Riscos", "prefixo": "6"},
            7: {"codigo": "CGCAF", "nome": "Coordenação de Cadastro Funcional", "prefixo": "7"},
            8: {"codigo": "CGECO", "nome": "Coordenação de Convênios", "prefixo": "8"}
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
            self.conversas.append({
                "usuario": mensagem, 
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
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
            elif self.estado == "etapas":
                return self._processar_etapas(mensagem)
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

    def _processar_nome(self, mensagem):
        """Captura nome inicial do usuário"""
        msg_limpa = mensagem.strip()
        
        # Aceitar qualquer nome não vazio com pelo menos 2 caracteres
        if len(msg_limpa) >= 2:
            palavras = msg_limpa.split()
            self.nome_temporario = palavras[0].capitalize()
            self.estado = "confirma_nome"
            
            return {
                "resposta": f"Olá {self.nome_temporario}, prazer em te conhecer. Antes de continuarmos, me confirma, posso te chamar de {self.nome_temporario} mesmo? (Digite SIM ou NÃO)",
                "tipo_interface": "texto",
                "dados_interface": {},
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": "0/10",
                "proximo_estado": "confirma_nome"
            }
        else:
            return {
                "resposta": "Olá! Sou a Helena, assistente da DECIPEX para mapeamento de processos. Como você gostaria de ser chamado?",
                "tipo_interface": "texto",
                "dados_interface": {},
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": "0/10",
                "proximo_estado": "nome"
            }

    def _processar_confirma_nome(self, mensagem):
        """Confirma se o nome capturado está correto - aceita apenas SIM ou NÃO"""
        resposta_lower = mensagem.lower().strip()
        
        # Lista de respostas positivas (SIM)
        respostas_positivas = ["sim", "s", "yes", "uhum", "aham", "isso"]
        
        # Lista de respostas negativas (NÃO)
        respostas_negativas = ["não", "nao", "no", "n"]
        
        if resposta_lower in respostas_positivas:
            # Confirmar nome e avançar
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
        
        elif resposta_lower in respostas_negativas:
            # Voltar a perguntar o nome
            self.nome_temporario = ""
            self.estado = "nome"
            
            return {
                "resposta": "Sem problemas! Como você gostaria de ser chamado?",
                "tipo_interface": "texto",
                "dados_interface": {},
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": "0/10",
                "proximo_estado": "nome"
            }
        
        else:
            # Não entendeu - dar segunda chance
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
                "resposta": f"Nesse chat eu vou conduzir uma conversa guiada. A intenção é preencher esse formulário de Procedimento Operacional Padrão - POP aí do lado. Tá vendo? Aproveita pra conhecer.\n\nNossa meta juntas é entregar isso prontinho! Tá pronta pra continuar? Se estiver, digite sim.",
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
                "resposta": f"Mas olha, se ao olhar o formulário você pensou 'nossa, eu não sei definir um desses campos!' quero te tranquilizar: se você travar na hora de responder qualquer pergunta, clica no botão vermelho 'Preciso de Ajuda' e abre um espaço de bate-papo livre, sem formulário.\n\nVocê me conta sua angústia e eu te ajudo a refinar a resposta pro formulário. Em seguida voltamos pra cá.\n\nCombinado?",
                "tipo_interface": "texto",
                "dados_interface": {},
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": "1/10",
                "proximo_estado": "explicacao_final"
            }
        else:
            return {
                "resposta": f"Tudo bem! Só posso seguir quando você me disser 'sim', {nome_exibir}. Quando estiver pronta, é só me dizer.",
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
                # Editar operadores
                self.editando_campo = "operadores"
                self.etapa_atual_campo = 4
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
            
            elif campo_num == 7:
                # Editar pontos de atenção
                self.editando_campo = "pontos_atencao"
                self.etapa_atual_campo = 5
                self.estado = "campos"
                valor_atual = self.dados.get("pontos_atencao", "")
                return {
                    "resposta": f"Valor atual: {valor_atual}\n\nHá algum ponto especial de atenção ou cuidado nesta atividade?",
                    "tipo_interface": "texto",
                    "dados_interface": {},
                    "dados_extraidos": {},
                    "conversa_completa": False,
                    "progresso": "10/10",
                    "proximo_estado": "campos"
                }
            
            elif campo_num == 8:
                # Editar documentos
                self.editando_campo = "documentos_utilizados"
                self.documentos_processo = []
                self.aguardando_tipo_documento = False
                self.documento_temporario = ""
                self.estado = "documentos"
                return {
                    "resposta": f"Vamos redefinir os documentos. Liste o documento 1:",
                    "tipo_interface": "texto",
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
                        "dados_extraidos": {"area": self.AREAS_DECIPEX[area_id]},
                        "conversa_completa": False,
                        "progresso": "10/10",
                        "proximo_estado": "revisao"
                    }
                
                # Fluxo normal
                self.estado = "arquitetura"
                
                return {
                    "resposta": f"Perfeito! Você trabalha na {self.AREAS_DECIPEX[area_id]['nome']}. Agora vamos localizar seu processo na arquitetura da DECIPEX. Primeiro, qual é o macroprocesso?",
                    "tipo_interface": "dropdown_macro",
                    "dados_interface": {
                        "opcoes": self.arquitetura.obter_macroprocessos_unicos(),
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
        
        print(f"🔵 ARQUITETURA: Mensagem='{mensagem}'")
        print(f"🔵 ARQUITETURA: Macro={self.macro_selecionado}")
        print(f"🔵 ARQUITETURA: Processo={self.processo_selecionado}")
        print(f"🔵 ARQUITETURA: Subprocesso={self.subprocesso_selecionado}")
        
        if not self.macro_selecionado:
            self.macro_selecionado = mensagem.strip()
            processos = self.arquitetura.obter_processos_por_macro(self.macro_selecionado)
            
            return {
                "resposta": f"Macroprocesso: {self.macro_selecionado}. Agora selecione o processo:",
                "tipo_interface": "dropdown_processo",
                "dados_interface": {"opcoes": processos},
                "dados_extraidos": {"macroprocesso": self.macro_selecionado},
                "conversa_completa": False,
                "progresso": self._calcular_progresso(),
                "proximo_estado": "arquitetura"
            }
        
        elif not self.processo_selecionado:
            self.processo_selecionado = mensagem.strip()
            subprocessos = self.arquitetura.obter_subprocessos_por_processo(
                self.macro_selecionado, self.processo_selecionado
            )
            
            print(f"🟡 Subprocessos encontrados: {len(subprocessos)} itens")
            print(f"🟡 Lista: {subprocessos[:3] if subprocessos else 'VAZIA'}")
            
            if not subprocessos or len(subprocessos) == 0:
                print("⚠️ Nenhum subprocesso encontrado! Pulando para atividade...")
                self.subprocesso_selecionado = "Não informado"
                
                atividades = self.arquitetura.obter_atividades_por_subprocesso(
                    self.macro_selecionado, self.processo_selecionado, "Não informado"
                )
                
                return {
                    "resposta": f"Processo: {self.processo_selecionado}. Não encontrei subprocessos no CSV. Selecione a atividade:",
                    "tipo_interface": "dropdown_atividade",
                    "dados_interface": {"opcoes": atividades if atividades else []},
                    "dados_extraidos": {"processo": self.processo_selecionado},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "arquitetura"
                }
            
            return {
                "resposta": f"Processo: {self.processo_selecionado}. Agora selecione o subprocesso:",
                "tipo_interface": "dropdown_subprocesso",
                "dados_interface": {"opcoes": subprocessos},
                "dados_extraidos": {"processo": self.processo_selecionado},
                "conversa_completa": False,
                "progresso": self._calcular_progresso(),
                "proximo_estado": "arquitetura"
            }
        
        elif not self.subprocesso_selecionado:
            self.subprocesso_selecionado = mensagem.strip()
            atividades = self.arquitetura.obter_atividades_por_subprocesso(
                self.macro_selecionado, self.processo_selecionado, self.subprocesso_selecionado
            )
            
            return {
                "resposta": f"Subprocesso: {self.subprocesso_selecionado}. Agora selecione a atividade:",
                "tipo_interface": "dropdown_atividade",
                "dados_interface": {"opcoes": atividades},
                "dados_extraidos": {"subprocesso": self.subprocesso_selecionado},
                "conversa_completa": False,
                "progresso": self._calcular_progresso(),
                "proximo_estado": "arquitetura"
            }
        
        else:
            self.atividade_selecionada = mensagem.strip()
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
            
            return {
                "resposta": f"Perfeito! Mapeamos sua atividade: {self.atividade_selecionada}.\n\nAgora já temos Macroprocesso, Processo e Subprocesso. Ufa, muita coisa! Mas agora precisamos definir o Resultado final da atividade. Aquilo que entrega resultado e podemos entender é onde se encerra o processo.\n\nPode ser, por exemplo: Auxílio concedido, Requerimento analisado e decidido, Cadastro atualizado, Irregularidade apurada, Pagamento corrigido, Formulário protocolado.\n\nQual é o resultado final desta atividade?",
                "tipo_interface": "texto",
                "dados_interface": {},
                "dados_extraidos": {
                    "arquitetura": self.dados["arquitetura"],
                    "nome_processo": self.atividade_selecionada,
                    "processo_especifico": self.processo_selecionado,
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
        
        print(f"🟢 SISTEMAS PROCESSADOS: Estado agora é '{self.estado}'")
        print(f"🟢 SISTEMAS: {self.sistemas_selecionados}")
        
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
        print(f"🟡 PROCESSAR CAMPOS")
        print(f"   Etapa atual: {self.etapa_atual_campo}/{len(self.campos_principais)}")
        
        if self.etapa_atual_campo < len(self.campos_principais):
            campo_atual = self.campos_principais[self.etapa_atual_campo]
            print(f"   Campo atual: {campo_atual['nome']}")
        
        print(f"{'='*80}\n")
        
        if self.etapa_atual_campo < len(self.campos_principais):
            campo_atual = self.campos_principais[self.etapa_atual_campo]
            
            msg_lower = mensagem.lower().strip()
            
            respostas_invalidas = [
                "não sei", "nao sei", "não tenho certeza", "nao tenho certeza",
                "help", "ajuda", "?", "não", "nao",
                "nenhum", "nenhuma", "vazio", "em branco"
            ]
            
            if msg_lower in respostas_invalidas or len(mensagem.strip()) < 3:
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
                        "proximo_estado": "campos"
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
                self.estado = "documentos"
                return {
                    "resposta": f"Perfeito! Agora vamos listar os DOCUMENTOS, FORMULÁRIOS E MODELOS UTILIZADOS E GERADOS NA ATIVIDADE.\n\nListe o documento 1:",
                    "tipo_interface": "texto",
                    "dados_interface": {},
                    "dados_extraidos": {campo_atual["nome"]: self.dados[campo_atual["nome"]]},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "documentos"
                }
        else:
            return self._erro_estado()

    def _processar_documentos(self, mensagem):
        """Processa coleta iterativa de documentos"""
        resposta_lower = mensagem.lower().strip()
        
        if resposta_lower in ["não", "nao", "não há mais", "não ha mais", "fim", "finalizar"]:
            if self.documentos_processo:
                self.dados["documentos_utilizados"] = self.documentos_processo
                
                # Se está editando documentos, voltar para revisão
                if self.editando_campo == "documentos_utilizados":
                    self.editando_campo = None
                    self.estado = "revisao"
                    return {
                        "resposta": f"Documentos atualizados! Aqui está o resumo:",
                        "tipo_interface": "revisao",
                        "dados_interface": {
                            "dados_completos": self._gerar_dados_completos_pop(),
                            "codigo_gerado": self._gerar_codigo_processo()
                        },
                        "dados_extraidos": {"documentos_utilizados": self.documentos_processo},
                        "conversa_completa": False,
                        "progresso": "10/10",
                        "proximo_estado": "revisao"
                    }
                
                # Fluxo normal
                self.estado = "etapas"
                return {
                    "resposta": f"Ótimo! Agora vamos mapear as etapas do processo. Descreva a primeira etapa desta atividade:",
                    "tipo_interface": "texto",
                    "dados_interface": {},
                    "dados_extraidos": {"documentos_utilizados": self.documentos_processo},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "etapas"
                }
            else:
                return {
                    "resposta": "Você precisa informar pelo menos um documento. Qual o primeiro documento necessário?",
                    "tipo_interface": "texto",
                    "dados_interface": {},
                    "dados_extraidos": {},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "documentos"
                }
        
        if len(self.documentos_processo) == 0:
            self.documentos_processo.append(mensagem.strip())
            return {
                "resposta": f"Documento registrado: {mensagem[:60]}{'...' if len(mensagem) > 60 else ''}\n\nHá outro documento necessário? (Digite o próximo documento ou 'não' para finalizar)",
                "tipo_interface": "texto",
                "dados_interface": {},
                "dados_extraidos": {"documento_adicionado": mensagem.strip()},
                "conversa_completa": False,
                "progresso": self._calcular_progresso(),
                "proximo_estado": "documentos"
            }
        else:
            self.documentos_processo.append(mensagem.strip())
            return {
                "resposta": f"Documento registrado: {mensagem[:60]}{'...' if len(mensagem) > 60 else ''}\n\nHá outro documento? (Digite o próximo documento ou 'não' para finalizar)",
                "tipo_interface": "texto",
                "dados_interface": {},
                "dados_extraidos": {"documento_adicionado": mensagem.strip()},
                "conversa_completa": False,
                "progresso": self._calcular_progresso(),
                "proximo_estado": "documentos"
            }

    def _processar_etapas(self, mensagem):
        """Processa coleta dinâmica de etapas com detalhamento hierárquico"""
        resposta_lower = mensagem.lower().strip()
        
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
                    
                    # Fluxo normal
                    self.estado = "fluxos"
                    return {
                        "resposta": "Ótimo! Agora vou perguntar sobre os fluxos de trabalho. Seu processo recebe insumos de outra área da DECIPEX?",
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
                        "dados_extraidos": {"etapas": self.etapas_processo},
                        "conversa_completa": False,
                        "progresso": self._calcular_progresso(),
                        "proximo_estado": "fluxos"
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
            
            return {
                "resposta": f"Etapa registrada: {mensagem[:60]}{'...' if len(mensagem) > 60 else ''}\n\nVamos detalhar essa etapa. Qual o primeiro detalhe/passo?",
                "tipo_interface": "texto",
                "dados_interface": {},
                "dados_extraidos": {},
                "conversa_completa": False,
                "progresso": self._calcular_progresso(),
                "proximo_estado": "etapas"
            }
        
        else:
            if resposta_lower in ["não", "nao", "não há mais", "fim"]:
                numero_etapa = len(self.etapas_processo) + 1
                etapa = {
                    "numero": numero_etapa,
                    "descricao": self.etapa_temporaria,
                    "detalhes": self.detalhes_etapa_atual
                }
                self.etapas_processo.append(etapa)
                
                self.aguardando_detalhes = False
                self.detalhes_etapa_atual = []
                
                return {
                    "resposta": f"Etapa {numero_etapa} completa com {len(etapa['detalhes'])} detalhes!\n\nHá mais alguma etapa? (Digite a próxima etapa ou 'não' para finalizar)",
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
        """Gera código baseado na área e estrutura hierárquica"""
        if not self.area_selecionada:
            return "X.X.X.X"
        
        prefixo = self.AREAS_DECIPEX[self.area_selecionada]["prefixo"]
        
        try:
            filtro = (
                (self.arquitetura.df['Macroprocesso'] == self.macro_selecionado) &
                (self.arquitetura.df['Processo'] == self.processo_selecionado) &
                (self.arquitetura.df['Subprocesso'] == self.subprocesso_selecionado) &
                (self.arquitetura.df['Atividade'] == self.atividade_selecionada)
            )
            linha = self.arquitetura.df[filtro]
            
            if 'Codigo' in self.arquitetura.df.columns and not linha.empty:
                return linha['Codigo'].iloc[0]
            elif 'codigo' in self.arquitetura.df.columns and not linha.empty:
                return linha['codigo'].iloc[0]
        except:
            pass
        
        try:
            macros = self.arquitetura.obter_macroprocessos_unicos()
            idx_macro = macros.index(self.macro_selecionado) + 1 if self.macro_selecionado in macros else 1
            
            processos = self.arquitetura.obter_processos_por_macro(self.macro_selecionado)
            idx_processo = processos.index(self.processo_selecionado) + 1 if self.processo_selecionado in processos else 1
            
            subprocessos = self.arquitetura.obter_subprocessos_por_processo(self.macro_selecionado, self.processo_selecionado)
            idx_subprocesso = subprocessos.index(self.subprocesso_selecionado) + 1 if self.subprocesso_selecionado in subprocessos else 1
            
            atividades = self.arquitetura.obter_atividades_por_subprocesso(self.macro_selecionado, self.processo_selecionado, self.subprocesso_selecionado)
            idx_atividade = atividades.index(self.atividade_selecionada) + 1 if self.atividade_selecionada in atividades else 1
            
            return f"{prefixo}.{idx_macro}.{idx_processo}.{idx_subprocesso}.{idx_atividade}"
        except:
            return f"{prefixo}.1.1.1"

    def _gerar_dados_completos_pop(self):
        """Organiza todos os dados coletados"""
        return {
            "nome_usuario": self.nome_usuario,
            "area": self.dados.get("area", {}),
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