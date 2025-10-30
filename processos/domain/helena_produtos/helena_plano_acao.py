# -*- coding: utf-8 -*-
"""
Helena Plano de Acao - P6

Gestao completa de acoes: mitigacao de riscos, implementacao de oportunidades
e planejamento estrategico (incluindo mobilizacao para mapeamento).

Arquitetura Clean:
- Herda de BaseHelena (stateless)
- Estado gerenciado via session_data
- Maquina de estados para coleta de dados do plano de acao
"""
from enum import Enum
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from processos.domain.base import BaseHelena

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS - Estados da Conversa
# ============================================================================

class EstadoPlanoAcao(str, Enum):
    """Estados da maquina de estados para coleta do Plano de Acao"""
    BOAS_VINDAS = "boas_vindas"
    TIPO_PLANO = "tipo_plano"
    OBJETIVO = "objetivo"
    AREA_RESPONSAVEL = "area_responsavel"
    PRAZO_TOTAL = "prazo_total"
    ACOES_SUGESTAO = "acoes_sugestao"
    REFINAMENTO_ACOES = "refinamento_acoes"
    DETALHAMENTO_5W2H = "detalhamento_5w2h"
    CONFIRMACAO = "confirmacao"
    FINALIZADO = "finalizado"


# ============================================================================
# TEMPLATES DE PLANOS DE ACAO
# ============================================================================

TEMPLATES_PLANOS = {
    'mobilizacao': {
        'nome': 'Mobilizacao para Mapeamento de Processos',
        'acoes_padrao': [
            {
                'what': 'Reuniao de kickoff com equipe',
                'why': 'Alinhar objetivos e metodologia do mapeamento',
                'where': 'Sala de reunioes',
                'prazo_dias': 7,
                'who': 'Coordenador',
                'how': 'Apresentacao do projeto MapaGov e metodologia Helena',
                'custo': 0
            },
            {
                'what': 'Levantamento de processos existentes',
                'why': 'Identificar atividades criticas para priorizacao',
                'where': 'Area especifica',
                'prazo_dias': 21,
                'who': 'Equipe tecnica',
                'how': 'Entrevistas com gestores + analise de documentacao',
                'custo': 0
            },
            {
                'what': 'Priorizacao de atividades para mapeamento',
                'why': 'Definir ordem de execucao baseada em criticidade',
                'where': 'Reuniao de planejamento',
                'prazo_dias': 28,
                'who': 'Coordenador + Gestores',
                'how': 'Matriz de priorizacao (impacto x urgencia)',
                'custo': 0
            },
            {
                'what': 'Treinamento em Helena (P1 - Gerador de POP)',
                'why': 'Capacitar equipe no uso da ferramenta',
                'where': 'Online',
                'prazo_dias': 35,
                'who': 'Toda equipe',
                'how': 'Workshop pratico com casos reais',
                'custo': 3000
            },
            {
                'what': 'Execucao do mapeamento',
                'why': 'Documentar processos priorizados',
                'where': 'Area especifica',
                'prazo_dias': 90,
                'who': 'Toda equipe',
                'how': 'Chat com Helena + validacao com especialistas',
                'custo': 0
            }
        ]
    },
    'auditoria': {
        'nome': 'Preparacao para Auditoria',
        'acoes_padrao': [
            {
                'what': 'Levantamento de documentacao requerida',
                'why': 'Mapear requisitos da auditoria',
                'where': 'Setor responsavel',
                'prazo_dias': 7,
                'who': 'Analista de conformidade',
                'how': 'Analise do termo de referencia da auditoria',
                'custo': 0
            },
            {
                'what': 'Identificacao de gaps documentais',
                'why': 'Antecipar nao-conformidades',
                'where': 'Analise interna',
                'prazo_dias': 14,
                'who': 'Equipe de conformidade',
                'how': 'Checklist comparativo com requisitos',
                'custo': 0
            },
            {
                'what': 'Adequacao de processos nao-conformes',
                'why': 'Corrigir gaps identificados',
                'where': 'Areas envolvidas',
                'prazo_dias': 45,
                'who': 'Responsaveis pelos processos',
                'how': 'Plano de acao corretivo por gap',
                'custo': 5000
            },
            {
                'what': 'Simulacao de auditoria interna',
                'why': 'Validar preparacao antes da auditoria real',
                'where': 'Todas as areas auditadas',
                'prazo_dias': 60,
                'who': 'Auditoria interna',
                'how': 'Auditoria-piloto com checklist oficial',
                'custo': 2000
            }
        ]
    },
    'treinamento': {
        'nome': 'Treinamento de Equipe',
        'acoes_padrao': [
            {
                'what': 'Levantamento de necessidades de capacitacao',
                'why': 'Identificar gaps de conhecimento',
                'where': 'Pesquisa com equipe',
                'prazo_dias': 7,
                'who': 'RH + Gestor',
                'how': 'Questionario + entrevistas',
                'custo': 0
            },
            {
                'what': 'Selecao de fornecedores/instrutores',
                'why': 'Garantir qualidade do treinamento',
                'where': 'Processo de cotacao',
                'prazo_dias': 21,
                'who': 'Setor de compras',
                'how': 'Pesquisa de mercado + avaliacao tecnica',
                'custo': 0
            },
            {
                'what': 'Execucao do treinamento',
                'why': 'Capacitar equipe',
                'where': 'Online ou presencial',
                'prazo_dias': 45,
                'who': 'Toda equipe',
                'how': 'Curso teorico + pratico',
                'custo': 8000
            }
        ]
    }
}


