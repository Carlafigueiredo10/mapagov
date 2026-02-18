"""
Helena Reception Agent — triagem assistiva.

Papel: porta de entrada do sistema. Orienta, sugere e direciona.
- Campo aberto sempre disponivel (permite_texto=True)
- Menu de produtos como atalho, nao como portao
- Matching deterministico via catalogo (substring + fuzzy)
- LLM para respostas assistivas (max 80 palavras, temp 0.3)
- Estados: INICIO → ORIENTACAO → TRANSICAO
"""

import copy
import logging
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from processos.domain.helena_recepcao.catalogo_produtos import (
    CATALOGO_PRODUTOS,
    match_produto,
)

logger = logging.getLogger("helena_reception_agent")


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
        "dashboard": {
            "nome": "Painel Executivo",
            "descricao_curta": (
                "Indicadores e visão consolidada das iniciativas."
            ),
            "route": "/painel",
        },
    }

    # Produtos com rota/landing — transitam normalmente
    _PRODUTOS_STARTAVEIS = frozenset(PRODUTOS.keys())

    SYSTEM_PROMPT = (
        "Voce e Helena, assistente de recepcao do MapaGov. "
        "Seu papel e orientar o usuario sobre a plataforma e direcionar para um dos produtos.\n\n"
        "Regras:\n"
        "- Responda em no maximo 80 palavras.\n"
        "- Tom institucional e direto.\n"
        "- Se necessario, faca no maximo 1 pergunta objetiva para direcionar.\n"
        "- Sempre ofereca um encaminhamento para um produto disponivel.\n"
        "- Nao ofereca validacao, diagnostico ou julgamento.\n\n"
        "Produtos disponiveis:\n"
        "1. Mapear processo (POP) — registro estruturado de atividades e documentos\n"
        "2. Analisar riscos — identificacao e avaliacao de riscos com base no Guia MGI\n"
        "3. Planejar estrategicamente — planejamento institucional com modelos de gestao\n"
        "4. Criar fluxograma — representacao visual de processos em BPMN\n"
        "5. Painel Executivo — indicadores e visao consolidada das iniciativas"
    )

    TEXTO_BOAS_VINDAS = (
        "Olá. Posso orientar você sobre o uso da plataforma ou ajudar a localizar "
        "o produto adequado para sua necessidade.\n\n"
        "Você pode selecionar um produto abaixo ou digitar sua pergunta."
    )

    TEXTO_COMPARACAO = (
        "<strong>Comparação rápida dos produtos disponíveis:</strong><br><br>"
        "<strong>Mapear processo (POP)</strong> — você tem um processo de trabalho "
        "e quer documentar cada etapa, responsável e documento envolvido.<br><br>"
        "<strong>Analisar riscos</strong> — você já tem um processo e quer identificar "
        "o que pode dar errado e como tratar.<br><br>"
        "<strong>Planejar estrategicamente</strong> — você precisa definir objetivos, "
        "metas e indicadores para sua unidade.<br><br>"
        "<strong>Criar fluxograma</strong> — você quer uma representação visual "
        "de um fluxo de trabalho.<br><br>"
        "<strong>Painel Executivo</strong> — você precisa de indicadores "
        "e uma visão consolidada das iniciativas."
    )

    TEXTO_TRANSICAO = (
        "Você está saindo da recepção e iniciando "
        "o fluxo de trabalho selecionado."
    )

    _STATUS_LABELS = {
        "homologacao": "em homologação",
        "desenvolvimento": "em desenvolvimento",
        "planejado": "previsto no portfólio",
    }

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
            estrutura_atual["boas_vindas_enviada"] = contexto.get(
                "boas_vindas_enviada", False
            )

        return self._to_orchestrator(bruto, contexto)

    # =========================================================================
    # MAQUINA DE ESTADOS (INICIO → ORIENTACAO → TRANSICAO)
    # =========================================================================

    def processar(self, mensagem: str, contexto: Dict[str, Any]) -> Dict[str, Any]:
        contexto.setdefault("interacoes", 0)
        contexto["interacoes"] += 1

        # Em qualquer estado: chave de produto → transicao direta
        produto = self._extrair_produto(mensagem)
        if produto:
            return self._transicao(produto, contexto)

        # Guard: boas-vindas garantida mesmo se interacoes bugar
        if not contexto.get("boas_vindas_enviada"):
            contexto["boas_vindas_enviada"] = True
            return self._resposta_menu(
                self.TEXTO_BOAS_VINDAS, "ORIENTACAO", True, contexto
            )

        # ORIENTACAO (estado padrao apos boas-vindas)
        if self._eh_ainda_nao_sei(mensagem):
            return self._resposta_comparacao(contexto)

        # Match por catalogo para produtos NAO startaveis → resposta de status
        resultado = match_produto(mensagem)
        if resultado:
            chave_catalogo, origem = resultado
            if chave_catalogo not in self._PRODUTOS_STARTAVEIS:
                logger.info(
                    "recepcao_produto_portfolio produto=%s status=%s origem=%s",
                    chave_catalogo,
                    CATALOGO_PRODUTOS[chave_catalogo]["status"],
                    origem,
                )
                return self._resposta_menu(
                    self._texto_status_produto(chave_catalogo),
                    "ORIENTACAO", True, contexto,
                )
            # startavel → cai no LLM com hint via _sugerir_produto

        return self._resposta_com_llm(mensagem, "ORIENTACAO", contexto)

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
        # Enriquecer com sugestao de produto se detectada por keywords
        sugestao = self._sugerir_produto(mensagem)
        prompt_usuario = mensagem
        if sugestao:
            nome = self.PRODUTOS[sugestao]["nome"]
            prompt_usuario = (
                f"{mensagem}\n\n"
                f"[[SISTEMA: o usuario parece querer '{nome}'. "
                f"Sugira esse produto de forma natural.]]"
            )
            logger.info(
                "recepcao_produto_sugerido produto=%s", sugestao
            )

        try:
            resposta = self.llm.invoke(
                [
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt_usuario},
                ]
            )
            texto = resposta.content if hasattr(resposta, "content") else str(resposta)
            # Converter newlines do LLM para HTML
            texto = texto.replace("\n\n", "<br><br>").replace("\n", "<br>")
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
                    "permite_texto": True,
                    "estado": proximo_estado,
                },
            },
        }

    def _resposta_comparacao(self, contexto: Dict[str, Any]) -> Dict[str, Any]:
        contexto["estado_recepcao"] = "ORIENTACAO"
        return {
            "acao": "menu_produtos",
            "texto": self.TEXTO_COMPARACAO,
            "payload": {
                "tipo_interface": "decisao_produto",
                "dados_interface": {
                    "produtos": self._lista_produtos(),
                    "permite_texto": True,
                    "estado": "ORIENTACAO",
                },
            },
        }

    def _transicao(
        self, produto_key: str, contexto: Dict[str, Any]
    ) -> Dict[str, Any]:
        produto = self.PRODUTOS[produto_key]
        contexto["estado_recepcao"] = "TRANSICAO"
        logger.info("recepcao_transicao_produto produto=%s", produto_key)
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

    def _sugerir_produto(self, mensagem: str) -> str | None:
        """Match via catalogo. Retorna chave so se produto e startavel."""
        resultado = match_produto(mensagem)
        if resultado:
            chave, origem = resultado
            if chave in self._PRODUTOS_STARTAVEIS:
                logger.info(
                    "recepcao_produto_sugerido produto=%s origem=%s",
                    chave, origem,
                )
                return chave
        return None

    def _texto_status_produto(self, chave: str) -> str:
        """Texto informativo para produto que nao tem landing page."""
        prod = CATALOGO_PRODUTOS[chave]
        label = self._STATUS_LABELS.get(prod["status"], prod["status"])
        nome = prod["nome"]
        desc = prod["descricao_curta"]
        return (
            f"<strong>{nome}</strong> faz parte do portfólio MapaGov "
            f"e está {label}.<br><br>"
            f"{desc}<br><br>"
            f"Você quer trabalhar agora com: POP, riscos, planejamento, "
            f"fluxograma ou Painel Executivo?"
        )

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
