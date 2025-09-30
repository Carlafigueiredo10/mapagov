from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
import os
import json
import re
from datetime import datetime
from typing import List, Dict, Any
from processos.utils import BaseLegalSuggestor

class HelenaPOP:
    """Helena para mapeamento de POPs - versão completa integrada à DECIPEX"""
    
    def __init__(self):
        # LLM e RAG desabilitados para melhor performance
        self.vectorstore = None
        
        # Estados da conversa
        self.estado = "nome"  # nome -> area -> sistemas -> campos -> etapas -> fluxos -> revisao
        self.dados = {}
        self.nome_usuario = None
        self.area_selecionada = None
        self.sistemas_selecionados = []
        self.etapas_processo = []
        self.fluxos_entrada = []
        self.fluxos_saida = []
        self.etapa_atual_campo = 0
        self.conversas = []
        
        # ============ NOVA LINHA: INTEGRAÇÃO BASE LEGAL ============
        self.suggestor_base_legal = BaseLegalSuggestor()
        # ============================================================
        
        # Campos principais a coletar (após área e sistemas)
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
                "nome": "operadores",
                "pergunta": "Quem são os responsáveis por executar esta atividade?",
                "exemplo": "Ex: Técnico Especializado, Coordenador, Apoio-gabinete"
            },
            {
                "nome": "dispositivos_normativos",
                "pergunta": "Quais são as principais normas que regulam esta atividade?",
                "exemplo": "Ex: Art. 34 da IN SGP/SEDGG/ME nº 97/2022, Lei 8.112/90"
            },
            {
                "nome": "documentos_utilizados",
                "pergunta": "Quais documentos são necessários para executar esta atividade?",
                "exemplo": "Ex: Requerimento SIGEPE, Documentos pessoais, Comprovantes de pagamento"
            },
            {
                "nome": "pontos_atencao",
                "pergunta": "Há algum ponto especial de atenção ou cuidado nesta atividade?",
                "exemplo": "Ex: Auditar situação desde centralização, Observar prazos de retroatividade"
            }
        ]

    # =============================================================================
    # ESTRUTURAS DE DADOS DECIPEX
    # =============================================================================

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

    # =============================================================================
    # MÉTODO PRINCIPAL DE PROCESSAMENTO
    # =============================================================================

    def processar_mensagem(self, mensagem):
        """Processa mensagem do usuário de acordo com o estado atual"""
        try:
            # CORREÇÃO: Converter datetime para string antes de salvar
            self.conversas.append({
                "usuario": mensagem, 
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            if self.estado == "nome":
                return self._processar_nome(mensagem)
            elif self.estado == "area":
                return self._processar_area(mensagem)
            elif self.estado == "sistemas":
                return self._processar_sistemas(mensagem)
            elif self.estado == "campos":
                return self._processar_campos(mensagem)
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

    # =============================================================================
    # PROCESSAMENTO POR ESTADO
    # =============================================================================

    def _processar_nome(self, mensagem):
        """Processa nome do usuário"""
        palavras = mensagem.strip().split()
        if 1 <= len(palavras) <= 3 and all(len(p) > 1 for p in palavras):
            self.nome_usuario = palavras[0].capitalize()
            self.estado = "area"
            
            return {
                "resposta": f"Prazer, {self.nome_usuario}! Vamos mapear seu processo da DECIPEX. Em qual área você trabalha?",
                "tipo_interface": "areas",
                "dados_interface": {
                    "opcoes_areas": self.AREAS_DECIPEX,
                    "titulo": "Selecione sua área na DECIPEX"
                },
                "dados_extraidos": {"nome_usuario": self.nome_usuario},
                "conversa_completa": False,
                "progresso": self._calcular_progresso(),
                "proximo_estado": "area"
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

    def _processar_area(self, mensagem):
        """Processa seleção de área"""
        try:
            area_id = int(mensagem.strip())
            if area_id in self.AREAS_DECIPEX:
                self.area_selecionada = area_id
                self.dados["area"] = self.AREAS_DECIPEX[area_id]
                self.estado = "sistemas"
                
                return {
                    "resposta": f"Perfeito! Você trabalha na {self.AREAS_DECIPEX[area_id]['nome']}. Agora me diga: quais sistemas você utiliza neste processo?",
                    "tipo_interface": "sistemas",
                    "dados_interface": {
                        "sistemas_por_categoria": self.SISTEMAS_DECIPEX,
                        "area_contexto": self.AREAS_DECIPEX[area_id]['nome'],
                        "multipla_selecao": True
                    },
                    "dados_extraidos": {"area": self.AREAS_DECIPEX[area_id]},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "sistemas"
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

    def _processar_sistemas(self, mensagem):
        """Processa seleção de sistemas"""
        # Processar lista de sistemas selecionados
        sistemas_texto = mensagem.strip()
        
        if sistemas_texto.lower() in ["não sei", "nenhum", "não utilizo"]:
            self.sistemas_selecionados = []
        else:
            # Extrair sistemas da mensagem
            todos_sistemas = []
            for categoria in self.SISTEMAS_DECIPEX.values():
                todos_sistemas.extend(categoria)
            
            sistemas_encontrados = []
            for sistema in todos_sistemas:
                if sistema.lower() in sistemas_texto.lower():
                    sistemas_encontrados.append(sistema)
            
            self.sistemas_selecionados = sistemas_encontrados

        self.dados["sistemas"] = self.sistemas_selecionados
        self.estado = "campos"
        
        primeiro_campo = self.campos_principais[0]
        resposta_sistemas = f"Sistemas registrados: {', '.join(self.sistemas_selecionados) if self.sistemas_selecionados else 'Nenhum sistema específico'}.\n\n"
        
        return {
            "resposta": f"{resposta_sistemas}{primeiro_campo['pergunta']} {primeiro_campo['exemplo']}",
            "tipo_interface": "texto",
            "dados_interface": {},
            "dados_extraidos": {"sistemas": self.sistemas_selecionados},
            "conversa_completa": False,
            "progresso": self._calcular_progresso(),
            "proximo_estado": "campos"
        }

    def _processar_campos(self, mensagem):
        """Processa coleta de campos principais"""
        if self.etapa_atual_campo < len(self.campos_principais):
            campo_atual = self.campos_principais[self.etapa_atual_campo]
            
            # Verificar se usuário não sabe
            if mensagem.lower().strip() in ["não sei", "não tenho certeza", "help", "ajuda"]:
                return self._consultar_rag_exemplos(campo_atual["nome"])
            
            # Salvar resposta
            self.dados[campo_atual["nome"]] = mensagem.strip()
            self.etapa_atual_campo += 1
            
            # Verificar se há próximo campo
            if self.etapa_atual_campo < len(self.campos_principais):
                proximo_campo = self.campos_principais[self.etapa_atual_campo]
                
                # ============ NOVA LÓGICA: SUGESTÃO DE BASE LEGAL ============
                # Se o próximo campo for dispositivos normativos, sugerir base legal
                if proximo_campo["nome"] == "dispositivos_normativos":
                    sugestoes = self._sugerir_base_legal_contextual()
                    
                    if sugestoes:
                        sugestoes_texto = self._formatar_sugestoes_base_legal(sugestoes)
                        resposta = f"Anotado! {mensagem[:50]}{'...' if len(mensagem) > 50 else ''}\n\n{proximo_campo['pergunta']}\n\n{sugestoes_texto}"
                    else:
                        resposta = f"Anotado! {mensagem[:50]}{'...' if len(mensagem) > 50 else ''}\n\n{proximo_campo['pergunta']} {proximo_campo['exemplo']}"
                else:
                    # Campos normais sem sugestão
                    resposta = f"Anotado! {mensagem[:50]}{'...' if len(mensagem) > 50 else ''}\n\n{proximo_campo['pergunta']} {proximo_campo['exemplo']}"
                # ============================================================
                
                return {
                    "resposta": resposta,
                    "tipo_interface": "texto",
                    "dados_interface": {},
                    "dados_extraidos": {campo_atual["nome"]: mensagem.strip()},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "campos"
                }
            else:
                # Transição para etapas
                self.estado = "etapas"
                return {
                    "resposta": f"Perfeito! Agora vamos mapear as etapas do processo. Descreva a primeira etapa desta atividade:",
                    "tipo_interface": "texto",
                    "dados_interface": {},
                    "dados_extraidos": {campo_atual["nome"]: mensagem.strip()},
                    "conversa_completa": False,
                    "progresso": self._calcular_progresso(),
                    "proximo_estado": "etapas"
                }
        else:
            return self._erro_estado()

    def _processar_etapas(self, mensagem):
        """Processa coleta dinâmica de etapas"""
        resposta_lower = mensagem.lower().strip()
        
        # Comandos especiais para gerenciamento de etapas
        if resposta_lower in ["não", "nao", "não há mais", "fim", "finalizar"]:
            if self.etapas_processo:
                self.dados["etapas"] = self.etapas_processo
                self.estado = "fluxos"
                return {
                    "resposta": "Ótimo! Agora vou perguntar sobre os fluxos de trabalho. Seu processo recebe insumos de outra área da DECIPEX?",
                    "tipo_interface": "fluxos_entrada",
                    "dados_interface": {
                        "opcoes_areas": {k: v for k, v in self.AREAS_DECIPEX.items() if k != self.area_selecionada},
                        "tipo_fluxo": "entrada"
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
        
        # Adicionar etapa
        numero_etapa = len(self.etapas_processo) + 1
        etapa = {
            "numero": numero_etapa,
            "descricao": mensagem.strip()
        }
        self.etapas_processo.append(etapa)
        
        return {
            "resposta": f"Etapa {numero_etapa} registrada: {mensagem[:60]}{'...' if len(mensagem) > 60 else ''}\n\nHá mais alguma etapa? (Digite a próxima etapa ou 'não' para finalizar)",
            "tipo_interface": "texto",
            "dados_interface": {},
            "dados_extraidos": {"etapa_adicionada": etapa},
            "conversa_completa": False,
            "progresso": self._calcular_progresso(),
            "proximo_estado": "etapas"
        }

    def _processar_fluxos(self, mensagem):
        """Processa fluxos entre áreas"""
        resposta_lower = mensagem.lower().strip()
        
        # Lógica simplificada para fluxos
        if resposta_lower in ["sim", "s", "há", "recebe"]:
            # Processar áreas de entrada (simulado)
            self.fluxos_entrada = ["CGPAG"]  # Exemplo
            return {
                "resposta": "Entendido! E seu processo entrega resultados para outra área da DECIPEX?",
                "tipo_interface": "fluxos_saida",
                "dados_interface": {
                    "opcoes_areas": {k: v for k, v in self.AREAS_DECIPEX.items() if k != self.area_selecionada},
                    "tipo_fluxo": "saida"
                },
                "dados_extraidos": {"fluxos_entrada": self.fluxos_entrada},
                "conversa_completa": False,
                "progresso": self._calcular_progresso(),
                "proximo_estado": "fluxos"
            }
        elif hasattr(self, '_processando_saida'):
            # Segunda pergunta de fluxos
            if resposta_lower in ["sim", "s", "há", "entrega"]:
                self.fluxos_saida = ["COATE"]  # Exemplo
            
            self.dados["fluxos_entrada"] = self.fluxos_entrada
            self.dados["fluxos_saida"] = self.fluxos_saida
            self.estado = "revisao"
            
            return {
                "resposta": f"Excelente, {self.nome_usuario}! Coletei todas as informações. Vou gerar o código do processo e mostrar um resumo para sua revisão.",
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
        else:
            # Primeira pergunta de fluxos - não recebe insumos
            self.fluxos_entrada = []
            self._processando_saida = True
            
            return {
                "resposta": "Entendido! E seu processo entrega resultados para outra área da DECIPEX?",
                "tipo_interface": "fluxos_saida",
                "dados_interface": {
                    "opcoes_areas": {k: v for k, v in self.AREAS_DECIPEX.items() if k != self.area_selecionada},
                    "tipo_fluxo": "saida"
                },
                "dados_extraidos": {"fluxos_entrada": self.fluxos_entrada},
                "conversa_completa": False,
                "progresso": self._calcular_progresso(),
                "proximo_estado": "fluxos"
            }

    def _processar_revisao(self, mensagem):
        """Processa revisão final"""
        resposta_lower = mensagem.lower().strip()
        
        if resposta_lower in ["gerar", "pdf", "finalizar", "ok", "está bom"]:
            # ============ ALTERAÇÃO: RETORNAR DICT AO INVÉS DE TEXTO ============
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
        else:
            return {
                "resposta": "O que você gostaria de editar? Posso ajustar qualquer informação.",
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

    # =============================================================================
    # NOVOS MÉTODOS: SUGESTÃO DE BASE LEGAL
    # =============================================================================

    def _sugerir_base_legal_contextual(self) -> List[Dict[str, Any]]:
        """Sugere base legal baseada no contexto coletado até agora"""
        try:
            # Montar contexto para sugestão
            contexto = {
                "nome_processo": self.dados.get("nome_processo", ""),
                "area_codigo": self.AREAS_DECIPEX.get(self.area_selecionada, {}).get("codigo", ""),
                "sistemas": self.sistemas_selecionados,
                "objetivo": self.dados.get("entrega_esperada", "")
            }
            
            # Chamar suggestor
            sugestoes = self.suggestor_base_legal.sugerir_base_legal(contexto)
            
            # Retornar top 3
            return sugestoes[:3]
            
        except Exception as e:
            print(f"Erro ao sugerir base legal: {e}")
            return []

    def _formatar_sugestoes_base_legal(self, sugestoes: List[Dict[str, Any]]) -> str:
        """Formata sugestões de base legal para exibição"""
        if not sugestoes:
            return ""
        
        texto = "💡 **Baseado no seu processo, encontrei estas normas relevantes:**\n\n"
        
        for i, sugestao in enumerate(sugestoes, 1):
            confianca = sugestao.get('confianca', 0)
            icone_confianca = "🟢" if confianca > 80 else "🟡" if confianca > 60 else "🔵"
            
            texto += f"{icone_confianca} **{sugestao['nome_curto']}** - {sugestao.get('artigos', '')}\n"
            texto += f"   {sugestao['nome_completo']}\n"
            texto += f"   (Relevância: {int(confianca)}%)\n\n"
        
        texto += "Você pode usar estas sugestões ou informar outras normas que conheça."
        
        return texto

    # =============================================================================
    # INTEGRAÇÃO RAG
    # =============================================================================

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
                # Extrair contexto relevante
                linhas = content.split('\n')
                for linha in linhas:
                    if campo.lower() in linha and len(linha.strip()) > 10:
                        exemplos.append(linha.strip()[:100])
                        break
        
        return exemplos[:3] if exemplos else ["Processo de análise", "Procedimento de cadastro", "Atividade de controle"]

    # =============================================================================
    # GERAÇÃO DE CÓDIGO E DADOS
    # =============================================================================

    def _gerar_codigo_processo(self):
        """Gera código baseado na área e estrutura"""
        if not self.area_selecionada:
            return "X.X.X.X"
        
        prefixo = self.AREAS_DECIPEX[self.area_selecionada]["prefixo"]
        # Lógica simplificada - em produção consultaria RAG para incrementar
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
            "documentos_utilizados": self.dados.get("documentos_utilizados", ""),
            "pontos_atencao": self.dados.get("pontos_atencao", ""),
            "etapas": self.etapas_processo,
            "fluxos_entrada": self.fluxos_entrada,
            "fluxos_saida": self.fluxos_saida,
            "data_criacao": datetime.now().strftime("%d/%m/%Y %H:%M")
        }

    def _gerar_pop_completo(self):
        """Gera documento POP formatado - RETORNA DICT para PDFGenerator"""
        # Não gera mais texto, apenas retorna dados estruturados
        # O PDFGenerator em processos.utils fará a geração real
        return self._gerar_dados_completos_pop()

    # =============================================================================
    # MÉTODOS AUXILIARES
    # =============================================================================

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

    # =============================================================================
    # MÉTODOS PÚBLICOS PARA INTERFACE
    # =============================================================================

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