# ============================================================================
# HELENA PLANO DE ACAO
# ============================================================================

class HelenaPlanoAcao(BaseHelena):
    """
    Helena especializada em criacao de Planos de Acao (P6).

    Modo 3 (v1): Criar plano do zero via chat conversacional
    Futuro: Importar de P5 (riscos) e P3 (oportunidades)
    """

    PRODUTO_NOME = "Helena Plano de Acao"
    VERSION = "1.0.0"

    def __init__(self):
        super().__init__()
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    def inicializar_estado(self, skip_intro: bool = False) -> dict:
        """
        Retorna estado inicial limpo.

        Args:
            skip_intro: Se True, pula boas-vindas (para retomada de sessao)

        Returns:
            dict: Estado inicial
        """
        return {
            'estado_atual': EstadoPlanoAcao.TIPO_PLANO if skip_intro else EstadoPlanoAcao.BOAS_VINDAS,
            'dados_coletados': {
                'tipo_plano': None,
                'objetivo': None,
                'area': None,
                'prazo_total_dias': None,
                'acoes': []  # Lista de acoes 5W2H
            },
            'historico_conversa': []
        }

    def processar(self, mensagem: str, session_data: dict) -> dict:
        """
        Processa mensagem do usuario na maquina de estados.

        Args:
            mensagem: Texto do usuario
            session_data: Estado atual da sessao

        Returns:
            dict: Resposta + novo estado
        """
        self.validar_mensagem(mensagem)
        self.validar_session_data(session_data)

        estado_atual = session_data.get('estado_atual', EstadoPlanoAcao.BOAS_VINDAS)
        dados = session_data.get('dados_coletados', {})

        logger.info(f"[P6] Estado: {estado_atual} | Mensagem: {mensagem[:50]}...")

        # Adiciona ao historico
        historico = session_data.get('historico_conversa', [])
        historico.append(f"User: {mensagem}")

        # Roteamento por estado
        if estado_atual == EstadoPlanoAcao.BOAS_VINDAS:
            return self._handle_boas_vindas(mensagem, session_data)

        elif estado_atual == EstadoPlanoAcao.TIPO_PLANO:
            return self._handle_tipo_plano(mensagem, session_data)

        elif estado_atual == EstadoPlanoAcao.OBJETIVO:
            return self._handle_objetivo(mensagem, session_data)

        elif estado_atual == EstadoPlanoAcao.AREA_RESPONSAVEL:
            return self._handle_area(mensagem, session_data)

        elif estado_atual == EstadoPlanoAcao.PRAZO_TOTAL:
            return self._handle_prazo(mensagem, session_data)

        elif estado_atual == EstadoPlanoAcao.ACOES_SUGESTAO:
            return self._handle_acoes_sugestao(mensagem, session_data)

        elif estado_atual == EstadoPlanoAcao.REFINAMENTO_ACOES:
            return self._handle_refinamento(mensagem, session_data)

        elif estado_atual == EstadoPlanoAcao.CONFIRMACAO:
            return self._handle_confirmacao(mensagem, session_data)

        elif estado_atual == EstadoPlanoAcao.FINALIZADO:
            return self._handle_finalizado(mensagem, session_data)

        else:
            logger.error(f"Estado desconhecido: {estado_atual}")
            return self.criar_resposta(
                resposta="Ops, algo deu errado. Vamos recomecar?",
                novo_estado=self.inicializar_estado()
            )

    # ========================================================================
    # HANDLERS POR ESTADO
    # ========================================================================

    def _handle_boas_vindas(self, mensagem: str, session_data: dict) -> dict:
        """Boas-vindas e explicacao do P6"""
        resposta = """Ola! Sou a Helena Plano de Acao.

Vou te ajudar a criar um Plano de Acao estruturado para:
- Mobilizar equipe para mapeamento de processos
- Preparar auditorias
- Implementar oportunidades de melhoria
- Organizar treinamentos
- E muito mais!

Vamos comecar?"""

        novo_estado = session_data.copy()
        novo_estado['estado_atual'] = EstadoPlanoAcao.TIPO_PLANO

        return self.criar_resposta(
            resposta=resposta,
            novo_estado=novo_estado,
            progresso="Iniciando"
        )

    def _handle_tipo_plano(self, mensagem: str, session_data: dict) -> dict:
        """Coleta tipo de plano"""
        # Detecta tipo baseado em keywords
        msg_lower = mensagem.lower()

        if any(word in msg_lower for word in ['mapear', 'mapeamento', 'pop', 'processos', 'mobiliza']):
            tipo = 'mobilizacao'
        elif any(word in msg_lower for word in ['auditoria', 'audit', 'conformidade']):
            tipo = 'auditoria'
        elif any(word in msg_lower for word in ['treina', 'capacita', 'curso', 'workshop']):
            tipo = 'treinamento'
        else:
            # Pergunta explicitamente
            resposta = """Que tipo de plano voce quer criar?

1 - Mobilizacao para Mapeamento - Organizar equipe para mapear processos
2 - Preparacao para Auditoria - Estruturar preparacao para auditoria
3 - Treinamento de Equipe - Planejar capacitacao
4 - Outro - Criar plano personalizado

Digite o numero ou descreva o que precisa:"""

            return self.criar_resposta(
                resposta=resposta,
                novo_estado=session_data,
                progresso="1/6"
            )

        # Tipo detectado - avanca
        novo_estado = session_data.copy()
        novo_estado['dados_coletados']['tipo_plano'] = tipo
        novo_estado['estado_atual'] = EstadoPlanoAcao.OBJETIVO

        template_nome = TEMPLATES_PLANOS.get(tipo, {}).get('nome', tipo.title())

        resposta = f"""Perfeito! Vamos criar um plano de {template_nome}.

Agora me conte: qual e o objetivo principal deste plano?

Exemplo: "Mapear todas as 45 atividades da CGRIS nos proximos 3 meses" """

        return self.criar_resposta(
            resposta=resposta,
            novo_estado=novo_estado,
            progresso="2/6"
        )

    def _handle_objetivo(self, mensagem: str, session_data: dict) -> dict:
        """Coleta objetivo do plano"""
        novo_estado = session_data.copy()
        novo_estado['dados_coletados']['objetivo'] = mensagem
        novo_estado['estado_atual'] = EstadoPlanoAcao.AREA_RESPONSAVEL

        resposta = """Objetivo registrado!

Qual area ou setor sera responsavel pela execucao?

Exemplo: "CGRIS", "CGCAF", "Diretoria completa", etc."""

        return self.criar_resposta(
            resposta=resposta,
            novo_estado=novo_estado,
            progresso="3/6"
        )

    def _handle_area(self, mensagem: str, session_data: dict) -> dict:
        """Coleta area responsavel"""
        novo_estado = session_data.copy()
        novo_estado['dados_coletados']['area'] = mensagem
        novo_estado['estado_atual'] = EstadoPlanoAcao.PRAZO_TOTAL

        resposta = """Area registrada!

Qual o prazo total para conclusao do plano?

Digite em dias (ex: "90 dias") ou meses (ex: "3 meses"):"""

        return self.criar_resposta(
            resposta=resposta,
            novo_estado=novo_estado,
            progresso="4/6"
        )

    def _handle_prazo(self, mensagem: str, session_data: dict) -> dict:
        """Coleta prazo total"""
        # Extrai numero de dias
        import re
        msg_lower = mensagem.lower()

        # Tenta extrair dias
        match_dias = re.search(r'(\d+)\s*dias?', msg_lower)
        match_meses = re.search(r'(\d+)\s*m[eê]s', msg_lower)

        if match_dias:
            dias = int(match_dias.group(1))
        elif match_meses:
            dias = int(match_meses.group(1)) * 30
        else:
            # Tenta pegar qualquer numero
            match_num = re.search(r'(\d+)', mensagem)
            if match_num:
                dias = int(match_num.group(1))
            else:
                return self.criar_resposta(
                    resposta="Nao consegui entender o prazo. Por favor, digite algo como '90 dias' ou '3 meses':",
                    novo_estado=session_data,
                    progresso="4/6"
                )

        novo_estado = session_data.copy()
        novo_estado['dados_coletados']['prazo_total_dias'] = dias
        novo_estado['estado_atual'] = EstadoPlanoAcao.ACOES_SUGESTAO

        # Gera sugestoes de acoes baseado no template
        tipo = novo_estado['dados_coletados']['tipo_plano']
        template = TEMPLATES_PLANOS.get(tipo, {'acoes_padrao': []})

        acoes_sugeridas = self._gerar_acoes_com_ia(
            tipo=tipo,
            objetivo=novo_estado['dados_coletados']['objetivo'],
            prazo_dias=dias,
            template=template
        )

        novo_estado['dados_coletados']['acoes'] = acoes_sugeridas

        # Formata acoes para exibicao
        acoes_texto = self._formatar_acoes(acoes_sugeridas)

        resposta = f"""Prazo registrado: {dias} dias

Com base no seu objetivo, sugiro as seguintes acoes:

{acoes_texto}

O que voce acha? Podemos:
- Confirmar estas acoes
- Adicionar mais acoes
- Editar alguma acao especifica

Digite sua escolha:"""

        return self.criar_resposta(
            resposta=resposta,
            novo_estado=novo_estado,
            progresso="5/6"
        )

    def _handle_acoes_sugestao(self, mensagem: str, session_data: dict) -> dict:
        """Usuario confirma ou refina acoes"""
        msg_lower = mensagem.lower()

        if any(word in msg_lower for word in ['confirmar', 'ok', 'perfeito', 'sim', 'aprovar']):
            # Confirma - vai para finalizacao
            novo_estado = session_data.copy()
            novo_estado['estado_atual'] = EstadoPlanoAcao.CONFIRMACAO

            dados = session_data['dados_coletados']
            resumo = self._gerar_resumo(dados)

            resposta = f"""Otimo! Aqui esta o resumo do seu Plano de Acao:

{resumo}

Deseja salvar este plano?
Digite "salvar" para confirmar ou "editar" para ajustar algo."""

            return self.criar_resposta(
                resposta=resposta,
                novo_estado=novo_estado,
                progresso="6/6"
            )

        else:
            # Usuario quer editar - conversa com IA
            return self._handle_refinamento(mensagem, session_data)

    def _handle_refinamento(self, mensagem: str, session_data: dict) -> dict:
        """Refinamento conversacional das acoes"""
        # Usa LLM para interpretar edicao
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Voce e assistente especializada em planos de acao.
O usuario quer ajustar as acoes sugeridas. Interprete o pedido e ajude-o.

