"""
Helena Recepção - Orquestrador
Gerencia o fluxo conversacional de recepção e direcionamento usando agentes especializados
"""

import logging
from typing import Dict, Any
from .agents.reception_agent import ReceptionAgent

logger = logging.getLogger("helena_reception_orchestrator")

class HelenaRecepcaoOrchestrator:
    """
    Orquestrador conversacional para recepção e direcionamento.

    Arquitetura:
    - Mantém estado da sessão (histórico de interações)
    - Delega processamento para ReceptionAgent
    - Gerencia direcionamento para produtos
    - Retorna respostas formatadas para o frontend
    """

    VERSION = "2.0.0-refactored"
    PRODUTO_NOME = "Helena Recepção"

    def __init__(self):
        self.agent = ReceptionAgent()
        self.estado = "ativo"  # Recepção está sempre ativa

    def processar(self, mensagem: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa mensagem do usuário no fluxo de recepção.

        Args:
            mensagem: Mensagem do usuário
            session_data: Estado da sessão {
                'interacoes': 0,
                'historico': []
            }

        Returns:
            {
                'resposta': str,
                'produto_direcionado': str | None,
                'validacao_ok': bool,
                'acao': str
            }
        """
        try:
            # Inicializa session_data se vazio
            if not session_data:
                session_data = {
                    'interacoes': 0,
                    'historico': []
                }

            # Processa com agente
            resultado = self.agent.processar_mensagem(mensagem, session_data)

            # Adiciona ao histórico
            if 'historico' not in session_data:
                session_data['historico'] = []

            session_data['historico'].append({
                'usuario': mensagem,
                'helena': resultado['proxima_pergunta'],
                'campo': resultado.get('campo')
            })

            # Limita histórico a últimas 10 interações
            if len(session_data['historico']) > 10:
                session_data['historico'] = session_data['historico'][-10:]

            # Retorna resposta formatada
            return {
                'resposta': resultado['proxima_pergunta'],
                'produto_direcionado': resultado.get('valor'),
                'validacao_ok': resultado.get('validacao_ok', True),
                'acao': resultado.get('campo', 'neutro'),
                'historico': session_data.get('historico', []),
                'tipo_interface': resultado.get('tipo_interface'),
                'dados_interface': resultado.get('dados_interface'),
                'route': resultado.get('route'),
            }

        except Exception as e:
            logger.error(f"[processar] Erro: {e}", exc_info=True)
            return {
                'resposta': "⚠️ Ops, tive um problema temporário. Pode tentar novamente?",
                'produto_direcionado': None,
                'validacao_ok': False,
                'acao': 'erro',
                'erro': str(e)
            }

    def reset(self):
        """Reseta o orquestrador para novo ciclo"""
        self.estado = "ativo"
        self.agent = ReceptionAgent()


# Mantém compatibilidade com nome antigo
HelenaRecepcao = HelenaRecepcaoOrchestrator
