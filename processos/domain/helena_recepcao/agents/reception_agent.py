"""
Helena Reception Agent — funil de decisao institucional.

Papel: porta de entrada do sistema. Nao conversa, classifica e direciona.
- Apresenta os 4 produtos disponiveis desde a primeira interacao
- Max 2 respostas livres antes de forcar escolha
- Usa LLM apenas para explicacoes curtas (max 80 palavras, temp 0.3)
"""

import copy
from typing import Dict, Any
from langchain_openai import ChatOpenAI


class ReceptionAgent:

    PRODUTOS = {
        "pop": {
            "nome": "Mapear processo (POP)",
            "descricao_curta": (
                "Registro estruturado de atividades, responsáveis "
                "e documentos de um processo de trabalho."
            ),
            "route": "/pop",
        },
        "riscos": {
            "nome": "Analisar riscos",
            "descricao_curta": (
                "Identificação e avaliação de riscos associados a um processo, "
                "com base no Guia de Gestão de Riscos do MGI."
            ),
            "route": "/riscos",
        },
        "planejamento": {
            "nome": "Planejar estrategicamente",
            "descricao_curta": (
                "Construção de planejamento estratégico institucional "
                "com modelos reconhecidos de gestão."
            ),
            "route": "/planejamento-estrategico",
        },
        "fluxograma": {
            "nome": "Criar fluxograma",
            "descricao_curta": (
                "Representação visual do fluxo de um processo "
                "em notação BPMN."
            ),
            "route": "/fluxograma",
        },
    }

    SYSTEM_PROMPT = (
        "Você é Helena, recepcionista do MapaGov. "
        "Seu papel é estritamente direcional.\n\n"
        "Regras:\n"
        "- Responda em no máximo 80 palavras.\n"
        "- Seja institucional e direta.\n"
        "- Não faça perguntas abertas.\n"
        "- Sempre conclua orientando o usuário a escolher um dos produtos disponíveis.\n"
        "- Não ofereça validação, diagnóstico ou julgamento.\n\n"
        "Produtos disponíveis:\n"
        "1. Mapear processo (POP) — registro estruturado de atividades e documentos\n"
        "2. Analisar riscos — identificação e avaliação de riscos com base no Guia MGI\n"
        "3. Planejar estrategicamente — planejamento institucional com modelos de gestão\n"
        "4. Criar fluxograma — representação visual de processos em BPMN"
    )

    TEXTO_BOAS_VINDAS = (
        "Este sistema executa atividades de Governança, Riscos e Conformidade.\n\n"
        "Para continuar, selecione o tipo de trabalho que você precisa realizar."
    )

    TEXTO_COMPARACAO = (
        "**Comparação rápida dos produtos disponíveis:**\n\n"
        "- **Mapear processo (POP):** você tem um processo de trabalho e quer "
        "documentar cada etapa, responsável e documento envolvido.\n\n"
        "- **Analisar riscos:** você já tem um processo e quer identificar o que "
        "pode dar errado e como tratar.\n\n"
        "- **Planejar estrategicamente:** você precisa definir objetivos, metas "
        "e indicadores para sua unidade.\n\n"
        "- **Criar fluxograma:** você quer uma representação visual de um fluxo "
        "de trabalho.\n\n"
        "Selecione a opção que mais se aproxima da sua necessidade."
    )

    TEXTO_TRANSICAO = (
        "Você está saindo da recepção e iniciando "
        "o fluxo de trabalho selecionado."
    )

    def __init__(self, llm: ChatOpenAI | None = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.3, request_timeout=30)

    # =========================================================================
    # INTERFACE COM ORQUESTRADOR
    # =========================================================================

    def processar_mensagem(
        self, mensagem: str, estrutura_atual: Dict[str, Any] | None
    ) -> Dict[str, Any]:
        contexto = self._init_contexto(estrutura_atual)
        bruto = self.processar(mensagem, contexto)

        # Sync estado de volta para session_data do orquestrador
        if estrutura_atual is not None:
            estrutura_atual["estado_recepcao"] = contexto.get(
                "estado_recepcao", "INICIO"
            )
            estrutura_atual["interacoes"] = contexto.get("interacoes", 0)

        return self._to_orchestrator(bruto, contexto)

    # =========================================================================
    # MAQUINA DE ESTADOS
    # =========================================================================

    def processar(self, mensagem: str, contexto: Dict[str, Any]) -> Dict[str, Any]:
        contexto.setdefault("interacoes", 0)
        contexto["interacoes"] += 1

        estado = contexto.get("estado_recepcao", "INICIO")

        # Em qualquer estado: se a mensagem e uma chave de produto, transiciona
        produto = self._extrair_produto(mensagem)
        if produto:
            return self._transicao(produto, contexto)

        # --- INICIO ---
        if estado == "INICIO":
            if contexto["interacoes"] == 1:
                # Primeira interacao: welcome + menu
                return self._resposta_menu(
                    self.TEXTO_BOAS_VINDAS, "INICIO", permite_texto=True, contexto=contexto
                )
            else:
                # Usuario digitou texto em vez de selecionar
                contexto["estado_recepcao"] = "EXPLICACAO_CURTA"
                return self._resposta_com_llm(mensagem, "EXPLICACAO_CURTA", contexto)

        # --- EXPLICACAO_CURTA ---
        if estado == "EXPLICACAO_CURTA":
            if self._eh_ainda_nao_sei(mensagem):
                return self._resposta_comparacao(contexto)
            contexto["estado_recepcao"] = "DECISAO_OBRIGATORIA"
            return self._resposta_com_llm(mensagem, "DECISAO_OBRIGATORIA", contexto)

        # --- DECISAO_OBRIGATORIA ---
        if estado == "DECISAO_OBRIGATORIA":
            if self._eh_ainda_nao_sei(mensagem):
                return self._resposta_comparacao(contexto)
            # Qualquer texto nao reconhecido: reapresenta menu sem texto livre
            return self._resposta_menu(
                "Selecione uma das opções disponíveis para continuar.",
                "DECISAO_OBRIGATORIA",
                permite_texto=False,
                contexto=contexto,
            )

        # Fallback
        return self._resposta_menu(
            self.TEXTO_BOAS_VINDAS, "INICIO", permite_texto=True, contexto=contexto
        )

    # =========================================================================
    # RESPOSTAS
    # =========================================================================

    def _resposta_menu(
        self,
        texto: str,
        estado: str,
        permite_texto: bool,
        contexto: Dict[str, Any],
    ) -> Dict[str, Any]:
        contexto["estado_recepcao"] = estado
        return {
            "acao": "menu_produtos",
            "texto": texto,
            "payload": {
                "tipo_interface": "decisao_produto",
                "dados_interface": {
                    "produtos": self._lista_produtos(),
                    "permite_texto": permite_texto,
                    "estado": estado,
                },
            },
        }

    def _resposta_com_llm(
        self, mensagem: str, proximo_estado: str, contexto: Dict[str, Any]
    ) -> Dict[str, Any]:
        permite_texto = proximo_estado != "DECISAO_OBRIGATORIA"

        try:
            resposta = self.llm.invoke(
                [
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": mensagem},
                ]
            )
            texto = resposta.content if hasattr(resposta, "content") else str(resposta)
        except Exception:
            texto = (
                "Não foi possível processar sua pergunta no momento. "
                "Selecione uma das opções abaixo para continuar."
            )

        contexto["estado_recepcao"] = proximo_estado
        return {
            "acao": "menu_produtos",
            "texto": texto,
            "payload": {
                "tipo_interface": "decisao_produto",
                "dados_interface": {
                    "produtos": self._lista_produtos(),
                    "permite_texto": permite_texto,
                    "estado": proximo_estado,
                },
            },
        }

    def _resposta_comparacao(self, contexto: Dict[str, Any]) -> Dict[str, Any]:
        contexto["estado_recepcao"] = "DECISAO_OBRIGATORIA"
        return {
            "acao": "menu_produtos",
            "texto": self.TEXTO_COMPARACAO,
            "payload": {
                "tipo_interface": "decisao_produto",
                "dados_interface": {
                    "produtos": self._lista_produtos(),
                    "permite_texto": False,
                    "estado": "DECISAO_OBRIGATORIA",
                },
            },
        }

    def _transicao(
        self, produto_key: str, contexto: Dict[str, Any]
    ) -> Dict[str, Any]:
        produto = self.PRODUTOS[produto_key]
        contexto["estado_recepcao"] = "TRANSICAO"
        return {
            "acao": "transicao_produto",
            "texto": self.TEXTO_TRANSICAO,
            "payload": {
                "produto": produto_key,
                "route": produto["route"],
                "tipo_interface": "transicao_produto",
                "dados_interface": {
                    "produto_nome": produto["nome"],
                    "route": produto["route"],
                },
            },
        }

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _extrair_produto(self, mensagem: str) -> str | None:
        """Verifica se a mensagem e uma chave de produto (enviada pelo frontend)."""
        chave = mensagem.strip().lower()
        if chave in self.PRODUTOS:
            return chave
        return None

    def _eh_ainda_nao_sei(self, mensagem: str) -> bool:
        msg = mensagem.strip().lower()
        return msg in (
            "ainda_nao_sei",
            "ainda nao sei",
            "ainda não sei",
            "nao sei",
            "não sei",
        )

    def _lista_produtos(self) -> list:
        return [
            {
                "key": key,
                "nome": p["nome"],
                "descricao_curta": p["descricao_curta"],
            }
            for key, p in self.PRODUTOS.items()
        ]

    def _init_contexto(self, estrutura_atual: Dict[str, Any] | None) -> Dict[str, Any]:
        ctx = copy.deepcopy(estrutura_atual or {})
        ctx.setdefault("interacoes", 0)
        ctx.setdefault("estado_recepcao", "INICIO")
        return ctx

    def _to_orchestrator(
        self, bruto: Dict[str, Any], contexto: Dict[str, Any]
    ) -> Dict[str, Any]:
        acao = bruto.get("acao", "")
        texto = bruto.get("texto", "")
        payload = bruto.get("payload", {})

        campo_map = {
            "menu_produtos": "menu",
            "transicao_produto": "transicao",
        }
        campo = campo_map.get(acao, "neutro")

        return {
            "campo": campo,
            "valor": payload.get("produto"),
            "proxima_pergunta": texto,
            "completo": acao == "transicao_produto",
            "percentual": 100,
            "validacao_ok": True,
            "tipo_interface": payload.get("tipo_interface"),
            "dados_interface": payload.get("dados_interface"),
            "route": payload.get("route"),
        }


# Alias para compatibilidade
HelenaReceptionAgent = ReceptionAgent
