"""
Helena Análise de Riscos - Orquestrador
Gerencia o fluxo conversacional de análise de riscos usando agentes especializados
"""

import json
import logging
from typing import Dict, Any
from .agents.risk_agent import RiskAgent

logger = logging.getLogger("helena_risks_orchestrator")

class HelenaAnaliseRiscosOrchestrator:
    """
    Orquestrador conversacional para análise de riscos.

    Arquitetura:
    - Mantém estado da sessão (respostas, progresso, contexto do processo)
    - Delega processamento para RiskAgent
    - Retorna respostas formatadas para o frontend
    """

    VERSION = "2.0.0-refactored"
    PRODUTO_NOME = "Helena Análise de Riscos"

    def __init__(self):
        self.agent = RiskAgent()
        self.estado = "inicial"

    def processar(self, mensagem: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa mensagem do usuário no fluxo de análise de riscos.

        Args:
            mensagem: Mensagem do usuário
            session_data: Estado da sessão {
                'respostas': {},
                'pergunta_atual_idx': 0,
                'pop_info': {},  # Info do POP se disponível
                'pop_text': ''   # Texto do POP se disponível
            }

        Returns:
            {
                'resposta': str,
                'completo': bool,
                'percentual': int,
                'dados_coletados': dict,
                'validacao_ok': bool
            }
        """
        try:
            # Inicializa session_data se vazio
            if not session_data:
                session_data = {
                    'respostas': {},
                    'pergunta_atual_idx': 0,
                    'pop_info': {},
                    'pop_text': ''
                }

            # Processa com agente
            resultado = self.agent.processar_mensagem(mensagem, session_data)

            # Atualiza session_data com contexto modificado pelo agente
            # (o agente trabalha com deep copy, então precisamos extrair mudanças)
            if resultado.get('campo') == 'pergunta' and resultado.get('valor'):
                # Agent avançou para próxima pergunta
                pass

            # Verifica se finalizou coleta
            if resultado.get('completo'):
                # Gera relatório usando função existente
                relatorio = self._gerar_relatorio_final(session_data)
                return {
                    'resposta': resultado['proxima_pergunta'],
                    'completo': True,
                    'percentual': 100,
                    'dados_coletados': session_data.get('respostas', {}),
                    'relatorio': relatorio,
                    'validacao_ok': True
                }

            # Retorna próxima pergunta
            return {
                'resposta': resultado['proxima_pergunta'],
                'completo': False,
                'percentual': resultado.get('percentual', 0),
                'dados_coletados': session_data.get('respostas', {}),
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

    def _gerar_relatorio_final(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera relatório final de análise de riscos.
        Usa a função analyze_risks_helena do módulo original.
        """
        try:
            from z_md.helena_analise_riscos import analyze_risks_helena

            pop_text = session_data.get('pop_text', '')
            pop_info = session_data.get('pop_info', {})
            respostas = session_data.get('respostas', {})

            # Converte respostas do formato campo → formato numérico legado
            # (a função original espera '1', '2', '3'... como chaves)
            respostas_legado = self._converter_para_formato_legado(respostas)

            resultado = analyze_risks_helena(
                pop_text=pop_text,
                pop_info=pop_info,
                answers=respostas_legado,
                model="gpt-4o",
                temperature=0.2,
                max_tokens=7000
            )

            return resultado

        except Exception as e:
            logger.error(f"[_gerar_relatorio_final] Erro: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'data': {
                    'cabecalho': {'titulo': 'Erro na geração do relatório'},
                    'riscos': [],
                    'conclusoes_recomendacoes': f'Erro ao gerar relatório: {str(e)}'
                }
            }

    def _converter_para_formato_legado(self, respostas: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converte formato de respostas do novo agente para o formato legado.

        Novo formato: {'contexto_processo': '...', 'dependencias_externas': 'sim', ...}
        Formato legado: {'1': 'sim', '2': 'não', ...}
        """
        # Mapeamento campo → índice numérico legado
        mapeamento = {
            'dependencias_externas': '1',
            'picos_sazonais': '2',
            'risco_conflito_normativo': '3',
            'apontamentos_orgaos_controle': '4',
            'segregacao_funcoes_adequada': '5',
            'plano_backup_operadores': '6',
            'equipe_treinada': '7',
            'frequencia_indisponibilidade_sistemas': '8',
            'inconsistencia_dados_sistemas': '9',
            'plano_contingencia_sistemas': '10',
            'documentos_devolvidos_frequentemente': '11',
            'taxa_devolucoes_alta': '12',
            'risco_fraude_documental': '13',
            'gargalos_principais_fluxo': '14',
            'tempo_medio_conclusao_dias': '15',
            'risco_calculo_incorreto': '16',
            'reposicao_erario_anterior': '17',
            'dados_pessoais_sensiveis_lgpd': '18',
            'controles_internos_existentes': '19',
            'contexto_processo': 'observacoes_adicionais'
        }

        respostas_legado = {}
        for campo, valor in respostas.items():
            if campo in mapeamento:
                chave = mapeamento[campo]
                respostas_legado[chave] = valor

        return respostas_legado

    def reset(self):
        """Reseta o orquestrador para novo ciclo"""
        self.estado = "inicial"
        self.agent = RiskAgent()


# Mantém compatibilidade com nome antigo
HelenaAnaliseRiscos = HelenaAnaliseRiscosOrchestrator