Se ele quiser adicionar acao, pergunte os detalhes.
Se quiser remover, confirme qual.
Se quiser editar, pergunte o que mudar.

Seja objetiva e pratica."""),
            ("human", "{mensagem}")
        ])

        chain = prompt | self.llm
        resposta_ia = chain.invoke({"mensagem": mensagem})

        return self.criar_resposta(
            resposta=resposta_ia.content,
            novo_estado=session_data,
            progresso="5/6 (Refinando)"
        )

    def _handle_confirmacao(self, mensagem: str, session_data: dict) -> dict:
        """Confirmacao final e salvamento"""
        msg_lower = mensagem.lower()

        if 'salvar' in msg_lower or 'confirmar' in msg_lower or 'sim' in msg_lower:
            # Salva no banco de dados
            plano_id = self._salvar_plano(session_data['dados_coletados'])

            novo_estado = session_data.copy()
            novo_estado['estado_atual'] = EstadoPlanoAcao.FINALIZADO
            novo_estado['plano_id'] = plano_id

            resposta = f"""Plano de Acao salvo com sucesso!

ID do Plano: {plano_id}

Proximos passos:
1. Acesse o Dashboard para visualizar o plano
2. Acompanhe o andamento das acoes
3. Atualize o status conforme execucao

Posso ajudar com algo mais?"""

            return self.criar_resposta(
                resposta=resposta,
                novo_estado=novo_estado,
                progresso="Concluido"
            )

        else:
            resposta = """O que voce gostaria de editar?

