"""
Helena POP v2.0 - Mapeamento de Processos Operacionais Padrão

Arquitetura Clean:
- Herda de BaseHelena (stateless)
- Estado gerenciado via session_data
- Sem dependências externas de domain_old/infra_old
- Máquina de estados para coleta de dados do processo
"""
from enum import Enum
from typing import Dict, Any, List
import logging
import pandas as pd

from processos.domain.base import BaseHelena

# Tentativa de importar BaseLegalSuggestorDECIPEx (opcional)
try:
    from processos.base_legal_decipex import BaseLegalSuggestorDECIPEx
    BASE_LEGAL_DISPONIVEL = True
except ImportError:
    BASE_LEGAL_DISPONIVEL = False

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS - Estados da Conversa
# ============================================================================

class EstadoPOP(str, Enum):
    """Estados da máquina de estados para coleta do POP"""
    BOAS_VINDAS = "boas_vindas"
    NOME_USUARIO = "nome_usuario"
    CONFIRMA_NOME = "confirma_nome"
    PRE_EXPLICACAO = "pre_explicacao"
    EXPLICACAO = "explicacao"
    EXPLICACAO_FINAL = "explicacao_final"
    AREA_DECIPEX = "area_decipex"
    ARQUITETURA = "arquitetura"
    NOME_PROCESSO = "nome_processo"
    ENTREGA_ESPERADA = "entrega_esperada"
    DISPOSITIVOS_NORMATIVOS = "dispositivos_normativos"
    OPERADORES = "operadores"
    SISTEMAS = "sistemas"
    DOCUMENTOS = "documentos"
    FLUXOS = "fluxos"
    TRANSICAO_EPICA = "transicao_epica"  # 🎯 NOVO: Transição motivacional antes das etapas
    DELEGACAO_ETAPAS = "delegacao_etapas"
    FINALIZADO = "finalizado"


# ============================================================================
# ARQUITETURA DECIPEX
# ============================================================================

class ArquiteturaDecipex:
    """Carrega e consulta arquitetura de processos da DECIPEX"""

    def __init__(self, caminho_csv='documentos_teste/Arquitetura_DECIPEX_mapeada.csv'):
        try:
            self.df = pd.read_csv(caminho_csv)
        except FileNotFoundError:
            logger.warning(f"Arquivo CSV não encontrado: {caminho_csv}")
            self.df = pd.DataFrame(columns=['Macroprocesso', 'Processo', 'Subprocesso', 'Atividade'])
        except Exception as e:
            logger.error(f"Erro ao carregar CSV: {e}")
            self.df = pd.DataFrame(columns=['Macroprocesso', 'Processo', 'Subprocesso', 'Atividade'])

    def obter_macroprocessos_unicos(self) -> List[str]:
        return self.df['Macroprocesso'].unique().tolist()

    def obter_processos_por_macro(self, macro: str) -> List[str]:
        return self.df[self.df['Macroprocesso'] == macro]['Processo'].unique().tolist()

    def obter_subprocessos_por_processo(self, macro: str, processo: str) -> List[str]:
        filtro = (self.df['Macroprocesso'] == macro) & (self.df['Processo'] == processo)
        return self.df[filtro]['Subprocesso'].unique().tolist()

    def obter_atividades_por_subprocesso(self, macro: str, processo: str, subprocesso: str) -> List[str]:
        filtro = (
            (self.df['Macroprocesso'] == macro) &
            (self.df['Processo'] == processo) &
            (self.df['Subprocesso'] == subprocesso)
        )
        return self.df[filtro]['Atividade'].unique().tolist()


# ============================================================================
# STATE MACHINE - POPStateMachine
# ============================================================================

