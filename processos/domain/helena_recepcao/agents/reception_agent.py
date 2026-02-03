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
        Processa mensagem do usuário de forma conversacional.

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

        # 👋 Boas-vindas (primeira interação com saudação)
        if contexto["interacoes"] == 1:
            if any(p in msg for p in ["oi", "olá", "bom dia", "boa tarde", "começar", "iniciar", "start", "help"]):
                return {
                    "acao": "boas_vindas",
                    "texto": (
                        "Oi! 👋 Bem-vindo à Helena GRC!\n\n"
                        "Sou a recepcionista virtual. Posso te ajudar a entender sobre GRC "
                        "e te direcionar ao produto certo.\n\n"
                        "**Produtos disponíveis:**\n"
                        "🧩 **P1: Gerador de POP** - Mapear e documentar processos\n"
                        "🔄 **P2: Fluxograma** - Criar diagramas visuais\n"
                        "🧠 **P5: Análise de Riscos** - GRC e conformidade\n"
                        "📊 **P3: Dashboard** (em breve) - Indicadores e métricas\n\n"
                        "Me conta: o que você precisa fazer hoje? Pode perguntar qualquer coisa!"
                    ),
                    "payload": {}
                }

        # ❓ PRIMEIRO: Verificar se é uma PERGUNTA (antes de detectar produto)
        eh_pergunta = self._eh_pergunta(msg)

        if eh_pergunta:
            # Usa LLM para responder de forma conversacional
            return self._responder_pergunta(mensagem, contexto)

        # 🎯 SEGUNDO: Detecta intenção de USAR um produto
        if self._quer_usar_produto(msg):
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

        # 🤖 TERCEIRO: Tenta responder com LLM para qualquer outra coisa
        return self._responder_pergunta(mensagem, contexto)

    def _eh_pergunta(self, msg: str) -> bool:
        """Detecta se a mensagem é uma pergunta."""
        indicadores_pergunta = [
            "o que é", "o que são", "o que significa",
            "como funciona", "como faço", "como fazer",
            "qual é", "qual a", "quais são", "quais os",
            "por que", "porque", "pra que", "para que",
            "quando", "onde", "quem",
            "explica", "me explica", "pode explicar",
            "me fala", "me conta", "me diz",
            "o que", "?",
            "significa", "conceito", "definição",
            "diferença entre", "diferente de"
        ]
        return any(ind in msg for ind in indicadores_pergunta)

    def _quer_usar_produto(self, msg: str) -> bool:
        """Detecta se o usuário quer USAR um produto (não só perguntar sobre)."""
        indicadores_uso = [
            "quero", "preciso", "vou", "vamos",
            "fazer", "criar", "gerar", "mapear",
            "iniciar", "começar", "usar", "utilizar",
            "me ajuda a", "ajuda a", "ajude-me",
            "pode fazer", "faz um", "faz uma",
            "elaborar", "desenvolver", "construir"
        ]
        return any(ind in msg for ind in indicadores_uso)

    def _responder_pergunta(self, mensagem: str, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """Usa LLM para responder perguntas de forma conversacional."""

        # Contexto sobre os produtos para a LLM
        produtos_info = "\n".join([
            f"- {p['emoji']} {p['nome']} ({p['codigo']}): {p['descricao']}"
            for p in self.PRODUTOS.values()
        ])

        prompt = f"""Você é Helena, uma assistente virtual especializada em GRC (Governança, Riscos e Conformidade).

Seu papel é CONVERSAR e EXPLICAR conceitos de forma clara e didática. Seja amigável e prestativa.

**Produtos disponíveis na plataforma:**
{produtos_info}

**Instruções:**
1. Responda a pergunta do usuário de forma clara e educativa
2. Se a pergunta for sobre um tema relacionado a um produto, explique o conceito primeiro
3. Ao final, sugira gentilmente o produto relacionado se fizer sentido (não force)
4. Use linguagem simples e acessível
5. Resposta deve ter no máximo 150 palavras
6. Use markdown para formatação (negrito, listas)

**Pergunta do usuário:** {mensagem}

Responda de forma conversacional:"""

        try:
            resposta = self.llm.invoke(prompt)
            texto_resposta = resposta.content if hasattr(resposta, 'content') else str(resposta)

            return {
                "acao": "conversa",
                "texto": texto_resposta,
                "payload": {}
            }
        except Exception as e:
            # Fallback se LLM falhar
            return {
                "acao": "conversa",
                "texto": (
                    "Boa pergunta! Infelizmente tive um probleminha técnico.\n\n"
                    "Posso te ajudar de outra forma:\n"
                    "🧩 **Gerador de POP** - documentar processos\n"
                    "🔄 **Fluxograma** - criar diagramas\n"
                    "🧠 **Análise de Riscos** - GRC e conformidade\n\n"
                    "Qual te interessa?"
                ),
                "payload": {"erro": str(e)}
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
            "conversa": ("conversa", None, True),
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
