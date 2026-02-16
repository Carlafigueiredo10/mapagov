"""
PE Orchestrator - Orquestrador Principal do Helena Planejamento Estratégico

Responsável por:
- Gerenciar máquina de estados
- Delegar para agentes especializados
- Coordenar fluxo conversacional
- Persistir dados na sessão
"""
import logging
from typing import Dict, Any
from langchain_openai import ChatOpenAI

from processos.domain.base import BaseHelena
from .schemas import EstadoPlanejamento, MODELOS_ESTRATEGICOS, PERGUNTAS_DIAGNOSTICO
from .agents.okr_agent import OKRAgent
from .agents.swot_agent import SWOTAgent
from .agents.tradicional_agent import TradicionalAgent
from .agents.bsc_agent import BSCAgent
from .agents.cenarios_agent import CenariosAgent
from .agents.analise_5w2h_agent import Analise5W2HAgent
from .agents.hoshin_kanri_agent import HoshinKanriAgent

logger = logging.getLogger(__name__)


class HelenaPlanejamentoEstrategico(BaseHelena):
    """
    Helena especializada em Planejamento Estratégico

    Oferece 3 modos de entrada:
    1. Diagnóstico guiado (5 perguntas)
    2. Exploração de modelos
    3. Seleção direta

    Arquitetura:
    - Herda de BaseHelena (stateless)
    - Delega construção para agentes especializados
    - Máquina de estados gerencia fluxo
    """

    PRODUTO_NOME = "Helena Planejamento Estratégico"
    VERSION = "2.0.0-refactored"

    def __init__(self):
        super().__init__()
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, request_timeout=30)

        # Registry de agentes especializados
        self.agentes = {
            'okr': OKRAgent(llm=self.llm),
            'swot': SWOTAgent(llm=self.llm),
            'tradicional': TradicionalAgent(llm=self.llm),
            'bsc': BSCAgent(llm=self.llm),
            'cenarios': CenariosAgent(llm=self.llm),
            '5w2h': Analise5W2HAgent(llm=self.llm),
            'hoshin': HoshinKanriAgent(llm=self.llm),
        }

    def inicializar_estado(self, skip_intro: bool = False) -> dict:
        """
        Retorna estado inicial limpo

        Args:
            skip_intro: Se True, pula boas-vindas

        Returns:
            dict: Estado inicial
        """
        return {
            'estado_atual': EstadoPlanejamento.ESCOLHA_MODO if skip_intro else EstadoPlanejamento.BOAS_VINDAS,
            'modo_entrada': None,  # diagnostico | explorar | direto
            'diagnostico': {},
            'pontuacao_modelos': {modelo: 0 for modelo in MODELOS_ESTRATEGICOS.keys()},
            'modelos_recomendados': [],
            'modelo_selecionado': None,
            'contexto_organizacional': {},
            'estrutura_planejamento': {},
            'percentual_conclusao': 0,
            'historico_conversa': []
        }

    def processar(self, mensagem: str, session_data: dict) -> dict:
        """
        Processa mensagem do usuário na máquina de estados

        Args:
            mensagem: Texto do usuário
            session_data: Estado atual da sessão

        Returns:
            dict: Resposta + novo estado
        """
        self.validar_mensagem(mensagem)
        self.validar_session_data(session_data)

        estado_atual = session_data.get('estado_atual', EstadoPlanejamento.BOAS_VINDAS)

        logger.info(f"[PE] Estado: {estado_atual} | Mensagem: {mensagem[:50]}...")

        # Adiciona ao histórico
        historico = session_data.get('historico_conversa', [])
        historico.append(f"User: {mensagem}")
        session_data['historico_conversa'] = historico

        # Roteamento por estado
        handler_map = {
            EstadoPlanejamento.BOAS_VINDAS: self._handle_boas_vindas,
            EstadoPlanejamento.ESCOLHA_MODO: self._handle_escolha_modo,
            EstadoPlanejamento.DIAGNOSTICO_P1: self._handle_diagnostico_p1,
            EstadoPlanejamento.DIAGNOSTICO_P2: self._handle_diagnostico_p2,
            EstadoPlanejamento.DIAGNOSTICO_P3: self._handle_diagnostico_p3,
            EstadoPlanejamento.DIAGNOSTICO_P4: self._handle_diagnostico_p4,
            EstadoPlanejamento.DIAGNOSTICO_P5: self._handle_diagnostico_p5,
            EstadoPlanejamento.RECOMENDACAO: self._handle_recomendacao,
            EstadoPlanejamento.CONTEXTO_ORGANIZACIONAL: self._handle_contexto_organizacional,
            EstadoPlanejamento.CONSTRUCAO_MODELO: self._handle_construcao_modelo,
            EstadoPlanejamento.REVISAO: self._handle_revisao,
            EstadoPlanejamento.CONFIRMACAO: self._handle_confirmacao,
            EstadoPlanejamento.FINALIZADO: self._handle_finalizado,
        }

        handler = handler_map.get(estado_atual)

        if not handler:
            logger.error(f"Estado não reconhecido: {estado_atual}")
            return {
                'resposta': f"⚠️ Estado inválido: {estado_atual}. Reinicie a conversa.",
                'session_data': session_data,
                'tipo_interface': 'texto'
            }

        # Executa handler
        resultado = handler(mensagem, session_data)

        # Adiciona resposta ao histórico
        historico.append(f"Helena: {resultado['resposta'][:100]}...")
        session_data['historico_conversa'] = historico[-20:]  # Mantém últimas 20 mensagens

        return resultado

    # ============================================================================
    # HANDLERS DE ESTADOS
    # ============================================================================

    def _handle_boas_vindas(self, mensagem: str, session_data: dict) -> dict:
        """Boas-vindas e apresentação"""
        session_data['estado_atual'] = EstadoPlanejamento.ESCOLHA_MODO

        return {
            'resposta': """Olá! Sou Helena, sua assistente de Planejamento Estratégico. 🎯

Posso te ajudar a criar planejamentos com 7 metodologias diferentes:
- Tradicional (Missão/Visão/Valores)
- BSC Público
- OKR
- SWOT
- Cenários
- 5W2H
- Hoshin Kanri

Como você quer começar?

1️⃣ **Diagnóstico** - Respondo 5 perguntas e te recomendo o melhor modelo
2️⃣ **Explorar** - Quero conhecer os modelos primeiro
3️⃣ **Direto** - Já sei qual modelo usar

Digite o número ou nome da opção.""",
            'session_data': session_data,
            'tipo_interface': 'escolha_modo'
        }

    def _handle_escolha_modo(self, mensagem: str, session_data: dict) -> dict:
        """Escolha do modo de entrada"""
        msg_lower = mensagem.lower()

        # Modo diagnóstico
        if '1' in mensagem or 'diagnostico' in msg_lower or 'diagnóstico' in msg_lower:
            session_data['modo_entrada'] = 'diagnostico'
            session_data['estado_atual'] = EstadoPlanejamento.DIAGNOSTICO_P1

            primeira_pergunta = PERGUNTAS_DIAGNOSTICO[0]
            opcoes_texto = '\n'.join([f"{i+1}. {op['texto']}" for i, op in enumerate(primeira_pergunta['opcoes'])])

            return {
                'resposta': f"""Ótimo! Vou te fazer 5 perguntas rápidas. 📋

**Pergunta 1 de 5:**

{primeira_pergunta['texto']}

{opcoes_texto}

Digite o número da sua resposta.""",
                'session_data': session_data,
                'tipo_interface': 'diagnostico',
                'pergunta_atual': primeira_pergunta
            }

        # Modo explorar
        elif '2' in mensagem or 'explorar' in msg_lower:
            session_data['modo_entrada'] = 'explorar'

            return {
                'resposta': """Em breve! Modo exploração em desenvolvimento. 🚧

Por enquanto, escolha:
1. Diagnóstico
3. Seleção direta""",
                'session_data': session_data,
                'tipo_interface': 'texto'
            }

        # Modo direto
        elif '3' in mensagem or 'direto' in msg_lower:
            session_data['modo_entrada'] = 'direto'
            session_data['estado_atual'] = EstadoPlanejamento.CONTEXTO_ORGANIZACIONAL

            modelos_lista = '\n'.join([
                f"{i+1}. {config['icone']} **{config['nome_curto']}** - {config['descricao'][:60]}..."
                for i, (key, config) in enumerate(MODELOS_ESTRATEGICOS.items())
            ])

            return {
                'resposta': f"""Escolha o modelo desejado:

{modelos_lista}

Digite o número ou nome do modelo.""",
                'session_data': session_data,
                'tipo_interface': 'lista_modelos',
                'modelos': MODELOS_ESTRATEGICOS
            }

        # Não entendeu
        return {
            'resposta': """Não entendi. Por favor, digite:
- **1** para Diagnóstico
- **2** para Explorar
- **3** para Seleção Direta""",
            'session_data': session_data,
            'tipo_interface': 'escolha_modo'
        }

    def _handle_diagnostico_p1(self, mensagem: str, session_data: dict) -> dict:
        """Primeira pergunta do diagnóstico"""
        return self._processar_pergunta_diagnostico(mensagem, session_data, pergunta_index=0, proximo_estado=EstadoPlanejamento.DIAGNOSTICO_P2)

    def _handle_diagnostico_p2(self, mensagem: str, session_data: dict) -> dict:
        """Segunda pergunta do diagnóstico"""
        return self._processar_pergunta_diagnostico(mensagem, session_data, pergunta_index=1, proximo_estado=EstadoPlanejamento.DIAGNOSTICO_P3)

    def _handle_diagnostico_p3(self, mensagem: str, session_data: dict) -> dict:
        """Terceira pergunta do diagnóstico"""
        return self._processar_pergunta_diagnostico(mensagem, session_data, pergunta_index=2, proximo_estado=EstadoPlanejamento.DIAGNOSTICO_P4)

    def _handle_diagnostico_p4(self, mensagem: str, session_data: dict) -> dict:
        """Quarta pergunta do diagnóstico"""
        return self._processar_pergunta_diagnostico(mensagem, session_data, pergunta_index=3, proximo_estado=EstadoPlanejamento.DIAGNOSTICO_P5)

    def _handle_diagnostico_p5(self, mensagem: str, session_data: dict) -> dict:
        """Quinta pergunta do diagnóstico"""
        return self._processar_pergunta_diagnostico(mensagem, session_data, pergunta_index=4, proximo_estado=EstadoPlanejamento.RECOMENDACAO)

    def _processar_pergunta_diagnostico(self, mensagem: str, session_data: dict, pergunta_index: int, proximo_estado: EstadoPlanejamento) -> dict:
        """Helper para processar perguntas do diagnóstico"""
        pergunta = PERGUNTAS_DIAGNOSTICO[pergunta_index]

        # Extrai resposta
        try:
            opcao_index = int(mensagem.strip()) - 1
            if 0 <= opcao_index < len(pergunta['opcoes']):
                opcao_escolhida = pergunta['opcoes'][opcao_index]

                # Registra resposta
                session_data['diagnostico'][pergunta['id']] = opcao_escolhida['valor']

                # Atualiza pontuação
                for modelo, pontos in opcao_escolhida['pontos'].items():
                    session_data['pontuacao_modelos'][modelo] = session_data['pontuacao_modelos'].get(modelo, 0) + pontos

                # Se não é a última pergunta, vai para próxima
                if pergunta_index < len(PERGUNTAS_DIAGNOSTICO) - 1:
                    proxima_pergunta = PERGUNTAS_DIAGNOSTICO[pergunta_index + 1]
                    opcoes_texto = '\n'.join([f"{i+1}. {op['texto']}" for i, op in enumerate(proxima_pergunta['opcoes'])])

                    session_data['estado_atual'] = proximo_estado

                    return {
                        'resposta': f"""**Pergunta {pergunta_index + 2} de 5:**

{proxima_pergunta['texto']}

{opcoes_texto}""",
                        'session_data': session_data,
                        'tipo_interface': 'diagnostico',
                        'pergunta_atual': proxima_pergunta,
                        'progresso': int((pergunta_index + 1) / 5 * 100)
                    }

                # Última pergunta - vai para recomendação
                session_data['estado_atual'] = EstadoPlanejamento.RECOMENDACAO
                return self._handle_recomendacao("", session_data)

        except (ValueError, IndexError):
            pass

        # Resposta inválida
        opcoes_texto = '\n'.join([f"{i+1}. {op['texto']}" for i, op in enumerate(pergunta['opcoes'])])

        return {
            'resposta': f"""Resposta inválida. Digite o número de 1 a {len(pergunta['opcoes'])}:

{opcoes_texto}""",
            'session_data': session_data,
            'tipo_interface': 'diagnostico',
            'pergunta_atual': pergunta
        }

    def _handle_recomendacao(self, mensagem: str, session_data: dict) -> dict:
        """Gera recomendação baseada no diagnóstico"""
        # Ordena modelos por pontuação
        ranking = sorted(
            session_data['pontuacao_modelos'].items(),
            key=lambda x: x[1],
            reverse=True
        )

        top3 = ranking[:3]
        session_data['modelos_recomendados'] = [modelo for modelo, _ in top3]

        recomendacoes = []
        for i, (modelo_key, pontos) in enumerate(top3, 1):
            config = MODELOS_ESTRATEGICOS[modelo_key]
            recomendacoes.append(
                f"{i}. {config['icone']} **{config['nome']}** ({pontos} pontos)\n"
                f"   {config['descricao']}"
            )

        recomendacoes_texto = '\n\n'.join(recomendacoes)

        session_data['estado_atual'] = EstadoPlanejamento.CONTEXTO_ORGANIZACIONAL

        return {
            'resposta': f"""Diagnóstico concluído! 🎯

Com base nas suas respostas, recomendo:

{recomendacoes_texto}

Qual modelo você escolhe? Digite o número (1, 2 ou 3).""",
            'session_data': session_data,
            'tipo_interface': 'recomendacao',
            'modelos_recomendados': top3
        }

    def _handle_contexto_organizacional(self, mensagem: str, session_data: dict) -> dict:
        """Captura contexto organizacional básico"""
        # TODO: Implementar captura de contexto
        # Por enquanto, vai direto para construção

        # Seleciona modelo baseado na mensagem
        try:
            escolha = int(mensagem.strip())
            if 1 <= escolha <= 3:
                modelo_key = session_data['modelos_recomendados'][escolha - 1]
                session_data['modelo_selecionado'] = modelo_key
                session_data['estrutura_planejamento'] = MODELOS_ESTRATEGICOS[modelo_key]['estrutura_inicial'].copy()
                session_data['estado_atual'] = EstadoPlanejamento.CONSTRUCAO_MODELO

                # Delega para agente especializado
                return self._handle_construcao_modelo("", session_data)
        except (ValueError, IndexError):
            pass

        return {
            'resposta': "Escolha inválida. Digite 1, 2 ou 3.",
            'session_data': session_data,
            'tipo_interface': 'texto'
        }

    def _handle_construcao_modelo(self, mensagem: str, session_data: dict) -> dict:
        """Delega construção para agente especializado"""
        modelo_selecionado = session_data.get('modelo_selecionado')

        if not modelo_selecionado:
            return {
                'resposta': "Erro: Modelo não selecionado.",
                'session_data': session_data,
                'tipo_interface': 'texto'
            }

        # Busca agente correspondente
        agente = self.agentes.get(modelo_selecionado)

        if not agente:
            return {
                'resposta': f"⚠️ Agente para '{modelo_selecionado}' ainda não implementado. Em breve!",
                'session_data': session_data,
                'tipo_interface': 'texto'
            }

        # Delega para agente
        if not mensagem:  # Primeira vez
            mensagem = "iniciar"

        resultado_agente = agente.processar_mensagem(
            mensagem=mensagem,
            estrutura_atual=session_data['estrutura_planejamento']
        )

        # Atualiza estrutura
        campo = resultado_agente['campo']
        valor = resultado_agente['valor']

        if campo != 'erro' and campo != 'completo':
            if campo == 'objetivos' and valor:
                # Adiciona objetivo
                if 'objetivos' not in session_data['estrutura_planejamento']:
                    session_data['estrutura_planejamento']['objetivos'] = []
                session_data['estrutura_planejamento']['objetivos'].append(valor)
            elif campo == 'resultados_chave':
                # Atualiza KRs do último objetivo
                ultimo_obj = session_data['estrutura_planejamento']['objetivos'][-1]
                ultimo_obj['resultados_chave'] = valor
            else:
                session_data['estrutura_planejamento'][campo] = valor

        # Atualiza percentual
        session_data['percentual_conclusao'] = resultado_agente['percentual']

        # Se completo, vai para revisão
        if resultado_agente['completo']:
            session_data['estado_atual'] = EstadoPlanejamento.REVISAO
            resumo = agente.gerar_resumo(session_data['estrutura_planejamento'])

            return {
                'resposta': f"""Planejamento concluído! 🎉

{resumo}

Quer revisar ou finalizar?""",
                'session_data': session_data,
                'tipo_interface': 'revisao',
                'estrutura_completa': session_data['estrutura_planejamento']
            }

        # Continua construção
        return {
            'resposta': resultado_agente['proxima_pergunta'],
            'session_data': session_data,
            'tipo_interface': 'construcao',
            'percentual': resultado_agente['percentual']
        }

    def _handle_revisao(self, mensagem: str, session_data: dict) -> dict:
        """Permite revisão antes de finalizar"""
        if 'finalizar' in mensagem.lower():
            session_data['estado_atual'] = EstadoPlanejamento.FINALIZADO
            return self._handle_finalizado("", session_data)

        return {
            'resposta': "Recurso de edição em desenvolvimento. Digite 'finalizar' para concluir.",
            'session_data': session_data,
            'tipo_interface': 'revisao'
        }

    def _handle_confirmacao(self, mensagem: str, session_data: dict) -> dict:
        """Confirmação final"""
        session_data['estado_atual'] = EstadoPlanejamento.FINALIZADO
        return self._handle_finalizado(mensagem, session_data)

    def _handle_finalizado(self, mensagem: str, session_data: dict) -> dict:
        """Estado final"""
        return {
            'resposta': """Planejamento Estratégico concluído com sucesso! ✅

Seu planejamento foi salvo e está disponível para consulta.

Obrigada por usar Helena! 🎯""",
            'session_data': session_data,
            'tipo_interface': 'finalizado',
            'planejamento_completo': session_data['estrutura_planejamento']
        }

    # ============================================================================
    # MÉTODOS AUXILIARES
    # ============================================================================

    def _validar_estrutura_modelo(self, modelo_id: str, estrutura: dict) -> dict:
        """
        Valida se estrutura tem campos mínimos obrigatórios

        Args:
            modelo_id: ID do modelo
            estrutura: Estrutura atual do planejamento

        Returns:
            dict: Status de validação com campos faltantes
        """
        validacoes = {
            'tradicional': ['missao', 'visao', 'valores'],
            'bsc': ['perspectivas'],
            'okr': ['trimestre', 'objetivos'],
            'swot': ['forcas', 'fraquezas', 'oportunidades', 'ameacas'],
            'cenarios': ['forcas_motrizes', 'incertezas_criticas'],
            '5w2h': ['acoes'],
            'hoshin': ['breakthrough', 'matriz_x']
        }

        campos_obrigatorios = validacoes.get(modelo_id, [])
        campos_faltantes = []

        for campo in campos_obrigatorios:
            valor = estrutura.get(campo)
            # Campo vazio ou lista vazia
            if not valor or (isinstance(valor, list) and len(valor) == 0):
                campos_faltantes.append(campo)

        total_campos = len(campos_obrigatorios)
        campos_preenchidos = total_campos - len(campos_faltantes)

        return {
            'valido': len(campos_faltantes) == 0,
            'campos_faltantes': campos_faltantes,
            'percentual': (campos_preenchidos / total_campos * 100) if total_campos > 0 else 0
        }
