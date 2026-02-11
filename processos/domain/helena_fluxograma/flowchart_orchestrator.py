"""
Helena Fluxograma - Orquestrador
Delega coleta e edição ao FlowchartAgent; gera Mermaid quando completo.
"""

import logging
from typing import Dict, Any
from .agents.flowchart_agent import FlowchartAgent

logger = logging.getLogger("helena_flowchart_orchestrator")


class HelenaFluxogramaOrchestrator:

    VERSION = "3.0.0"
    PRODUTO_NOME = "Helena Fluxograma"

    def __init__(self, dados_pdf: Dict[str, Any] | None = None):
        self.agent = FlowchartAgent(dados_pdf=dados_pdf)
        self.dados_pdf = dados_pdf

    def processar(self, mensagem: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa mensagem do usuário.

        session_data é mutado in-place pelo agent (etapas, decisoes, campo_atual_idx, etc.).
        O caller (views.py) salva session_data de volta na sessão Django.

        Returns:
            {resposta, completo, percentual, validacao_ok, fluxograma_mermaid?}
        """
        try:
            resultado = self.agent.processar_mensagem(mensagem, session_data)

            if resultado.get("completo"):
                fluxograma_mermaid = self.agent.gerar_mermaid(session_data)
                logger.info("[processar] completo=True, mermaid gerado")

                return {
                    "resposta": resultado["proxima_pergunta"],
                    "completo": True,
                    "percentual": 100,
                    "fluxograma_mermaid": fluxograma_mermaid,
                    "validacao_ok": resultado.get("validacao_ok", True),
                }

            return {
                "resposta": resultado["proxima_pergunta"],
                "completo": False,
                "percentual": resultado.get("percentual", 0),
                "validacao_ok": resultado.get("validacao_ok", True),
            }

        except Exception as e:
            logger.error(f"[processar] Erro: {e}", exc_info=True)
            return {
                "resposta": f"Ops, tive um problema: {str(e)}. Pode tentar de novo?",
                "completo": False,
                "percentual": 0,
                "validacao_ok": False,
            }

    def gerar_mermaid(self, session_data: Dict[str, Any]) -> str:
        return self.agent.gerar_mermaid(session_data)

    def reset(self):
        self.agent = FlowchartAgent(dados_pdf=self.dados_pdf)


# Compatibilidade
HelenaFluxograma = HelenaFluxogramaOrchestrator
