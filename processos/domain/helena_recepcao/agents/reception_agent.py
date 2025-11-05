import copy
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from processos.domain.helena_semantic_planner import HelenaSemanticPlanner

class ReceptionAgent:
    """
    Helena Reception Agent – recepcionista virtual para direcionamento GRC.

    Papel: RECEPCIONISTA, não executora
    - Dar boas-vindas e entender necessidade
    - Direcionar para produto correto
    - Responder dúvidas gerais sobre GRC

    Usa HelenaSemanticPlanner para interpretação semântica robusta.
    """

    PRODUTOS = {
        "pop": {
            "nome": "Gerador de POP",
            "emoji": "🧩",
            "codigo": "P1",
            "descricao": "Mapear processos e gerar Procedimentos Operacionais Padrão",
            "keywords": ["pop", "procedimento", "mapear", "processo", "documentar", "passo a passo"]
        },
        "fluxograma": {
            "nome": "Gerador de Fluxograma",
            "emoji": "🔄",
            "codigo": "P2",
            "descricao": "Criar fluxogramas visuais de processos",
            "keywords": ["fluxograma", "diagrama", "fluxo", "visual", "mermaid", "etapas"]
        },
        "riscos": {
            "nome": "Análise de Riscos",
            "emoji": "🧠",
            "codigo": "P5",
            "descricao": "Identificar e analisar riscos em processos (GRC)",
            "keywords": ["risco", "análise", "grc", "controle", "conformidade", "auditoria"]
        },
        "dashboard": {
            "nome": "Dashboard",
            "emoji": "📊",
            "codigo": "P3",
            "descricao": "Visualizar indicadores e métricas",
            "keywords": ["dashboard", "indicador", "métrica", "painel", "visualizar"],
            "status": "em_desenvolvimento"
        }
    }

    def __init__(self, llm: ChatOpenAI | None = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        self.planner = HelenaSemanticPlanner()

    # =========================================================================
    # SHIM DE COMPATIBILIDADE COM ORQUESTRADOR
    # =========================================================================

    def processar_mensagem(self, mensagem: str, estrutura_atual: Dict[str, Any] | None) -> Dict[str, Any]:
        """
        Método de compatibilidade com o orquestrador.

        Retorna: {'campo', 'valor', 'proxima_pergunta', 'completo', 'percentual', 'validacao_ok'}
        """
        contexto = self._init_contexto(estrutura_atual)
        bruto = self.processar(mensagem, contexto)
        return self._to_orchestrator(bruto, contexto)

    # =========================================================================
    # LÓGICA INTERNA (FORMATO SEMÂNTICO)
    # =========================================================================

    def processar(self, mensagem: str, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa mensagem do usuário usando interpretação semântica.

        Returns formato interno:
            {
                'acao': str,
                'texto': str,
                'payload': dict
            }
        """
        msg = mensagem.lower().strip()

        # Inicializa estrutura
        contexto.setdefault("interacoes", 0)
        contexto["interacoes"] += 1

        # 👋 Boas-vindas (primeira interação)
        if contexto["interacoes"] == 1:
            if any(p in msg for p in ["oi", "olá", "bom dia", "boa tarde", "começar", "iniciar", "start", "ajuda", "help"]):
                return {
                    "acao": "boas_vindas",
                    "texto": (
                        "Oi! 👋 Bem-vindo à Helena GRC!\n\n"
                        "Sou a recepcionista virtual. Estou aqui para te direcionar ao produto certo.\n\n"
                        "**Produtos disponíveis:**\n"
                        "🧩 **P1: Gerador de POP** - Mapear e documentar processos\n"
                        "🔄 **P2: Fluxograma** - Criar diagramas visuais\n"
                        "🧠 **P5: Análise de Riscos** - GRC e conformidade\n"
                        "📊 **P3: Dashboard** (em breve) - Indicadores e métricas\n\n"
                        "Me conta: o que você precisa fazer hoje?"
                    ),
                    "payload": {}
                }

        # 🔍 Detecta intenção usando palavras-chave
        produto_detectado = self._detectar_produto(msg)

        if produto_detectado:
            produto = self.PRODUTOS[produto_detectado]

            # Se produto em desenvolvimento
            if produto.get("status") == "em_desenvolvimento":
                return {
                    "acao": "produto_indisponivel",
                    "texto": (
                        f"{produto['emoji']} **{produto['nome']}** ({produto['codigo']}) está em desenvolvimento.\n\n"
                        "Por enquanto, posso te ajudar com:\n"
                        "🧩 Gerador de POP\n"
                        "🔄 Fluxograma\n"
                        "🧠 Análise de Riscos\n\n"
                        "Qual desses te interessa?"
                    ),
                    "payload": {"produto_solicitado": produto_detectado}
                }

            # Produto disponível - direciona
            return {
                "acao": "direcionar_produto",
                "texto": (
                    f"Perfeito! Para isso você precisa do **{produto['nome']}** {produto['emoji']}\n\n"
                    f"**{produto['descricao']}**\n\n"
                    f"👉 Clique no card **{produto['codigo']}** no menu para começar!\n\n"
                    "Precisa de mais alguma coisa?"
                ),
                "payload": {
                    "produto": produto_detectado,
                    "produto_codigo": produto['codigo'],
                    "produto_nome": produto['nome']
                }
            }

        # ❓ Perguntas gerais sobre GRC
        if any(p in msg for p in ["o que é", "como funciona", "explica", "conceito", "norma", "lei"]):
            return {
                "acao": "orientacao_grc",
                "texto": (
                    "Posso te dar uma orientação geral sobre GRC!\n\n"
                    "**Governança, Riscos e Conformidade (GRC)** envolve:\n"
                    "📋 Mapear processos organizacionais\n"
                    "🔍 Identificar riscos operacionais\n"
                    "✅ Garantir conformidade com normas\n"
                    "📊 Monitorar indicadores de desempenho\n\n"
                    "Para trabalhar com isso na prática, use nossos produtos:\n"
                    "- **Gerador de POP**: documenta processos\n"
                    "- **Análise de Riscos**: mapeia vulnerabilidades\n"
                    "- **Fluxograma**: visualiza fluxos\n\n"
                    "Qual desses você quer usar?"
                ),
                "payload": {}
            }

        # 🤷 Não entendeu - pede clarificação
        return {
            "acao": "pedir_clarificacao",
            "texto": (
                "Hmm, não entendi direito. Pode me contar com outras palavras?\n\n"
                "Por exemplo:\n"
                "- 'Quero mapear um processo'\n"
                "- 'Preciso analisar riscos'\n"
                "- 'Como faço um fluxograma?'\n\n"
                "Ou escolha diretamente:\n"
                "🧩 POP | 🔄 Fluxograma | 🧠 Riscos"
            ),
            "payload": {}
        }

    def _detectar_produto(self, mensagem: str) -> str | None:
        """Detecta qual produto o usuário precisa baseado em keywords"""

        msg_lower = mensagem.lower()

        # Conta matches para cada produto
        matches = {}
        for produto_id, produto in self.PRODUTOS.items():
            count = sum(1 for keyword in produto["keywords"] if keyword in msg_lower)
            if count > 0:
                matches[produto_id] = count

        # Retorna produto com mais matches
        if matches:
            return max(matches, key=matches.get)

        return None

    # =========================================================================
    # CONVERSORES DE FORMATO
    # =========================================================================

    def _init_contexto(self, estrutura_atual: Dict[str, Any] | None) -> Dict[str, Any]:
        """Inicializa contexto a partir da estrutura do orquestrador."""
        ctx = copy.deepcopy(estrutura_atual or {})
        ctx.setdefault("interacoes", 0)
        return ctx

    def _to_orchestrator(self, bruto: Dict[str, Any], contexto: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converte formato interno {acao, texto, payload} para contrato do orquestrador.
        """
        acao = bruto.get("acao")
        texto = bruto.get("texto", "")
        payload = bruto.get("payload", {})

        # Mapeamento de ações → campo/valor
        mapeamento = {
            "boas_vindas": ("inicio", None, True),
            "direcionar_produto": ("direcionar", payload.get("produto"), True),
            "orientacao_grc": ("orientacao", None, True),
            "produto_indisponivel": ("indisponivel", payload.get("produto_solicitado"), True),
            "pedir_clarificacao": ("clarificacao", None, True),
        }

        campo, valor, validacao_ok = mapeamento.get(acao, ("neutro", None, True))

        return {
            "campo": campo,
            "valor": valor,
            "proxima_pergunta": texto,
            "completo": False,  # Recepção nunca "completa", é sempre contínua
            "percentual": 100,  # Sempre 100% porque não tem fluxo linear
            "validacao_ok": validacao_ok
        }


# Alias para compatibilidade
HelenaReceptionAgent = ReceptionAgent