Digite o numero da acao que deseja modificar ou descreva a mudanca:"""

            novo_estado = session_data.copy()
            novo_estado['estado_atual'] = EstadoPlanoAcao.REFINAMENTO_ACOES

            return self.criar_resposta(
                resposta=resposta,
                novo_estado=novo_estado,
                progresso="5/6 (Editando)"
            )

    def _handle_finalizado(self, mensagem: str, session_data: dict) -> dict:
        """Estado final - plano ja salvo"""
        resposta = """Plano de Acao ja foi salvo!

Quer criar um novo plano? Digite "novo plano"
Ou acesse o Dashboard para gerenciar seus planos."""

        return self.criar_resposta(
            resposta=resposta,
            novo_estado=session_data,
            progresso="Concluido"
        )

    # ========================================================================
    # HELPERS
    # ========================================================================

    def _gerar_acoes_com_ia(
        self,
        tipo: str,
        objetivo: str,
        prazo_dias: int,
        template: dict
    ) -> List[Dict[str, Any]]:
        """
        Gera acoes usando template + ajuste por IA.

        Args:
            tipo: Tipo do plano
            objetivo: Objetivo descrito pelo usuario
            prazo_dias: Prazo total em dias
            template: Template de acoes padrao

        Returns:
            Lista de acoes estruturadas
        """
        acoes_base = template.get('acoes_padrao', [])

        # Ajusta prazos proporcionalmente
        data_inicio = datetime.now().date()
        acoes = []

        for idx, acao in enumerate(acoes_base):
            prazo_acao = data_inicio + timedelta(days=acao['prazo_dias'])

            acoes.append({
                'ordem': idx + 1,
                'what': acao['what'],
                'why': acao['why'],
                'where': acao['where'],
                'when_fim': prazo_acao.isoformat(),
                'who': acao['who'],
                'how': acao['how'],
                'how_much_estimado': acao['custo']
            })

        return acoes

    def _formatar_acoes(self, acoes: List[Dict[str, Any]]) -> str:
        """Formata lista de acoes para exibicao"""
        linhas = []
        for acao in acoes:
            linhas.append(
                f"{acao['ordem']}. {acao['what']}\n"
                f"   Onde: {acao['where']}\n"
                f"   Quem: {acao['who']}\n"
                f"   Prazo: {acao['when_fim']}\n"
                f"   Custo: R$ {acao['how_much_estimado']}\n"
            )
        return "\n".join(linhas)

    def _gerar_resumo(self, dados: dict) -> str:
        """Gera resumo do plano para confirmacao"""
        tipo_display = TEMPLATES_PLANOS.get(dados['tipo_plano'], {}).get('nome', dados['tipo_plano'])
        total_acoes = len(dados['acoes'])
        custo_total = sum(a['how_much_estimado'] for a in dados['acoes'])

        return f"""Tipo: {tipo_display}
