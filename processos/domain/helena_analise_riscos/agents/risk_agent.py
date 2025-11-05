import copy
from typing import Dict, Any
from langchain_openai import ChatOpenAI
import re
from processos.domain.helena_semantic_planner import HelenaSemanticPlanner

class RiskAgent:
    """
    Helena Risk Agent – parceira conversacional para análise de riscos.
    Não há formulário rígido, apenas perguntas contextuais sobre o processo.
    Helena guia naturalmente pela coleta de dados de GRC.

    Usa HelenaSemanticPlanner para interpretação semântica robusta.
    """

    def __init__(self, llm: ChatOpenAI | None = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        self.planner = HelenaSemanticPlanner()

        # Seções de perguntas organizadas por tema
        self.SECOES = [
            {
                "nome": "Contexto Geral",
                "perguntas": [
                    {
                        "id": "contexto_geral",
                        "tipo": "texto_livre",
                        "mensagem": "Oi! Vamos conversar sobre o processo. Me conta brevemente como ele funciona no dia a dia?",
                        "campo": "contexto_processo"
                    },
                    {
                        "id": "dependencias_externas",
                        "tipo": "sim_nao",
                        "mensagem": "O processo depende de aprovações ou sistemas de outros órgãos/áreas?",
                        "campo": "dependencias_externas"
                    },
                    {
                        "id": "picos_demanda",
                        "tipo": "sim_nao",
                        "mensagem": "Existem períodos do ano com muito mais demanda que o normal (ex: final do ano, férias)?",
                        "campo": "picos_sazonais"
                    }
                ]
            },
            {
                "nome": "Sistemas e Tecnologia",
                "perguntas": [
                    {
                        "id": "conflito_normativo",
                        "tipo": "escala",
                        "mensagem": "Qual o risco de haver conflito entre as normas que regem o processo?",
                        "opcoes": ["Baixo", "Médio", "Alto"],
                        "campo": "risco_conflito_normativo"
                    },
                    {
                        "id": "apontamentos_controle",
                        "tipo": "sim_nao",
                        "mensagem": "Já houve apontamentos de TCU, CGU ou Ouvidoria sobre este processo?",
                        "campo": "apontamentos_orgaos_controle"
                    },
                    {
                        "id": "segregacao_funcoes",
                        "tipo": "sim_nao",
                        "mensagem": "A mesma pessoa que solicita também pode aprovar? (isso seria um problema de segregação)",
                        "campo": "segregacao_funcoes_adequada",
                        "inverter": True
                    }
                ]
            },
            {
                "nome": "Equipe e Operação",
                "perguntas": [
                    {
                        "id": "backup_operadores",
                        "tipo": "sim_nao",
                        "mensagem": "Se alguém da equipe se ausenta, outra pessoa consegue assumir facilmente as tarefas?",
                        "campo": "plano_backup_operadores"
                    },
                    {
                        "id": "treinamento",
                        "tipo": "sim_nao",
                        "mensagem": "A equipe recebe treinamento periódico sobre normas e sistemas?",
                        "campo": "equipe_treinada"
                    },
                    {
                        "id": "sistemas_indisponibilidade",
                        "tipo": "escala",
                        "mensagem": "Com que frequência os sistemas (SIGEPE, SEI, SouGov) ficam fora do ar?",
                        "opcoes": ["Nunca", "Raramente (1x/mês)", "Às vezes (1x/semana)", "Frequentemente (>2x/semana)"],
                        "campo": "frequencia_indisponibilidade_sistemas"
                    }
                ]
            },
            {
                "nome": "Gestão Documental",
                "perguntas": [
                    {
                        "id": "inconsistencia_dados",
                        "tipo": "sim_nao",
                        "mensagem": "Já houve casos de dados diferentes entre sistemas (ex: CPF no SIAPE ≠ SEI)?",
                        "campo": "inconsistencia_dados_sistemas"
                    },
                    {
                        "id": "plano_contingencia",
                        "tipo": "sim_nao",
                        "mensagem": "Existe procedimento alternativo quando o sistema cai?",
                        "campo": "plano_contingencia_sistemas"
                    },
                    {
                        "id": "documentos_devolvidos",
                        "tipo": "sim_nao",
                        "mensagem": "Documentos costumam ser devolvidos para correção?",
                        "campo": "documentos_devolvidos_frequentemente"
                    },
                    {
                        "id": "taxa_devolucoes",
                        "tipo": "sim_nao",
                        "mensagem": "Mais de 10% dos documentos são devolvidos?",
                        "campo": "taxa_devolucoes_alta"
                    }
                ]
            },
            {
                "nome": "Segurança e Integridade",
                "perguntas": [
                    {
                        "id": "fraude",
                        "tipo": "sim_nao",
                        "mensagem": "Já houve caso ou suspeita de fraude/manipulação de documentos?",
                        "campo": "risco_fraude_documental"
                    },
                    {
                        "id": "gargalos",
                        "tipo": "texto_livre",
                        "mensagem": "Qual etapa do processo costuma atrasar mais?",
                        "campo": "gargalos_principais_fluxo"
                    },
                    {
                        "id": "tempo_medio",
                        "tipo": "numero",
                        "mensagem": "Qual o tempo médio para concluir um processo? (em dias)",
                        "campo": "tempo_medio_conclusao_dias"
                    }
                ]
            },
            {
                "nome": "Riscos Financeiros",
                "perguntas": [
                    {
                        "id": "calculo_incorreto",
                        "tipo": "sim_nao",
                        "mensagem": "Já houve erro de cálculo que gerou pagamento incorreto?",
                        "campo": "risco_calculo_incorreto"
                    },
                    {
                        "id": "reposicao_erario",
                        "tipo": "sim_nao",
                        "mensagem": "Já foi necessário devolver dinheiro ao erário por erro?",
                        "campo": "reposicao_erario_anterior"
                    }
                ]
            },
            {
                "nome": "Conformidade e LGPD",
                "perguntas": [
                    {
                        "id": "dados_sensiveis",
                        "tipo": "sim_nao",
                        "mensagem": "O processo trata dados pessoais sensíveis (CPF, saúde, financeiros)?",
                        "campo": "dados_pessoais_sensiveis_lgpd"
                    },
                    {
                        "id": "controles_internos",
                        "tipo": "sim_nao",
                        "mensagem": "Existem controles formalizados (checklist, dupla conferência, indicadores)?",
                        "campo": "controles_internos_existentes"
                    }
                ]
            }
        ]

        # Total de perguntas
        self.total_perguntas = sum(len(secao["perguntas"]) for secao in self.SECOES)

    # =========================================================================
    # SHIM DE COMPATIBILIDADE COM ORQUESTRADOR
    # =========================================================================

    def processar_mensagem(self, mensagem: str, estrutura_atual: Dict[str, Any] | None) -> Dict[str, Any]:
        """
        Método de compatibilidade com o orquestrador.

        Mantém a assinatura esperada pelo risk_orchestrator.py:
        - Recebe estrutura_atual (dict)
        - Retorna {'campo', 'valor', 'proxima_pergunta', 'completo', 'percentual', 'validacao_ok'}
        """
        contexto = self._init_contexto(estrutura_atual)
        bruto = self.processar(mensagem, contexto)  # Chama método interno
        return self._to_orchestrator(bruto, contexto)

    # =========================================================================
    # LÓGICA INTERNA (FORMATO SEMÂNTICO)
    # =========================================================================

    def processar(self, mensagem: str, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa mensagem do usuário usando interpretação semântica.

        Returns formato interno:
            {
                'acao': str,      # boas_vindas, proxima_pergunta, salvar_resposta, etc.
                'texto': str,     # Mensagem para o usuário
                'payload': dict   # Dados adicionais
            }
        """
        msg = mensagem.lower().strip()

        # Inicializa estrutura
        contexto.setdefault("respostas", {})
        contexto.setdefault("pergunta_atual_idx", 0)

        # 👋 Boas-vindas (primeira interação)
        if contexto["pergunta_atual_idx"] == 0:
            if any(p in msg for p in ["oi", "olá", "começar", "iniciar", "start"]):
                # Primeira mensagem é boas-vindas, próxima será primeira pergunta
                return {
                    "acao": "boas_vindas",
                    "texto": (
                        "Oi 👋 Que bom te ver! Vou te ajudar a fazer uma análise de riscos completa do processo.\n\n"
                        "Não é formulário chato, é conversa natural. Vamos juntos mapear:\n"
                        "🔍 Contexto e dependências\n"
                        "⚙️ Sistemas e tecnologia\n"
                        "👥 Equipe e operação\n"
                        "📄 Gestão documental\n"
                        "🔒 Segurança e integridade\n"
                        "💰 Riscos financeiros\n"
                        "✅ Conformidade e LGPD\n\n"
                        "Vamos começar?"
                    ),
                    "payload": {}
                }
            # Se não é mensagem de início mas idx=0, avança para primeira pergunta
            # (usuário já respondeu boas-vindas ou iniciou sem saudação)

        # Salva resposta anterior e avança
        if contexto["pergunta_atual_idx"] > 0:
            self._salvar_resposta_contexto(mensagem, contexto)

        # Verifica se acabou
        if contexto["pergunta_atual_idx"] >= self.total_perguntas:
            return {
                "acao": "finalizar",
                "texto": (
                    "✅ Perfeito! Coletei todas as informações necessárias.\n\n"
                    "Agora vou gerar o **Relatório de Análise de Riscos Avançado** "
                    "baseado nos referenciais COSO ERM, ISO 31000 e TCU.\n\n"
                    "Pode levar alguns segundos..."
                ),
                "payload": {"respostas_completas": contexto["respostas"]}
            }

        # Próxima pergunta
        return self._proxima_pergunta(contexto)

    def _proxima_pergunta(self, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """Retorna próxima pergunta do fluxo"""

        idx = contexto["pergunta_atual_idx"]
        contador = 0

        for secao in self.SECOES:
            for pergunta in secao["perguntas"]:
                if contador == idx:
                    contexto["pergunta_atual_idx"] += 1

                    # Monta mensagem
                    mensagem = pergunta["mensagem"]
                    if pergunta["tipo"] == "escala":
                        opcoes_texto = " | ".join([f"({i+1}) {opt}" for i, opt in enumerate(pergunta["opcoes"])])
                        mensagem += f"\n\n{opcoes_texto}"

                    progresso = f"[{contexto['pergunta_atual_idx']}/{self.total_perguntas}]"

                    return {
                        "acao": "fazer_pergunta",
                        "texto": f"{progresso} {mensagem}",
                        "payload": {
                            "pergunta_id": pergunta["id"],
                            "pergunta_config": pergunta
                        }
                    }
                contador += 1

        # Acabou
        return {
            "acao": "finalizar",
            "texto": "✅ Análise completa! Gerando relatório...",
            "payload": {}
        }

    def _salvar_resposta_contexto(self, mensagem: str, contexto: Dict[str, Any]):
        """Salva resposta do usuário no contexto"""

        idx = contexto["pergunta_atual_idx"] - 1
        contador = 0

        for secao in self.SECOES:
            for pergunta in secao["perguntas"]:
                if contador == idx:
                    campo = pergunta["campo"]

                    # Normaliza conforme tipo
                    if pergunta["tipo"] == "sim_nao":
                        valor = "sim" if any(x in mensagem.lower() for x in ["sim", "s", "yes", "1"]) else "não"
                        if pergunta.get("inverter"):
                            valor = "não" if valor == "sim" else "sim"
                        contexto["respostas"][campo] = valor

                    elif pergunta["tipo"] == "escala":
                        # Tenta extrair número ou texto da opção
                        for i, opcao in enumerate(pergunta["opcoes"]):
                            if str(i+1) in mensagem or opcao.lower() in mensagem.lower():
                                contexto["respostas"][campo] = opcao.lower()
                                break
                        else:
                            contexto["respostas"][campo] = mensagem.lower()

                    elif pergunta["tipo"] in ["texto_livre", "numero"]:
                        contexto["respostas"][campo] = mensagem

                    return
                contador += 1

    # =========================================================================
    # CONVERSORES DE FORMATO
    # =========================================================================

    def _init_contexto(self, estrutura_atual: Dict[str, Any] | None) -> Dict[str, Any]:
        """Inicializa contexto a partir da estrutura do orquestrador."""
        ctx = copy.deepcopy(estrutura_atual or {})
        ctx.setdefault("respostas", {})
        ctx.setdefault("pergunta_atual_idx", 0)
        return ctx

    def _to_orchestrator(self, bruto: Dict[str, Any], contexto: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converte formato interno {acao, texto, payload} para contrato do orquestrador:
        {'campo', 'valor', 'proxima_pergunta', 'completo', 'percentual', 'validacao_ok'}
        """
        acao = bruto.get("acao")
        texto = bruto.get("texto", "")
        payload = bruto.get("payload", {})

        # Mapeamento de ações → campo/valor
        mapeamento = {
            "boas_vindas": ("inicio", None, True),
            "fazer_pergunta": ("pergunta", payload.get("pergunta_id"), True),
            "finalizar": ("relatorio", payload.get("respostas_completas"), True),
        }

        campo, valor, validacao_ok = mapeamento.get(acao, ("neutro", None, True))

        return {
            "campo": campo,
            "valor": valor,
            "proxima_pergunta": texto,
            "completo": acao == "finalizar",
            "percentual": self._calc_percentual(contexto),
            "validacao_ok": validacao_ok
        }

    def _calc_percentual(self, contexto: Dict[str, Any]) -> int:
        """Calcula percentual de conclusão da análise de riscos."""
        idx = contexto.get("pergunta_atual_idx", 0)
        if idx == 0:
            return 5

        percentual = int((idx / self.total_perguntas) * 95) + 5
        return min(percentual, 100)


# Alias para compatibilidade
HelenaRiskAgent = RiskAgent
