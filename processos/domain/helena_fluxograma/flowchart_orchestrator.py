"""
Helena Fluxograma - Orquestrador
Gerencia o fluxo conversacional de mapeamento de processos usando agentes especializados
"""

import json
import logging
from typing import Dict, Any
from .agents.flowchart_agent import FlowchartAgent

logger = logging.getLogger("helena_flowchart_orchestrator")

class HelenaFluxogramaOrchestrator:
    """
    Orquestrador conversacional para mapeamento de fluxogramas.

    Arquitetura:
    - Mantém estado da sessão (dados coletados, campo atual, PDF importado)
    - Delega processamento para FlowchartAgent
    - Gera fluxogramas visuais em Mermaid
    - Retorna respostas formatadas para o frontend
    """

    VERSION = "2.0.0-refactored"
    PRODUTO_NOME = "Helena Fluxograma"

    def __init__(self, dados_pdf: Dict[str, Any] | None = None):
        """
        Inicializa orquestrador.

        Args:
            dados_pdf: Dados opcionais extraídos do PDF do POP
                {
                    'atividade': 'Nome do processo',
                    'sistemas': ['SEI', 'SIGEPE'],
                    'operadores': ['Servidor', 'Chefia', 'RH'],
                    'titulo': 'Título alternativo'
                }
        """
        self.agent = FlowchartAgent(dados_pdf=dados_pdf)
        self.dados_pdf = dados_pdf
        self.estado = "inicial"

    def processar(self, mensagem: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa mensagem do usuário no fluxo de mapeamento.

        Args:
            mensagem: Mensagem do usuário
            session_data: Estado da sessão {
                'dados_coletados': {},
                'campo_atual_idx': 0
            }

        Returns:
            {
                'resposta': str,
                'completo': bool,
                'percentual': int,
                'dados_coletados': dict,
                'validacao_ok': bool,
                'fluxograma_mermaid': str (quando completo)
            }
        """
        try:
            # Inicializa session_data se vazio
            if not session_data:
                session_data = {
                    'dados_coletados': {},
                    'campo_atual_idx': 0
                }

            # Processa com agente
            resultado = self.agent.processar_mensagem(mensagem, session_data)

            # Verifica se finalizou coleta
            if resultado.get('completo'):
                # Gera fluxograma Mermaid
                dados = session_data.get('dados_coletados', {})
                fluxograma_mermaid = self.agent.gerar_mermaid(dados)

                return {
                    'resposta': resultado['proxima_pergunta'] + f"\n\n```mermaid\n{fluxograma_mermaid}\n```",
                    'completo': True,
                    'percentual': 100,
                    'dados_coletados': dados,
                    'fluxograma_mermaid': fluxograma_mermaid,
                    'validacao_ok': True
                }

            # Retorna próxima pergunta
            return {
                'resposta': resultado['proxima_pergunta'],
                'completo': False,
                'percentual': resultado.get('percentual', 0),
                'dados_coletados': session_data.get('dados_coletados', {}),
                'validacao_ok': resultado.get('validacao_ok', True)
            }

        except Exception as e:
            logger.error(f"[processar] Erro: {e}", exc_info=True)
            return {
                'resposta': f"Ops, tive um problema: {str(e)}. Pode tentar de novo?",
                'completo': False,
                'percentual': 0,
                'dados_coletados': {},
                'validacao_ok': False,
                'erro': str(e)
            }

    def gerar_mermaid(self, dados: Dict[str, Any]) -> str:
        """
        Gera código Mermaid para fluxograma visual.

        Args:
            dados: Dados coletados do processo

        Returns:
            Código Mermaid formatado
        """
        return self.agent.gerar_mermaid(dados)

    def reset(self):
        """Reseta o orquestrador para novo ciclo"""
        self.estado = "inicial"
        self.agent = FlowchartAgent(dados_pdf=self.dados_pdf)


# Mantém compatibilidade com nome antigo
HelenaFluxograma = HelenaFluxogramaOrchestrator