Objetivo: {dados['objetivo']}
Area: {dados['area']}
Prazo: {dados['prazo_total_dias']} dias
Total de Acoes: {total_acoes}
Custo Total Estimado: R$ {custo_total:,.2f}"""

    def _salvar_plano(self, dados: dict) -> int:
        """
        Salva plano no banco de dados.

        Args:
            dados: Dados coletados do plano

        Returns:
            ID do plano criado
        """
        from processos.models_new import PlanoAcao, Acao
        from django.contrib.auth.models import User
        from decimal import Decimal

        # Pega usuario padrao (em producao, viria do contexto)
        user = User.objects.get(username='teste_helena')

        # Cria plano
        plano = PlanoAcao.objects.create(
            titulo=f"{dados['objetivo'][:100]}",
            tipo=dados['tipo_plano'],
            objetivo=dados['objetivo'],
            prazo_total_dias=dados['prazo_total_dias'],
            area=dados['area'],
            custo_total_estimado=Decimal(sum(a['how_much_estimado'] for a in dados['acoes'])),
            criado_por=user,
            status='ativo'
        )

        # Cria acoes
        for acao_data in dados['acoes']:
            Acao.objects.create(
                plano=plano,
                ordem=acao_data['ordem'],
                what=acao_data['what'],
                why=acao_data['why'],
                where=acao_data['where'],
                when_fim=acao_data['when_fim'],
                who=acao_data['who'],
                how=acao_data['how'],
                how_much_estimado=Decimal(acao_data['how_much_estimado']),
                status='pendente'
            )

        logger.info(f"[P6] Plano salvo: ID={plano.id}, {len(dados['acoes'])} acoes")

        return plano.id