class POPStateMachine:
    """Máquina de estados para coletar dados do POP"""

    def __init__(self):
        self.estado = EstadoPOP.BOAS_VINDAS
        self.nome_usuario = ""
        self.nome_temporario = ""
        self.area_selecionada = None
        self.macro_selecionado = None
        self.processo_selecionado = None
        self.subprocesso_selecionado = None
        self.atividade_selecionada = None
        self.dados_coletados = {
            'nome_processo': '',
            'entrega_esperada': '',
            'dispositivos_normativos': [],
            'operadores': [],
            'sistemas': [],
            'documentos': [],
            'fluxos_entrada': [],
            'fluxos_saida': []
        }
        self.concluido = False

    def to_dict(self) -> Dict[str, Any]:
        """Serializa o state machine para JSON"""
        return {
            'estado': self.estado.value,
            'nome_usuario': self.nome_usuario,
            'nome_temporario': self.nome_temporario,
            'area_selecionada': self.area_selecionada,
            'macro_selecionado': self.macro_selecionado,
            'processo_selecionado': self.processo_selecionado,
            'subprocesso_selecionado': self.subprocesso_selecionado,
            'atividade_selecionada': self.atividade_selecionada,
            'dados_coletados': self.dados_coletados,
            'concluido': self.concluido
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'POPStateMachine':
        """Deserializa o state machine do JSON"""
        sm = cls()
        sm.estado = EstadoPOP(data.get('estado', EstadoPOP.BOAS_VINDAS.value))
        sm.nome_usuario = data.get('nome_usuario', '')
        sm.nome_temporario = data.get('nome_temporario', '')
        sm.area_selecionada = data.get('area_selecionada')
        sm.macro_selecionado = data.get('macro_selecionado')
        sm.processo_selecionado = data.get('processo_selecionado')
        sm.subprocesso_selecionado = data.get('subprocesso_selecionado')
        sm.atividade_selecionada = data.get('atividade_selecionada')
        sm.dados_coletados = data.get('dados_coletados', {
            'nome_processo': '',
            'entrega_esperada': '',
            'dispositivos_normativos': [],
            'operadores': [],
            'sistemas': [],
            'documentos': [],
            'fluxos_entrada': [],
            'fluxos_saida': []
        })
        sm.concluido = data.get('concluido', False)
        return sm


# ============================================================================
# HELENA POP v2.0
# ============================================================================

class HelenaPOP(BaseHelena):
    """
    Helena POP v2.0 - Coleta de dados para mapeamento de processos

    Responsabilidades:
    - Guiar usuário através da coleta de dados do processo
    - Integrar com arquitetura DECIPEX
    - Sugerir base legal quando disponível
    - Preparar dados para delegação ao Helena Etapas
    """

    VERSION = "2.0.0"
    PRODUTO_NOME = "Helena POP"

    def __init__(self):
        super().__init__()

        # Carregar arquitetura DECIPEX
        self.arquitetura = ArquiteturaDecipex()

        # Integração base legal (opcional)
        if BASE_LEGAL_DISPONIVEL:
            try:
                self.suggestor_base_legal = BaseLegalSuggestorDECIPEx()
            except Exception as e:
                logger.warning(f"Não foi possível carregar BaseLegalSuggestorDECIPEx: {e}")
                self.suggestor_base_legal = None
        else:
            self.suggestor_base_legal = None

    @property
    def AREAS_DECIPEX(self) -> Dict[int, Dict[str, str]]:
        """Áreas da DECIPEX com códigos e prefixos"""
        return {
            1: {"codigo": "CGBEN", "nome": "Coordenação Geral de Benefícios", "prefixo": "1"},
            2: {"codigo": "CGPAG", "nome": "Coordenação Geral de Pagamentos", "prefixo": "2"},
            3: {"codigo": "COATE", "nome": "Coordenação de Atendimento", "prefixo": "3"},
            4: {"codigo": "CGGAF", "nome": "Coordenação Geral de Gestão de Acervos Funcionais", "prefixo": "4"},
            5: {"codigo": "DIGEP", "nome": "Diretoria de Pessoal dos Ex-Territórios", "prefixo": "5"},
            6: {"codigo": "CGRIS", "nome": "Coordenação Geral de Riscos e Controle", "prefixo": "6"},
            7: {"codigo": "CGCAF", "nome": "Coordenação Geral de Gestão de Complementação da Folha", "prefixo": "7"},
            8: {"codigo": "CGECO", "nome": "Coordenação Geral de Extinção e Convênio", "prefixo": "8"}
        }

    @property
    def DESCRICOES_AREAS(self) -> Dict[str, str]:
        """Descrições personalizadas e acolhedoras de cada área da DECIPEX"""
        return {
            "CGBEN": "que cuida das concessões, manutenções e revisões de aposentadorias e pensões, garantindo direitos e segurança jurídica aos beneficiários.",
            "CGPAG": "responsável pela execução e controle da folha de pagamentos dos aposentados e pensionistas, garantindo que tudo ocorra com precisão e transparência.",
            "COATE": "que acolhe, orienta e soluciona as demandas dos cidadãos e servidores, garantindo um atendimento humano e eficiente.",
            "CGGAF": "que organiza, digitaliza e mantém o acervo funcional dos servidores, preservando a memória e o acesso seguro às informações.",
            "DIGEP": "que assegura os direitos dos servidores vinculados aos ex-territórios, conduzindo análises e gestões complexas com zelo e compromisso histórico.",
            "CGRIS": "que fortalece a governança, os controles internos e a integridade institucional, promovendo uma gestão pública mais segura e eficiente.",
            "CGCAF": "responsável pela gestão das complementações de aposentadorias e pensões, garantindo equilíbrio e correção dos pagamentos.",
            "CGECO": "que gerencia processos de encerramento de órgãos e acordos administrativos, preservando a continuidade institucional e a responsabilidade pública."
        }

    @property
    def SISTEMAS_DECIPEX(self) -> Dict[str, List[str]]:
        """Sistemas organizados por categoria"""
        return {
            "gestao_pessoal": ["SIAPE", "E-SIAPE", "SIGEPE", "SIGEP - AFD", "E-Pessoal TCU", "SIAPNET", "SIGAC"],
            "documentos": ["SEI", "DOINET", "DOU", "SOUGOV", "PETRVS"],
            "transparencia": ["Portal da Transparência", "CNIS", "Site CGU-PAD", "Sistema de Pesquisa Integrada do TCU", "Consulta CPF RFB"],
            "previdencia": ["SISTEMA COMPREV", "BG COMPREV"],
            "comunicacao": ["TEAMS", "OUTLOOK"],
            "outros": ["DW"]
        }

    @property
    def OPERADORES_DECIPEX(self) -> List[str]:
        """Operadores padrão da DECIPEX"""
        return [
            "Técnico Especializado",
            "Coordenador-Geral",
            "Coordenador",
            "Apoio-gabinete",
            "Equipe técnica",
            "Outros (especificar)"
        ]

    def inicializar_estado(self, skip_intro: bool = False) -> dict:
        """
        Inicializa estado limpo para Helena POP

        Args:
            skip_intro: Se True, pula a introdução e vai direto para NOME_USUARIO
                       (usado quando frontend já mostrou mensagem de boas-vindas)

        Returns:
            dict: Estado inicial com POPStateMachine
        """
        sm = POPStateMachine()

        # Se frontend já mostrou introdução, pular para coleta de nome
        if skip_intro:
            sm.estado = EstadoPOP.NOME_USUARIO

        return sm.to_dict()

    def processar(self, mensagem: str, session_data: dict) -> dict:
        """
        Processa mensagem do usuário de acordo com o estado atual

        Args:
            mensagem: Texto do usuário
            session_data: Estado atual da sessão

        Returns:
            dict: Resposta com novo estado
        """
        # Validações
        self.validar_mensagem(mensagem)
        self.validar_session_data(session_data)

        # Carregar state machine
        sm = POPStateMachine.from_dict(session_data)

        # Processar de acordo com o estado
        if sm.estado == EstadoPOP.BOAS_VINDAS:
            resposta, novo_sm = self._processar_boas_vindas(mensagem, sm)

        elif sm.estado == EstadoPOP.NOME_USUARIO:
            resposta, novo_sm = self._processar_nome_usuario(mensagem, sm)

        elif sm.estado == EstadoPOP.CONFIRMA_NOME:
            resposta, novo_sm = self._processar_confirma_nome(mensagem, sm)

        elif sm.estado == EstadoPOP.PRE_EXPLICACAO:
            resposta, novo_sm = self._processar_pre_explicacao(mensagem, sm)

        elif sm.estado == EstadoPOP.EXPLICACAO:
            resposta, novo_sm = self._processar_explicacao(mensagem, sm)

        elif sm.estado == EstadoPOP.EXPLICACAO_FINAL:
            resposta, novo_sm = self._processar_explicacao_final(mensagem, sm)

        elif sm.estado == EstadoPOP.AREA_DECIPEX:
            resposta, novo_sm = self._processar_area_decipex(mensagem, sm)

        elif sm.estado == EstadoPOP.ARQUITETURA:
            resposta, novo_sm = self._processar_arquitetura(mensagem, sm)

        elif sm.estado == EstadoPOP.NOME_PROCESSO:
            resposta, novo_sm = self._processar_nome_processo(mensagem, sm)

        elif sm.estado == EstadoPOP.ENTREGA_ESPERADA:
            resposta, novo_sm = self._processar_entrega_esperada(mensagem, sm)

        elif sm.estado == EstadoPOP.DISPOSITIVOS_NORMATIVOS:
            resposta, novo_sm = self._processar_dispositivos_normativos(mensagem, sm)

        elif sm.estado == EstadoPOP.OPERADORES:
            resposta, novo_sm = self._processar_operadores(mensagem, sm)

        elif sm.estado == EstadoPOP.SISTEMAS:
            resposta, novo_sm = self._processar_sistemas(mensagem, sm)

        elif sm.estado == EstadoPOP.DOCUMENTOS:
            resposta, novo_sm = self._processar_documentos(mensagem, sm)

        elif sm.estado == EstadoPOP.FLUXOS:
            resposta, novo_sm = self._processar_fluxos(mensagem, sm)

        elif sm.estado == EstadoPOP.TRANSICAO_EPICA:
            resposta, novo_sm = self._processar_transicao_epica(mensagem, sm)

        elif sm.estado == EstadoPOP.DELEGACAO_ETAPAS:
            resposta, novo_sm = self._processar_delegacao_etapas(mensagem, sm)

        else:
            resposta = "Estado desconhecido. Vamos recomeçar?"
            novo_sm = POPStateMachine()

        # Calcular progresso
        progresso = self._calcular_progresso(novo_sm)
        progresso_detalhado = self.obter_progresso(novo_sm)

        # Verificar se deve sugerir mudança de contexto
        sugerir_contexto = None
        if novo_sm.estado == EstadoPOP.DELEGACAO_ETAPAS or novo_sm.concluido:
            sugerir_contexto = 'etapas'

        # Adicionar badge de conquista se chegou na transição épica
        metadados_extra = {
            'progresso_detalhado': progresso_detalhado
        }

        # Badge de conquista na transição épica
        if novo_sm.estado == EstadoPOP.TRANSICAO_EPICA:
            metadados_extra['badge'] = {
                'tipo': 'fase_previa_completa',
                'emoji': '🏆',
                'titulo': 'Fase Prévia Concluída!',
                'descricao': 'Você mapeou toda a estrutura básica do processo',
                'mostrar_animacao': True
            }

        # 🎯 Definir interface dinâmica baseada no estado
        tipo_interface = None
        dados_interface = None

        if novo_sm.estado == EstadoPOP.AREA_DECIPEX:
            tipo_interface = 'areas'
            dados_interface = {
                'opcoes_areas': {
                    str(num): {'codigo': info['codigo'], 'nome': info['nome']}
                    for num, info in self.AREAS_DECIPEX.items()
                }
            }

        return self.criar_resposta(
            resposta=resposta,
            novo_estado=novo_sm.to_dict(),
            progresso=progresso,
            sugerir_contexto=sugerir_contexto,
            metadados=metadados_extra,
            tipo_interface=tipo_interface,
            dados_interface=dados_interface
        )

    # ========================================================================
    # PROCESSADORES DE ESTADO
    # ========================================================================

    def _processar_boas_vindas(self, _mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa estado inicial de boas-vindas"""
        sm.estado = EstadoPOP.NOME_USUARIO
        resposta = (
            "👋 Olá! Sou a Helena, assistente de IA da DECIPEX especializada em mapeamento de processos.\n\n"
            "Vou te ajudar a documentar seu procedimento de forma clara e estruturada, pergunta por pergunta.\n\n"
            "Para começarmos, qual seu nome?"
        )
        return resposta, sm

    def _processar_nome_usuario(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa coleta do nome do usuário"""
        sm.nome_temporario = mensagem.strip()
        sm.estado = EstadoPOP.CONFIRMA_NOME
        resposta = (
            f"Olá, {sm.nome_temporario}! Prazer em te conhecer. Fico feliz que você tenha aceitado "
            f"essa missão de documentar nossos processos.\n\n"
            f"Antes de continuarmos, me confirma, posso te chamar de {sm.nome_temporario} mesmo? "
            f"(Digite SIM ou NÃO)"
        )
        return resposta, sm

    def _processar_confirma_nome(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa confirmação do nome"""
        msg_lower = mensagem.lower().strip()

        if any(palavra in msg_lower for palavra in ['sim', 's', 'pode', 'ok', 'claro']):
            sm.nome_usuario = sm.nome_temporario
            sm.estado = EstadoPOP.PRE_EXPLICACAO

            resposta = f"Ótimo então {sm.nome_usuario}, antes de seguir preciso explicar algumas coisas ok?"
        else:
            sm.estado = EstadoPOP.NOME_USUARIO
            resposta = "Sem problemas! Como você prefere que eu te chame?"

        return resposta, sm

    def _processar_pre_explicacao(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Aguarda confirmação antes de explicar o processo"""
        msg_lower = mensagem.lower().strip()

        respostas_positivas = ['sim', 's', 'ok', 'pode', 'claro', 'vamos', 'yes', 'uhum', 'aham', 'beleza', 'tudo bem', 'sigo']

        if msg_lower in respostas_positivas:
            sm.estado = EstadoPOP.EXPLICACAO
            resposta = (
                f"Nesse chat eu vou conduzir uma conversa guiada. A intenção é preencher esse formulário "
                f"de Procedimento Operacional Padrão - POP aí do lado. Tá vendo? Aproveita pra conhecer.\n\n"
                f"Nossa meta é entregar esse POP prontinho. Vamos continuar? (digite sim que seguimos em frente)"
            )
        else:
            resposta = "Sem problemas! Quando você estiver pronto pra ouvir, é só me dizer 'ok' ou 'pode'."

        return resposta, sm

    def _processar_explicacao(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Confirma que está tudo claro e pronto para começar"""
        msg_lower = mensagem.lower().strip()

        respostas_positivas = ['sim', 's', 'pode', 'ok', 'claro', 'vamos', 'yes', 'uhum', 'aham', 'beleza', 'entendi', 'bora', 'vamo', 'pronta', 'pronto']

        if msg_lower in respostas_positivas:
            sm.estado = EstadoPOP.EXPLICACAO_FINAL
            resposta = (
                f"Mas {sm.nome_usuario}, se ao olhar o formulário você ficou com dúvida em algum campo, "
                f"quero te tranquilizar! Essa missão é em dupla e você pode sempre acionar o botão "
                f"'Preciso de Ajuda' que eu entro em ação!\n\n"
                f"Digite sim pra gente continuar."
            )
        else:
            resposta = f"Tudo bem! Só posso seguir quando você me disser 'sim', {sm.nome_usuario}. Quando quiser continuar, é só digitar."

        return resposta, sm

    def _processar_explicacao_final(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa explicação final e avança para seleção de área"""
        msg_lower = mensagem.lower().strip()

        respostas_positivas = ['sim', 's', 'pode', 'ok', 'claro', 'vamos', 'beleza', 'continuar']

        if msg_lower in respostas_positivas:
            sm.estado = EstadoPOP.AREA_DECIPEX

            # 🎯 RETORNAR INTERFACE DE CARDS ao invés de texto
            # A resposta será processada pelo processar() principal
            resposta = f"Perfeito, {sm.nome_usuario}!"
        else:
            resposta = f"Sem pressa, {sm.nome_usuario}! Quando estiver pronto, é só digitar 'sim'."

        return resposta, sm

    def _processar_area_decipex(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa seleção da área DECIPEX"""
        try:
            numero = int(mensagem.strip())
            if numero in self.AREAS_DECIPEX:
                sm.area_selecionada = self.AREAS_DECIPEX[numero]
                sm.estado = EstadoPOP.ARQUITETURA

                # Buscar descrição personalizada da área
                codigo_area = sm.area_selecionada['codigo']
                descricao_area = self.DESCRICOES_AREAS.get(codigo_area, "")

                resposta = (
                    f"Ótimo, {sm.nome_usuario}! 🌿\n"
                    f"Você faz parte da **{sm.area_selecionada['nome']}**, {descricao_area}\n\n"
                    "Agora vamos definir juntos o **macroprocesso, processo, subprocesso, atividade e entrega final** da sua rotina.\n\n"
                    "✍️ Pra isso, me conte em uma frase o que você faz por aqui — pode ser algo simples, tipo:\n"
                    "• 'Analiso pensões'\n"
                    "• 'Faço reposição ao erário'\n"
                    "• 'Cadastro atos de aposentadoria'"
                )
            else:
                resposta = (
                    "Número inválido. Por favor, digite um número de 1 a 8 correspondente "
                    "a uma das áreas listadas acima."
                )
        except ValueError:
            resposta = (
                "Por favor, digite apenas o número da área (de 1 a 8)."
            )

        return resposta, sm

    def _processar_arquitetura(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Processa navegação na arquitetura DECIPEX usando Helena Mapeamento (IA)

        A IA sugere:
        - Macroprocesso
        - Processo
        - Subprocesso
        - Atividade
        - Entrega Final
        """
        descricao_usuario = mensagem.strip()

        # Validação: mínimo 10 caracteres
        if len(descricao_usuario) < 10:
            resposta = (
                "Por favor, descreva sua atividade com mais detalhes (mínimo 10 caracteres).\n\n"
                "Exemplo: 'Analiso requerimentos de auxílio saúde de aposentados'"
            )
            return resposta, sm

        # Chamar Helena Ajuda Inteligente para sugerir arquitetura + entrega
        try:
            from processos.domain.helena_produtos.helena_ajuda_inteligente import analisar_atividade_com_helena

            # Montar contexto
            area_nome = sm.area_selecionada['nome']
            area_codigo = sm.area_selecionada['codigo']

            contexto = {
                'area': area_nome,
                'area_codigo': area_codigo
            }

            logger.info("Chamando Helena Ajuda Inteligente para sugerir arquitetura + entrega")

            # Chamar Helena - ela sugere desde macroprocesso até resultado final
            resultado = analisar_atividade_com_helena(
                descricao_usuario=descricao_usuario,
                nivel_atual='completo',  # Pedir sugestão completa
                contexto_ja_selecionado=contexto
            )

            # Verificar se obteve sucesso
            if not resultado.get('sucesso'):
                raise ValueError("Helena não conseguiu analisar a descrição")

            sugestao = resultado['sugestao']

            # Validar sugestão
            campos_obrigatorios = ['macroprocesso', 'processo', 'subprocesso', 'atividade', 'resultado_final']
            if not all(campo in sugestao for campo in campos_obrigatorios):
                raise ValueError("Sugestão incompleta da IA")

            # Salvar sugestão no state machine
            sm.macro_selecionado = sugestao['macroprocesso']
            sm.processo_selecionado = sugestao['processo']
            sm.subprocesso_selecionado = sugestao['subprocesso']
            sm.atividade_selecionada = sugestao['atividade']
            sm.dados_coletados['nome_processo'] = sugestao['atividade']
            sm.dados_coletados['entrega_esperada'] = sugestao['resultado_final']

            # Salvar dados de arquitetura
            sm.dados_coletados['macroprocesso'] = sugestao['macroprocesso']
            sm.dados_coletados['processo'] = sugestao['processo']
            sm.dados_coletados['subprocesso'] = sugestao['subprocesso']
            sm.dados_coletados['atividade'] = sugestao['atividade']

            # Avançar para próximo estado (dispositivos normativos)
            sm.estado = EstadoPOP.DISPOSITIVOS_NORMATIVOS

            # Mapear confiança para emoji
            confianca = resultado.get('confianca', 'media')
            emoji_confianca = "🎯" if confianca == 'alta' else "🤔" if confianca == 'media' else "💭"

            justificativa = resultado.get('justificativa', '')

            resposta = (
                f"{emoji_confianca} Analisando o que você faz, sugiro essa classificação:\n\n"
                f"**Arquitetura:**\n"
                f"• Macroprocesso: {sugestao['macroprocesso']}\n"
                f"• Processo: {sugestao['processo']}\n"
                f"• Subprocesso: {sugestao['subprocesso']}\n"
                f"• Atividade: {sugestao['atividade']}\n\n"
                f"**Entrega Final:**\n"
                f"• {sugestao['resultado_final']}\n\n"
            )

            if justificativa:
                resposta += f"💡 **Justificativa:** {justificativa}\n\n"

            resposta += "Se concordar, digite 'sim' para continuar.\nSe quiser ajustar algo, digite 'ajustar'."

            logger.info(f"✅ Helena Ajuda Inteligente sugeriu: {sugestao['atividade']} → {sugestao['resultado_final']}")

        except Exception as e:
            logger.error(f"Erro ao sugerir arquitetura com Helena: {e}")
            import traceback
            traceback.print_exc()

            # Fallback: pedir manualmente
            sm.estado = EstadoPOP.NOME_PROCESSO
            resposta = (
                "Desculpe, tive dificuldade em processar sua descrição.\n\n"
                "Pode me dizer de forma mais direta: qual é o nome completo da atividade que você quer mapear?\n\n"
                "Ex: 'Conceder ressarcimento a aposentado civil', 'Análise de requerimento de auxílio alimentação'"
            )

        return resposta, sm

    def _processar_nome_processo(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa coleta do nome do processo"""
        sm.dados_coletados['nome_processo'] = mensagem.strip()
        sm.estado = EstadoPOP.ENTREGA_ESPERADA

        resposta = (
            f"Perfeito! Vamos mapear: '{sm.dados_coletados['nome_processo']}'\n\n"
            "Agora me diga: qual é o resultado final desta atividade?\n\n"
            "Ex: 'Auxílio concedido', 'Requerimento analisado e decidido', 'Cadastro atualizado'"
        )
        return resposta, sm

    def _processar_entrega_esperada(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa coleta da entrega esperada"""
        sm.dados_coletados['entrega_esperada'] = mensagem.strip()
        sm.estado = EstadoPOP.DISPOSITIVOS_NORMATIVOS

        # Tentar sugerir base legal se disponível
        sugestoes_texto = ""
        if self.suggestor_base_legal:
            try:
                sugestoes = self.suggestor_base_legal.sugerir_normas(
                    sm.dados_coletados['nome_processo']
                )
                if sugestoes:
                    sugestoes_texto = "\n\nAlgumas normas relevantes que identifiquei:\n"
                    for i, norma in enumerate(sugestoes[:3], 1):
                        sugestoes_texto += f"{i}. {norma}\n"
                    sugestoes_texto += "\nVocê pode usar essas sugestões ou mencionar outras normas."
            except Exception as e:
                logger.warning(f"Erro ao sugerir normas: {e}")

        resposta = (
            f"Entendi! A entrega esperada é: '{sm.dados_coletados['entrega_esperada']}'\n\n"
            "Agora, quais são as principais normas que regulam esta atividade?\n\n"
            "Ex: 'Art. 34 da IN SGP/SEDGG/ME nº 97/2022', 'Lei 8.112/90'"
            f"{sugestoes_texto}\n\n"
            "Digite as normas (separadas por vírgula ou em linhas separadas):"
        )
        return resposta, sm

    def _processar_dispositivos_normativos(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa coleta de dispositivos normativos"""
        # Separar por vírgula ou quebra de linha
        normas = [n.strip() for n in mensagem.replace('\n', ',').split(',') if n.strip()]
        sm.dados_coletados['dispositivos_normativos'] = normas
        sm.estado = EstadoPOP.OPERADORES

        # Montar lista de operadores
        operadores_texto = "\n".join([
            f"{i+1}. {op}"
            for i, op in enumerate(self.OPERADORES_DECIPEX)
        ])

        resposta = (
            f"Ótimo! Registrei {len(normas)} norma(s).\n\n"
            "Agora, quem são os responsáveis por executar esta atividade?\n\n"
            f"{operadores_texto}\n\n"
            "Digite os números correspondentes (separados por vírgula) ou descreva outros operadores:"
        )
        return resposta, sm

    def _processar_operadores(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa coleta de operadores"""
        # Tentar interpretar números
        operadores = []
        partes = [p.strip() for p in mensagem.replace('\n', ',').split(',')]

        for parte in partes:
            try:
                num = int(parte)
                if 1 <= num <= len(self.OPERADORES_DECIPEX):
                    operadores.append(self.OPERADORES_DECIPEX[num - 1])
            except ValueError:
                # Não é número, adicionar como texto
                if parte:
                    operadores.append(parte)

        sm.dados_coletados['operadores'] = operadores
        sm.estado = EstadoPOP.SISTEMAS

        # Montar lista de sistemas por categoria
        sistemas_texto = ""
        for categoria, sistemas in self.SISTEMAS_DECIPEX.items():
            categoria_nome = categoria.replace('_', ' ').title()
            sistemas_texto += f"\n**{categoria_nome}:**\n"
            sistemas_texto += ", ".join(sistemas) + "\n"

        resposta = (
            f"Perfeito! Registrei {len(operadores)} operador(es).\n\n"
            "Agora, quais sistemas são utilizados nesta atividade?\n\n"
            f"{sistemas_texto}\n\n"
            "Digite os nomes dos sistemas (separados por vírgula):"
        )
        return resposta, sm

    def _processar_sistemas(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa coleta de sistemas"""
        sistemas = [s.strip() for s in mensagem.replace('\n', ',').split(',') if s.strip()]
        sm.dados_coletados['sistemas'] = sistemas
        sm.estado = EstadoPOP.DOCUMENTOS

        resposta = (
            f"Ótimo! Registrei {len(sistemas)} sistema(s).\n\n"
            "Agora, quais documentos são utilizados ou gerados nesta atividade?\n\n"
            "Ex: 'Processo SEI', 'Formulário de requerimento', 'Despacho decisório'\n\n"
            "Digite os documentos (separados por vírgula ou digite 'nenhum' se não houver):"
        )
        return resposta, sm

    def _processar_documentos(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa coleta de documentos"""
        msg_lower = mensagem.lower().strip()

        if msg_lower in ['nenhum', 'nao', 'não']:
            sm.dados_coletados['documentos'] = []
        else:
            documentos = [d.strip() for d in mensagem.replace('\n', ',').split(',') if d.strip()]
            sm.dados_coletados['documentos'] = documentos

        sm.estado = EstadoPOP.FLUXOS

        resposta = (
            f"Entendi! Registrei {len(sm.dados_coletados['documentos'])} documento(s).\n\n"
            "Agora, vamos falar sobre fluxos de informação.\n\n"
            "Quais informações ou dados ENTRAM nesta atividade?\n\n"
            "Ex: 'Requerimento do servidor', 'Dados do SIAPE', 'Parecer técnico'\n\n"
            "Digite os fluxos de entrada (separados por vírgula ou digite 'nenhum'):"
        )
        return resposta, sm

    def _processar_fluxos(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa coleta de fluxos (entrada e saída)"""
        msg_lower = mensagem.lower().strip()

        # Se ainda não coletou fluxos de entrada
        if not sm.dados_coletados.get('fluxos_entrada'):
            if msg_lower in ['nenhum', 'nao', 'não']:
                sm.dados_coletados['fluxos_entrada'] = []
            else:
                fluxos = [f.strip() for f in mensagem.replace('\n', ',').split(',') if f.strip()]
                sm.dados_coletados['fluxos_entrada'] = fluxos

            resposta = (
                f"Perfeito! Registrei {len(sm.dados_coletados['fluxos_entrada'])} fluxo(s) de entrada.\n\n"
                "E quais informações ou dados SAEM desta atividade?\n\n"
                "Ex: 'Decisão de concessão', 'Dados atualizados no sistema', 'Notificação ao servidor'\n\n"
                "Digite os fluxos de saída (separados por vírgula ou digite 'nenhum'):"
            )
        else:
            # Coletar fluxos de saída
            if msg_lower in ['nenhum', 'nao', 'não']:
                sm.dados_coletados['fluxos_saida'] = []
            else:
                fluxos = [f.strip() for f in mensagem.replace('\n', ',').split(',') if f.strip()]
                sm.dados_coletados['fluxos_saida'] = fluxos

            sm.estado = EstadoPOP.TRANSICAO_EPICA

            # Resumo dos dados coletados
            resumo = self._gerar_resumo_pop(sm)

            resposta = (
                f"Excelente! Coletamos todas as informações básicas do processo.\n\n"
                f"{resumo}\n\n"
                "Digite 'ok' ou 'continuar' quando estiver pronto para a próxima fase:"
            )

        return resposta, sm

    def _processar_transicao_epica(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """
        Estado de transição épica - Celebra conquistas e prepara para etapas detalhadas

        Inclui:
        - Troféu/badge de conquista
        - Mensagem motivacional
        - Dicas de preparação
        - Estimativa de tempo
        - Opção de pausa
        """
        msg_lower = mensagem.lower().strip()
        nome = sm.nome_usuario

        # Palavras que indicam continuidade
        continuar_palavras = ['ok', 'continuar', 'sim', 'vamos', 'próximo', 'seguir', 'bora', 'vai']

        # Palavras que indicam pausa
        pausa_palavras = ['pausa', 'pausar', 'esperar', 'depois', 'mais tarde', 'aguardar']

        if any(palavra in msg_lower for palavra in pausa_palavras):
            # Usuário quer pausar
            resposta = (
                f"Sem problemas, {nome}! 🤝\n\n"
                "Você pode retomar quando quiser. Seus dados estão salvos.\n\n"
                "Quando voltar, é só continuar de onde parou!\n\n"
                "Digite 'continuar' quando estiver pronto para a fase detalhada."
            )
            # Não muda o estado, fica esperando
            return resposta, sm

        elif any(palavra in msg_lower for palavra in continuar_palavras):
            # Usuário confirmou - avançar para delegação
            sm.estado = EstadoPOP.DELEGACAO_ETAPAS

            resposta = (
                f"🎯 **VAMOS COMEÇAR!**\n\n"
                f"Vou te transferir agora para o Helena Etapas, que é especializada em "
                f"detalhar cada etapa operacional.\n\n"
                f"Ela vai te guiar pergunta por pergunta. Boa sorte, {nome}! 🚀"
            )

            return resposta, sm

        else:
            # Primeira visita ou mensagem não reconhecida - mostrar transição épica
            progresso = self.obter_progresso(sm)
            percentual = progresso['percentual']

            resposta = (
                f"🏆 **PARABÉNS, {nome.upper()}!** 🏆\n\n"
                f"Você concluiu a **Fase Prévia** do mapeamento!\n\n"
                f"📊 **Progresso:** {percentual}% da estrutura básica está mapeada!\n\n"
                f"---\n\n"
                f"🎯 **PRÓXIMA MISSÃO: Detalhamento das Etapas**\n\n"
                f"Agora vem a parte mais detalhada: vamos mapear **cada etapa** do seu processo, "
                f"incluindo responsáveis, prazos, documentos e critérios de qualidade.\n\n"
                f"⏱️ **Tempo estimado:** 15-20 minutos\n\n"
                f"💡 **Dicas para essa fase:**\n"
                f"• Pegue um café/água antes de começar ☕\n"
                f"• Tenha exemplos reais em mente\n"
                f"• Pense em cada passo que você faz no dia a dia\n"
                f"• Se tiver dúvida, use o botão 'Preciso de Ajuda'\n\n"
                f"---\n\n"
                f"Digite:\n"
                f"• **'VAMOS'** para começar agora 🚀\n"
                f"• **'PAUSA'** para continuar depois 🤝"
            )

            return resposta, sm

    def _processar_delegacao_etapas(self, mensagem: str, sm: POPStateMachine) -> tuple[str, POPStateMachine]:
        """Processa delegação para Helena Etapas"""
        msg_lower = mensagem.lower().strip()

        if any(palavra in msg_lower for palavra in ['ok', 'continuar', 'sim', 'vamos', 'próximo']):
            sm.concluido = True
            sm.estado = EstadoPOP.FINALIZADO

            resposta = (
                f"Perfeito, {sm.nome_usuario}! Os dados iniciais do processo foram coletados com sucesso.\n\n"
                "Agora vou transferir você para o Helena Etapas para detalharmos cada etapa operacional.\n\n"
                "Até logo!"
            )
        else:
            resposta = (
                "Não entendi. Digite 'ok' ou 'continuar' para prosseguir para o detalhamento das etapas."
            )

        return resposta, sm

    # ========================================================================
    # HELPERS
    # ========================================================================

    def _calcular_progresso(self, sm: POPStateMachine) -> str:
        """
        Calcula progresso da coleta baseado em campos preenchidos (não estados).
        Retorna formato "X/13" onde 13 é o total de campos principais.
        """
        total_campos = 13  # Total de campos principais no POP
        campos_preenchidos = 0

        # Nome usuário
        if sm.nome_usuario:
            campos_preenchidos += 1

        # Área DECIPEX
        if sm.dados_coletados.get('area_decipex'):
            campos_preenchidos += 1

        # Arquitetura (macro/processo/subprocesso/atividade)
        if sm.dados_coletados.get('macroprocesso'):
            campos_preenchidos += 1
        if sm.dados_coletados.get('processo'):
            campos_preenchidos += 1
        if sm.dados_coletados.get('subprocesso'):
            campos_preenchidos += 1
        if sm.dados_coletados.get('atividade'):
            campos_preenchidos += 1

        # Nome do processo
        if sm.dados_coletados.get('nome_processo'):
            campos_preenchidos += 1

        # Entrega esperada
        if sm.dados_coletados.get('entrega_esperada'):
            campos_preenchidos += 1

        # Dispositivos normativos
        if sm.dados_coletados.get('dispositivos_normativos'):
            campos_preenchidos += 1

        # Operadores
        if sm.dados_coletados.get('operadores'):
            campos_preenchidos += 1

        # Sistemas
        if sm.dados_coletados.get('sistemas'):
            campos_preenchidos += 1

        # Documentos (entrada/saída)
        if sm.dados_coletados.get('documentos_entrada') or sm.dados_coletados.get('documentos_saida'):
            campos_preenchidos += 1

        # Fluxos (entrada/saída)
        if sm.dados_coletados.get('fluxos_entrada') or sm.dados_coletados.get('fluxos_saida'):
            campos_preenchidos += 1

        return f"{campos_preenchidos}/{total_campos}"

    def obter_progresso(self, sm: POPStateMachine) -> dict:
        """
        Retorna detalhes completos do progresso atual.

        Returns:
            dict: {
                "campos_preenchidos": int,
                "total_campos": int,
                "percentual": int (0-100),
                "estado_atual": str,
                "campos_faltantes": list[str],
                "completo": bool
            }
        """
        total_campos = 13
        campos_preenchidos = 0
        campos_faltantes = []

        # Mapear campos e verificar preenchimento
        campos_map = {
            'nome_usuario': ('Nome do usuário', sm.nome_usuario),
            'area_decipex': ('Área DECIPEX', sm.dados_coletados.get('area_decipex')),
            'macroprocesso': ('Macroprocesso', sm.dados_coletados.get('macroprocesso')),
            'processo': ('Processo', sm.dados_coletados.get('processo')),
            'subprocesso': ('Subprocesso', sm.dados_coletados.get('subprocesso')),
            'atividade': ('Atividade', sm.dados_coletados.get('atividade')),
            'nome_processo': ('Nome do processo', sm.dados_coletados.get('nome_processo')),
            'entrega_esperada': ('Entrega esperada', sm.dados_coletados.get('entrega_esperada')),
            'dispositivos_normativos': ('Dispositivos normativos', sm.dados_coletados.get('dispositivos_normativos')),
            'operadores': ('Operadores', sm.dados_coletados.get('operadores')),
            'sistemas': ('Sistemas', sm.dados_coletados.get('sistemas')),
            'documentos': ('Documentos', sm.dados_coletados.get('documentos_entrada') or sm.dados_coletados.get('documentos_saida')),
            'fluxos': ('Fluxos', sm.dados_coletados.get('fluxos_entrada') or sm.dados_coletados.get('fluxos_saida')),
        }

        for campo_id, (campo_nome, valor) in campos_map.items():
            if valor:
                campos_preenchidos += 1
            else:
                campos_faltantes.append(campo_nome)

        percentual = int((campos_preenchidos / total_campos) * 100)

        return {
            "campos_preenchidos": campos_preenchidos,
            "total_campos": total_campos,
            "percentual": percentual,
            "estado_atual": sm.estado.value,
            "campos_faltantes": campos_faltantes,
            "completo": sm.estado == EstadoPOP.DELEGACAO_ETAPAS or percentual == 100
        }

    def _gerar_resumo_pop(self, sm: POPStateMachine) -> str:
        """Gera resumo dos dados coletados"""
        dados = sm.dados_coletados

        resumo = "**RESUMO DO PROCESSO**\n\n"
        resumo += f"**Área:** {sm.area_selecionada['nome']}\n"
        resumo += f"**Processo:** {dados['nome_processo']}\n"
        resumo += f"**Entrega:** {dados['entrega_esperada']}\n"
        resumo += f"**Normas:** {', '.join(dados['dispositivos_normativos'])}\n"
        resumo += f"**Operadores:** {', '.join(dados['operadores'])}\n"
        resumo += f"**Sistemas:** {', '.join(dados['sistemas'])}\n"

        if dados.get('documentos'):
            resumo += f"**Documentos:** {', '.join(dados['documentos'])}\n"

        if dados.get('fluxos_entrada'):
            resumo += f"**Entradas:** {', '.join(dados['fluxos_entrada'])}\n"

        if dados.get('fluxos_saida'):
            resumo += f"**Saídas:** {', '.join(dados['fluxos_saida'])}\n"

        return resumo

    def receber_dados(self, dados_etapas: dict) -> dict:
        """
        Recebe dados de volta do Helena Etapas (quando concluir)

        Args:
            dados_etapas: Etapas coletadas pelo Helena Etapas

        Returns:
            dict: Dados consolidados do processo completo
        """
        logger.info("Helena POP recebendo dados consolidados do Helena Etapas")

        # TODO: Consolidar dados do POP + Etapas
        # TODO: Gerar documento final
        # TODO: Oferecer próximos passos (fluxograma, riscos, etc.)

        return {
            'sucesso': True,
            'mensagem': 'Processo mapeado com sucesso!',
            'dados_consolidados': dados_etapas
        }
