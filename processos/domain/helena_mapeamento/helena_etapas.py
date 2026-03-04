"""
Helena Etapas v2.0 - Mapeamento Completo e Granular de Etapas Operacionais

RESPONSABILIDADES:
- Mapear etapas REAIS do processo (da entrada até a saída)
- Coletar informações DETALHADAS por etapa:
  * Descrição
  * Responsável (operador)
  * Sistemas utilizados
  * Documentos requeridos (analisados/recebidos)
  * Documentos gerados (produzidos)
  * Tempo estimado
  * Condicionais (decisões/cenários com subetapas)

IMPORTANTE:
- Não usa PMBOK (Iniciação, Planejamento, etc.)
- Coleta etapas dinâmicas conforme o processo real
- Retorna dados consolidados para Helena POP
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum
import json
import logging

from processos.domain.base import BaseHelena

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class EstadoEtapa(str, Enum):
    """Estados da máquina de estados para coleta de uma etapa"""
    DESCRICAO = "descricao"
    OPERADOR = "operador"
    SISTEMAS = "sistemas"
    DOCS_REQUERIDOS = "docs_requeridos"
    DOCS_GERADOS = "docs_gerados"
    TEMPO_ESTIMADO = "tempo_estimado"
    PERGUNTA_CONDICIONAL = "pergunta_condicional"
    TIPO_CONDICIONAL = "tipo_condicional"
    ANTES_DECISAO = "antes_decisao"
    CENARIOS = "cenarios"
    SUBETAPAS_CENARIO = "subetapas_cenario"
    DETALHES = "detalhes"
    FINALIZADA = "finalizada"


# =============================================================================
# MODELOS DE DOMÍNIO
# =============================================================================

@dataclass
class Subetapa:
    """Subetapa dentro de um cenário condicional"""
    numero: str
    descricao: str

    def to_dict(self) -> Dict[str, str]:
        return {"numero": self.numero, "descricao": self.descricao}


@dataclass
class Cenario:
    """Cenário condicional de uma etapa"""
    numero: str
    descricao: str
    subetapas: List[Subetapa] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "numero": self.numero,
            "descricao": self.descricao,
            "subetapas": [s.to_dict() for s in self.subetapas]
        }


@dataclass
class Etapa:
    """
    Etapa completa de um processo (linear ou condicional)

    Campos comuns:
    - numero, descricao, operador
    - sistemas, docs_requeridos, docs_gerados, tempo_estimado

    Etapa linear:
    - detalhes: List[str]

    Etapa condicional:
    - tipo_condicional, antes_decisao, cenarios
    """
    numero: str
    descricao: str
    operador: str
    sistemas: List[str] = field(default_factory=list)
    docs_requeridos: List[str] = field(default_factory=list)
    docs_gerados: List[str] = field(default_factory=list)
    tempo_estimado: Optional[str] = None
    detalhes: List[str] = field(default_factory=list)

    # Campos condicionais
    tipo: Optional[str] = None  # "condicional" ou None
    tipo_condicional: Optional[str] = None  # "binario" ou "multiplos"
    antes_decisao: Optional[Dict[str, str]] = None
    cenarios: List[Cenario] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Converte para formato canonico (schema_version=1)"""
        base = {
            "numero": self.numero,
            # Canonicos
            "acao_principal": self.descricao,
            "operador_nome": self.operador,
            "sistemas": self.sistemas,
            "docs_requeridos": self.docs_requeridos,
            "docs_gerados": self.docs_gerados,
            "tempo_estimado": self.tempo_estimado,
            # Aliases retrocompat
            "descricao": self.descricao,
        }

        if self.tipo == "condicional":
            base.update({
                "tipo": "condicional",
                "tipo_condicional": self.tipo_condicional,
                "antes_decisao": self.antes_decisao,
                "cenarios": [c.to_dict() for c in self.cenarios]
            })
        else:
            base["verificacoes"] = self.detalhes
            base["detalhes"] = self.detalhes  # alias retrocompat

        return base


# =============================================================================
# STATE MACHINE - COLETA DE UMA ETAPA
# =============================================================================

class EtapaStateMachine:
    """
    Máquina de estados para coletar UMA etapa completa.

    Fluxo:
    DESCRICAO → OPERADOR → SISTEMAS → DOCS_REQUERIDOS → DOCS_GERADOS →
    TEMPO_ESTIMADO → PERGUNTA_CONDICIONAL
      ├─ NÃO → DETALHES → FINALIZADA
      └─ SIM → TIPO_CONDICIONAL → ANTES_DECISAO → CENARIOS →
               SUBETAPAS_CENARIO → FINALIZADA
    """

    def __init__(
        self,
        numero_etapa: int,
        sistemas_disponiveis: List[str] = None,
        operadores_disponiveis: List[str] = None
    ):
        self.numero = numero_etapa
        self.sistemas_disponiveis = sistemas_disponiveis or []
        self.operadores_disponiveis = operadores_disponiveis or []
        self.estado = EstadoEtapa.DESCRICAO

        # Dados coletados
        self.descricao = ""
        self.operador: Optional[str] = None
        self.sistemas: List[str] = []
        self.docs_requeridos: List[str] = []
        self.docs_gerados: List[str] = []
        self.tempo_estimado: Optional[str] = None
        self.tem_condicionais: Optional[bool] = None
        self.tipo_condicional: Optional[str] = None
        self.antes_decisao: Optional[str] = None
        self.cenarios: List[Cenario] = []
        self.detalhes: List[str] = []

        # Controle interno
        self._cenario_index = 0
        # Indice da etapa em etapas_coletadas (para merge de condicionais via form)
        self.etapa_index: Optional[int] = None

    @classmethod
    def start_condicional(
        cls,
        numero_etapa: int,
        etapa_index: int,
        operadores_disponiveis: List[str] = None
    ) -> 'EtapaStateMachine':
        """
        Cria SM ja no estado TIPO_CONDICIONAL para coletar apenas
        a parte condicional (cenarios/subetapas).
        Os campos lineares ja foram coletados pelo form.
        """
        sm = cls(
            numero_etapa=numero_etapa,
            operadores_disponiveis=operadores_disponiveis,
        )
        sm.estado = EstadoEtapa.TIPO_CONDICIONAL
        sm.tem_condicionais = True
        sm.etapa_index = etapa_index
        return sm

    def processar(self, mensagem: str) -> Dict[str, Any]:
        """
        Processa mensagem e transita entre estados.

        Returns:
            Sinais para o adaptador UI:
            - {"proximo": "OPERADOR"} → avançou
            - {"pergunta": "sistemas"} → fazer pergunta
            - {"status": "finalizada"} → concluído
        """
        handlers = {
            EstadoEtapa.DESCRICAO: self._processar_descricao,
            EstadoEtapa.OPERADOR: self._processar_operador,
            EstadoEtapa.SISTEMAS: self._processar_sistemas,
            EstadoEtapa.DOCS_REQUERIDOS: self._processar_docs_requeridos,
            EstadoEtapa.DOCS_GERADOS: self._processar_docs_gerados,
            EstadoEtapa.TEMPO_ESTIMADO: self._processar_tempo_estimado,
            EstadoEtapa.PERGUNTA_CONDICIONAL: self._processar_pergunta_condicional,
            EstadoEtapa.TIPO_CONDICIONAL: self._processar_tipo_condicional,
            EstadoEtapa.ANTES_DECISAO: self._processar_antes_decisao,
            EstadoEtapa.CENARIOS: self._processar_cenarios,
            EstadoEtapa.SUBETAPAS_CENARIO: self._processar_subetapas_cenario,
            EstadoEtapa.DETALHES: self._processar_detalhes,
        }

        handler = handlers.get(self.estado)
        if handler:
            return handler(mensagem)
        else:
            return {"erro": f"Estado desconhecido: {self.estado}"}

    def completa(self) -> bool:
        """Retorna True se etapa foi completamente coletada"""
        return self.estado == EstadoEtapa.FINALIZADA

    def obter_etapa(self) -> Etapa:
        """Retorna objeto Etapa completo"""
        if self.tem_condicionais:
            return Etapa(
                numero=str(self.numero),
                descricao=self.descricao,
                operador=self.operador or "Não especificado",
                sistemas=self.sistemas,
                docs_requeridos=self.docs_requeridos,
                docs_gerados=self.docs_gerados,
                tempo_estimado=self.tempo_estimado,
                tipo="condicional",
                tipo_condicional=self.tipo_condicional,
                antes_decisao={
                    "numero": f"{self.numero}.1",
                    "descricao": self.antes_decisao
                },
                cenarios=self.cenarios
            )
        else:
            return Etapa(
                numero=str(self.numero),
                descricao=self.descricao,
                operador=self.operador or "Não especificado",
                sistemas=self.sistemas,
                docs_requeridos=self.docs_requeridos,
                docs_gerados=self.docs_gerados,
                tempo_estimado=self.tempo_estimado,
                detalhes=self.detalhes
            )

    def obter_dict(self) -> Dict[str, Any]:
        """Retorna dicionário no formato esperado"""
        return self.obter_etapa().to_dict()

    def to_dict(self) -> Dict[str, Any]:
        """Serializa o state machine para JSON"""
        return {
            'numero': self.numero,
            'estado': self.estado.value if isinstance(self.estado, EstadoEtapa) else self.estado,
            'descricao': self.descricao,
            'operador': self.operador,
            'sistemas': self.sistemas,
            'docs_requeridos': self.docs_requeridos,
            'docs_gerados': self.docs_gerados,
            'tempo_estimado': self.tempo_estimado,
            'tem_condicionais': self.tem_condicionais,
            'tipo_condicional': self.tipo_condicional,
            'antes_decisao': self.antes_decisao,
            'cenarios': [c.to_dict() for c in self.cenarios],
            'detalhes': self.detalhes,
            '_cenario_index': self._cenario_index,
            'etapa_index': self.etapa_index,
            'sistemas_disponiveis': self.sistemas_disponiveis,
            'operadores_disponiveis': self.operadores_disponiveis
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EtapaStateMachine':
        """Deserializa o state machine do JSON"""
        sm = cls(
            numero_etapa=data['numero'],
            sistemas_disponiveis=data.get('sistemas_disponiveis', []),
            operadores_disponiveis=data.get('operadores_disponiveis', [])
        )
        sm.estado = EstadoEtapa(data['estado'])
        sm.descricao = data['descricao']
        sm.operador = data.get('operador_nome') or data.get('operador')
        sm.sistemas = data.get('sistemas', [])
        sm.docs_requeridos = data.get('docs_requeridos', [])
        sm.docs_gerados = data.get('docs_gerados', [])
        sm.tempo_estimado = data.get('tempo_estimado')
        sm.tem_condicionais = data.get('tem_condicionais')
        sm.tipo_condicional = data.get('tipo_condicional')
        sm.antes_decisao = data.get('antes_decisao')
        sm.detalhes = data.get('detalhes', [])
        sm._cenario_index = data.get('_cenario_index', 0)
        sm.etapa_index = data.get('etapa_index')

        # Reconstruir cenários
        cenarios_data = data.get('cenarios', [])
        for c_data in cenarios_data:
            cenario = Cenario(
                numero=c_data['numero'],
                descricao=c_data['descricao'],
                subetapas=[Subetapa(**s) for s in c_data.get('subetapas', [])]
            )
            sm.cenarios.append(cenario)

        return sm

    # =========================================================================
    # HANDLERS (um por estado)
    # =========================================================================

    def _processar_descricao(self, mensagem: str) -> Dict[str, Any]:
        """Coleta descrição da etapa"""
        self.descricao = mensagem.strip()
        self.estado = EstadoEtapa.OPERADOR
        return {"proximo": "OPERADOR", "descricao": self.descricao}

    def _processar_operador(self, mensagem: str) -> Dict[str, Any]:
        """Coleta responsável pela execução"""
        self.operador = mensagem.strip()
        self.estado = EstadoEtapa.SISTEMAS
        return {"pergunta": "sistemas", "operador": self.operador}

    def _processar_sistemas(self, mensagem: str) -> Dict[str, Any]:
        """Coleta sistemas utilizados nesta etapa"""
        msg_lower = mensagem.lower().strip()

        # Permite pular
        if msg_lower in ["não", "nao", "nenhum", "pular", "skip"]:
            self.sistemas = []
        else:
            # Pode ser lista separada por vírgula ou JSON
            try:
                data = json.loads(mensagem)
                self.sistemas = data.get("sistemas", [])
            except json.JSONDecodeError:
                # Texto livre separado por vírgula
                self.sistemas = [s.strip() for s in mensagem.split(',') if s.strip()]

        self.estado = EstadoEtapa.DOCS_REQUERIDOS
        return {"pergunta": "docs_requeridos", "sistemas": self.sistemas}

    def _processar_docs_requeridos(self, mensagem: str) -> Dict[str, Any]:
        """Coleta documentos analisados/requeridos"""
        msg_lower = mensagem.lower().strip()

        if msg_lower in ["não", "nao", "nenhum", "pular", "skip"]:
            self.docs_requeridos = []
        else:
            try:
                data = json.loads(mensagem)
                self.docs_requeridos = data.get("docs_requeridos", [])
            except json.JSONDecodeError:
                self.docs_requeridos = [d.strip() for d in mensagem.split(',') if d.strip()]

        self.estado = EstadoEtapa.DOCS_GERADOS
        return {"pergunta": "docs_gerados", "docs_requeridos": self.docs_requeridos}

    def _processar_docs_gerados(self, mensagem: str) -> Dict[str, Any]:
        """Coleta documentos produzidos/gerados"""
        msg_lower = mensagem.lower().strip()

        if msg_lower in ["não", "nao", "nenhum", "pular", "skip"]:
            self.docs_gerados = []
        else:
            try:
                data = json.loads(mensagem)
                self.docs_gerados = data.get("docs_gerados", [])
            except json.JSONDecodeError:
                self.docs_gerados = [d.strip() for d in mensagem.split(',') if d.strip()]

        # Pular tempo por etapa — tempo total é perguntado após todas as etapas
        self.tempo_estimado = None
        self.estado = EstadoEtapa.PERGUNTA_CONDICIONAL
        return {"pergunta": "tem_condicionais", "docs_gerados": self.docs_gerados}

    def _processar_tempo_estimado(self, mensagem: str) -> Dict[str, Any]:
        """Coleta tempo estimado"""
        msg_lower = mensagem.lower().strip()

        if msg_lower in ["pular", "skip", "não sei", "nao sei"]:
            self.tempo_estimado = None
        else:
            self.tempo_estimado = mensagem.strip()

        self.estado = EstadoEtapa.PERGUNTA_CONDICIONAL
        return {"pergunta": "tem_condicionais", "tempo_estimado": self.tempo_estimado}

    def _processar_pergunta_condicional(self, mensagem: str) -> Dict[str, Any]:
        """Pergunta se tem condicionais"""
        msg_lower = mensagem.lower().strip()

        if msg_lower in ["sim", "s", "yes", "y"]:
            self.tem_condicionais = True
            self.estado = EstadoEtapa.TIPO_CONDICIONAL
            return {"pergunta": "tipo_condicional"}
        else:
            self.tem_condicionais = False
            self.estado = EstadoEtapa.DETALHES
            return {"pergunta": "detalhes"}

    def _processar_tipo_condicional(self, mensagem: str) -> Dict[str, Any]:
        """Coleta tipo de condicional"""
        msg_lower = mensagem.lower().strip()

        if "bin" in msg_lower or msg_lower in ["2", "dois"]:
            self.tipo_condicional = "binario"
        elif "mult" in msg_lower or msg_lower in ["3", "varios", "vários"]:
            self.tipo_condicional = "multiplos"
        else:
            return {"erro": "Responda 'binário' (2 cenários) ou 'múltiplos' (3+)"}

        self.estado = EstadoEtapa.ANTES_DECISAO
        return {"pergunta": "antes_decisao", "tipo_condicional": self.tipo_condicional}

    def _processar_antes_decisao(self, mensagem: str) -> Dict[str, Any]:
        """Coleta o que é feito antes da decisão"""
        self.antes_decisao = mensagem.strip()
        self.estado = EstadoEtapa.CENARIOS
        return {"pergunta": "cenarios", "antes_decisao": self.antes_decisao}

    def _processar_cenarios(self, mensagem: str) -> Dict[str, Any]:
        """Coleta descrição dos cenários"""
        try:
            data = json.loads(mensagem)
            cenarios_data = data.get("cenarios", [])

            # Validar número de cenários
            if self.tipo_condicional == "binario" and len(cenarios_data) != 2:
                return {"erro": "Para binário, forneça exatamente 2 cenários"}

            if self.tipo_condicional == "multiplos" and len(cenarios_data) < 3:
                return {"erro": "Para múltiplos, forneça pelo menos 3 cenários"}

            # Criar objetos Cenario
            for i, c in enumerate(cenarios_data, start=1):
                cenario = Cenario(
                    numero=f"{self.numero}.{i+1}",
                    descricao=c.get("descricao", ""),
                    subetapas=[]
                )
                self.cenarios.append(cenario)

            # Iniciar coleta de subetapas do primeiro cenário
            self._cenario_index = 0
            self.estado = EstadoEtapa.SUBETAPAS_CENARIO
            return {
                "pergunta": "subetapas",
                "cenario_descricao": self.cenarios[0].descricao,
                "cenario_numero": self.cenarios[0].numero
            }

        except json.JSONDecodeError:
            return {"erro": "Forneça os cenários em formato JSON"}

    def _processar_subetapas_cenario(self, mensagem: str) -> Dict[str, Any]:
        """Coleta subetapas de um cenário"""
        msg_lower = mensagem.lower().strip()

        if msg_lower in ["pular", "skip", "não", "nao", "nenhum"]:
            # Sem subetapas para este cenário
            pass
        else:
            # Processar subetapas (uma por linha ou JSON)
            try:
                data = json.loads(mensagem)
                subetapas_data = data.get("subetapas", [])
                for i, s in enumerate(subetapas_data, start=1):
                    subetapa = Subetapa(
                        numero=f"{self.cenarios[self._cenario_index].numero}.{i}",
                        descricao=s.get("descricao", s if isinstance(s, str) else "")
                    )
                    self.cenarios[self._cenario_index].subetapas.append(subetapa)
            except json.JSONDecodeError:
                # Texto livre (uma por linha)
                linhas = [l.strip() for l in mensagem.split('\n') if l.strip()]
                for i, desc in enumerate(linhas, start=1):
                    subetapa = Subetapa(
                        numero=f"{self.cenarios[self._cenario_index].numero}.{i}",
                        descricao=desc
                    )
                    self.cenarios[self._cenario_index].subetapas.append(subetapa)

        # Próximo cenário ou finalizar
        self._cenario_index += 1
        if self._cenario_index < len(self.cenarios):
            return {
                "pergunta": "subetapas",
                "cenario_descricao": self.cenarios[self._cenario_index].descricao,
                "cenario_numero": self.cenarios[self._cenario_index].numero
            }
        else:
            # Todos os cenários processados
            self.estado = EstadoEtapa.FINALIZADA
            return {"status": "finalizada"}

    def _processar_detalhes(self, mensagem: str) -> Dict[str, Any]:
        """Coleta detalhes opcionais da etapa linear"""
        msg_lower = mensagem.lower().strip()

        if msg_lower in ["não", "nao", "n"]:
            # Sem mais detalhes
            self.estado = EstadoEtapa.FINALIZADA
            return {"status": "finalizada"}
        else:
            # Adicionar detalhe
            self.detalhes.append(mensagem.strip())
            return {"pergunta": "mais_detalhes", "detalhe_adicionado": mensagem.strip()}


# =============================================================================
# HELENA ETAPAS - PRODUTO PRINCIPAL
# =============================================================================

class HelenaEtapas(BaseHelena):
    """
    Helena Etapas v2.0 - Coleta granular de etapas operacionais.

    Características:
    - Coleta etapas dinâmicas (não usa PMBOK)
    - Dados granulares por etapa (sistemas, docs, tempo)
    - Suporte a condicionais (cenários e subetapas)
    - Consolidação automática de dados
    - Retorna para Helena POP quando concluído
    """

    VERSION = "2.0.0"

    def inicializar_estado(self, dados_herdados: Optional[Dict[str, Any]] = None) -> dict:
        """
        Inicializa estado para Helena Etapas.

        Args:
            dados_herdados: Dados herdados de Helena POP (area, atividade, etc.)

        Returns:
            dict: Estado inicial com estruturas vazias e contexto herdado
        """
        contexto_pop = {}
        if dados_herdados:
            contexto_pop = {
                'area': dados_herdados.get('area'),
                'subarea': dados_herdados.get('subarea'),
                'macroprocesso': dados_herdados.get('macroprocesso'),
                'processo': dados_herdados.get('processo'),
                'subprocesso': dados_herdados.get('subprocesso'),
                'atividade': dados_herdados.get('atividade'),
                'codigo_cap': dados_herdados.get('codigo_cap'),
                'dados_coletados': dados_herdados.get('dados_coletados', {})
            }
            logger.info(f"[HELENA ETAPAS] Inicializando com dados herdados: {contexto_pop.get('atividade', 'N/A')}")

        return {
            'etapas': [],
            'concluido': False,
            'contexto_pop': contexto_pop,
            '_etapa_sm': None
        }

    def processar(self, mensagem: str, session_data: dict) -> dict:
        """
        Processa mensagem do usuário.

        Args:
            mensagem: Texto do usuário
            session_data: Estado da sessão (mutável)

        Returns:
            dict: Resposta com novo estado via criar_resposta()
        """
        # ✅ Consumir bootstrap (dados herdados do POP) apenas uma vez
        bootstrap = session_data.pop('_helena_bootstrap', None)

        # ✅ Usar namespace dedicado para evitar colisão de chaves
        session_data.setdefault('helena_etapas', {})
        estado = session_data['helena_etapas']

        # ✅ Inicializar apenas na primeira vez
        if bootstrap and not estado.get('_iniciado'):
            estado.update(self.inicializar_estado(bootstrap))
            estado['_iniciado'] = True
            logger.info(f"[HELENA ETAPAS] Inicializado com bootstrap: {bootstrap.get('nome_usuario', 'N/A')}")

        # Comandos globais
        msg_lower = mensagem.lower().strip()

        if msg_lower == 'resumo':
            return self._gerar_resumo(estado)

        if msg_lower in ['finalizar', 'concluir', 'terminar', 'não', 'nao']:
            if estado.get('_etapa_sm'):
                # Tem SM ativa, processar normalmente
                return self._processar_com_state_machine(estado, mensagem)
            else:
                # Sem SM, finalizar mapeamento
                return self._finalizar_mapeamento(estado)

        # Processar com StateMachine
        return self._processar_com_state_machine(estado, mensagem)

    def _processar_com_state_machine(self, estado: dict, mensagem: str) -> dict:
        """Processa usando EtapaStateMachine."""
        # 🎯 CASO ESPECIAL: Mensagem de inicialização (primeira vez)
        if not estado.get('_etapa_sm') and mensagem.lower().strip() == 'iniciar':
            # Retornar mensagem de boas-vindas e primeira pergunta sem criar SM ainda
            contexto_pop = estado.get('contexto_pop', {})
            atividade = contexto_pop.get('atividade', 'esta atividade')

            resposta = (
                f"🎯 **Olá! Agora vou te ajudar a mapear as etapas operacionais de: {atividade}**\n\n"
                f"Vou fazer perguntas sobre cada etapa para entender como o processo realmente funciona.\n\n"
                f"📝 **Vamos começar pela PRIMEIRA ETAPA:**\n\n"
                f"**Descreva o que é feito nesta etapa**\n\n"
                f"💡 _Seja breve e objetivo. Exemplo: \"Recebo documento pelo SEI e analiso\"_"
            )

            return self.criar_resposta(
                resposta=resposta,
                novo_estado=estado
            )

        # Criar nova SM se não existir
        if not estado.get('_etapa_sm'):
            numero_etapa = len(estado['etapas']) + 1
            contexto = estado.get('contexto_pop', {})

            sm = EtapaStateMachine(
                numero_etapa=numero_etapa,
                sistemas_disponiveis=contexto.get('sistemas_disponiveis', []),
                operadores_disponiveis=contexto.get('operadores_disponiveis', [])
            )

            estado['_etapa_sm'] = sm.to_dict()
            logger.info(f"Nova StateMachine criada para Etapa {numero_etapa}")

        # Deserializar e processar mensagem
        sm = EtapaStateMachine.from_dict(estado['_etapa_sm'])
        resultado = sm.processar(mensagem)

        # Serializar de volta
        estado['_etapa_sm'] = sm.to_dict()

        # Verificar se completou
        if sm.completa():
            etapa_dict = sm.obter_dict()
            estado['etapas'].append(etapa_dict)

            # Atualizar consolidados
            self._atualizar_consolidados(estado, etapa_dict)

            # Destruir SM
            estado['_etapa_sm'] = None

            total_etapas = len(estado['etapas'])
            resposta = f"\n✅ **Etapa {total_etapas} completa!**\n\n"
            resposta += f"📊 **Resumo rápido:**\n"
            resposta += f"- **Etapa:** {etapa_dict.get('acao_principal') or etapa_dict.get('descricao', '')}\n"
            resposta += f"- **Responsável:** {etapa_dict.get('operador_nome') or etapa_dict.get('operador', '')}\n"
            resposta += f"- **Sistemas:** {', '.join(etapa_dict['sistemas']) if etapa_dict['sistemas'] else 'Nenhum'}\n"
            resposta += f"- **Tipo:** {'🔀 Condicional' if etapa_dict.get('tipo') == 'condicional' else '➡️ Linear'}\n\n"
            resposta += f"🔄 **Há mais alguma etapa?**\n\n"
            resposta += f"Responda:\n"
            resposta += f"- Digite a **próxima etapa** para continuar\n"
            resposta += f"- Digite **\"não\"** ou **\"finalizar\"** para concluir\n\n"
            resposta += f"_Comando: \"resumo\" para ver todas etapas_\n"

            return self.criar_resposta(
                resposta=resposta,
                novo_estado=estado,
                progresso=f"{total_etapas} {'etapa' if total_etapas == 1 else 'etapas'} mapeada{'s' if total_etapas > 1 else ''}"
            )

        # Traduzir sinais da SM
        return self._traduzir_sinal_sm(estado, resultado)

    def _traduzir_sinal_sm(self, estado: dict, sinal: dict) -> dict:
        """Traduz sinais da StateMachine para respostas."""
        sm_dict = estado['_etapa_sm']
        sm = EtapaStateMachine.from_dict(sm_dict)

        if 'erro' in sinal:
            return self.criar_resposta(
                resposta=f"⚠️ {sinal['erro']}",
                novo_estado=estado
            )

        # Pergunta: Operador
        if sinal.get('proximo') == 'OPERADOR':
            return self.criar_resposta(
                resposta="👤 **Quem EXECUTA esta etapa?**\n\n💡 _Informe o cargo, função ou pessoa responsável._\n\n**Exemplos:** Funcionário, Gestor, Analista de RH",
                novo_estado=estado
            )

        # Pergunta: Sistemas
        elif sinal.get('pergunta') == 'sistemas':
            return self.criar_resposta(
                resposta="💻 **Quais SISTEMAS são utilizados nesta etapa?**\n\n💡 _Sistemas que o responsável usa para executar._\n\n**Exemplos:** SEI, SIAFI, SIGA, Sigepe\n\n_Digite separados por vírgula, ou 'nenhum'_",
                novo_estado=estado
            )

        # Pergunta: Docs Requeridos
        elif sinal.get('pergunta') == 'docs_requeridos':
            return self.criar_resposta(
                resposta="📄 **Quais DOCUMENTOS são ANALISADOS/REQUERIDOS?**\n\n💡 _Documentos recebidos, lidos ou analisados._\n\n**Exemplos:** CPF, RG, Requisição, Despacho\n\n_Digite separados por vírgula, ou 'nenhum'_",
                novo_estado=estado
            )

        # Pergunta: Docs Gerados
        elif sinal.get('pergunta') == 'docs_gerados':
            return self.criar_resposta(
                resposta="📤 **Quais DOCUMENTOS são PRODUZIDOS/GERADOS?**\n\n💡 _Documentos criados, emitidos ou gerados._\n\n**Exemplos:** Despacho, Parecer, Ofício, Relatório\n\n_Digite separados por vírgula, ou 'nenhum'_",
                novo_estado=estado
            )

        # Pergunta: Tempo
        elif sinal.get('pergunta') == 'tempo_estimado':
            return self.criar_resposta(
                resposta="⏱️ **Qual o TEMPO ESTIMADO?**\n\n💡 _Tempo médio para concluir._\n\n**Exemplos:** 15 minutos, 2 horas, 1 dia útil, Imediato\n\n_Digite o tempo ou 'pular'_",
                novo_estado=estado
            )

        # Pergunta: Tem Condicionais
        elif sinal.get('pergunta') == 'tem_condicionais':
            return self.criar_resposta(
                resposta="🔀 **Esta etapa possui DECISÕES ou CONDICIONAIS?**\n\n💡 _Há diferentes caminhos dependendo de uma condição?_\n\n**SIM:** Se aprovado → etapa X, senão → etapa Y\n**NÃO:** Etapa sempre segue o mesmo caminho\n\n_Responda: **sim** ou **não**_",
                novo_estado=estado
            )

        # Pergunta: Tipo Condicional
        elif sinal.get('pergunta') == 'tipo_condicional':
            return self.criar_resposta(
                resposta="🔀 **Quantos cenários existem?**\n\n1. **Binário** (2 cenários) - Ex: Aprovado/Recusado\n2. **Múltiplos** (3+) - Ex: Completo/Incompleto/Inválido\n\n_Digite: **binário** ou **múltiplos**_",
                novo_estado=estado
            )

        # Pergunta: Antes Decisão
        elif sinal.get('pergunta') == 'antes_decisao':
            return self.criar_resposta(
                resposta="⚙️ **O que é feito ANTES da decisão?**\n\n💡 _Ação antes de tomar a decisão._\n\n**Exemplos:**\n- Analisar conformidade documental\n- Verificar dados no sistema\n- Avaliar critérios técnicos",
                novo_estado=estado
            )

        # Pergunta: Cenários
        elif sinal.get('pergunta') == 'cenarios':
            num = 2 if sm.tipo_condicional == "binario" else "3 ou mais"
            exemplo = '{"cenarios": [{"descricao": "Documentação completa"}, {"descricao": "Documentação incompleta"}]}'

            return self.criar_resposta(
                resposta=f"📋 **Descreva os {num} cenários**\n\n**Formato JSON:**\n```json\n{exemplo}\n```",
                novo_estado=estado
            )

        # Pergunta: Subetapas
        elif sinal.get('pergunta') == 'subetapas':
            cenario = sinal.get('cenario_descricao', '')
            return self.criar_resposta(
                resposta=f"📌 **Cenário: {cenario}**\n\nQuais as SUBETAPAS?\n\n💡 _Uma por linha, ou 'pular'_\n\n**Exemplo:**\n```\nNotificar solicitante\nArquivar processo\nRegistrar no sistema\n```",
                novo_estado=estado
            )

        # Pergunta: Detalhes
        elif sinal.get('pergunta') == 'detalhes':
            return self.criar_resposta(
                resposta="📝 **Quer adicionar DETALHES desta etapa?**\n\n💡 _Pequenas ações dentro da etapa principal._\n\n**Exemplos:** Verificar campo X, Validar assinatura\n\n_Digite um detalhe ou 'não'_",
                novo_estado=estado
            )

        # Pergunta: Mais Detalhes
        elif sinal.get('pergunta') == 'mais_detalhes':
            detalhe = sinal.get('detalhe_adicionado', '')
            return self.criar_resposta(
                resposta=f"✅ Detalhe adicionado: _{detalhe}_\n\nHá mais? (Digite o próximo ou 'não')",
                novo_estado=estado
            )

        # Fallback
        return self.criar_resposta(
            resposta="Processando...",
            novo_estado=estado
        )

    def _atualizar_consolidados(self, estado: dict, etapa: dict):
        """Atualiza listas consolidadas com dados da nova etapa"""
        if 'sistemas_consolidados' not in estado:
            estado['sistemas_consolidados'] = []
        if 'operadores_consolidados' not in estado:
            estado['operadores_consolidados'] = []
        if 'documentos_consolidados' not in estado:
            estado['documentos_consolidados'] = []

        # Adicionar sistemas únicos
        for s in etapa.get('sistemas', []):
            if s and s not in estado['sistemas_consolidados']:
                estado['sistemas_consolidados'].append(s)

        # Adicionar operador único
        op = etapa.get('operador_nome') or etapa.get('operador')
        if op and op not in estado['operadores_consolidados']:
            estado['operadores_consolidados'].append(op)

        # Adicionar documentos únicos
        for d in etapa.get('docs_requeridos', []):
            if d and d not in estado['documentos_consolidados']:
                estado['documentos_consolidados'].append(d)
        for d in etapa.get('docs_gerados', []):
            if d and d not in estado['documentos_consolidados']:
                estado['documentos_consolidados'].append(d)

    def _finalizar_mapeamento(self, estado: dict) -> dict:
        """Finaliza e retorna para Helena POP."""
        if not estado['etapas']:
            return self.criar_resposta(
                resposta="⚠️ Nenhuma etapa foi mapeada. Descreva a primeira etapa.",
                novo_estado=estado
            )

        estado['concluido'] = True

        total_etapas = len(estado['etapas'])
        total_sistemas = len(estado.get('sistemas_consolidados', []))
        total_operadores = len(estado.get('operadores_consolidados', []))
        total_documentos = len(estado.get('documentos_consolidados', []))

        resposta = f"\n🎉 **Mapeamento concluído!**\n\n"
        resposta += f"📊 **Resumo:**\n"
        resposta += f"- ✅ **{total_etapas} etapas** mapeadas\n"
        resposta += f"- 💻 **{total_sistemas} sistemas**\n"
        resposta += f"- 👥 **{total_operadores} operadores**\n"
        resposta += f"- 📄 **{total_documentos} tipos de documentos**\n\n"
        resposta += f"✅ **Dados salvos! Retornando para Helena POP...**\n"

        # Retorna dados para Helena POP
        if estado.get('contexto_pop'):
            return self.criar_resposta(
                resposta=resposta,
                novo_estado=estado,
                retornar_para='pop',
                dados={
                    'etapas': estado['etapas'],
                    'sistemas_consolidados': estado.get('sistemas_consolidados', []),
                    'operadores_consolidados': estado.get('operadores_consolidados', []),
                    'documentos_consolidados': estado.get('documentos_consolidados', [])
                },
                progresso=f"{total_etapas} etapas concluídas"
            )
        else:
            return self.criar_resposta(
                resposta=resposta,
                novo_estado=estado,
                progresso=f"{total_etapas} etapas concluídas"
            )

    def _gerar_resumo(self, estado: dict) -> dict:
        """Gera resumo completo."""
        if not estado['etapas']:
            return self.criar_resposta(
                resposta="⚠️ Nenhuma etapa mapeada ainda.",
                novo_estado=estado
            )

        resposta = "📊 **RESUMO DAS ETAPAS MAPEADAS**\n\n"

        for etapa in estado['etapas']:
            resposta += f"**{etapa['numero']}. {etapa.get('acao_principal') or etapa.get('descricao', '')}**\n"
            resposta += f"   👤 {etapa.get('operador_nome') or etapa.get('operador', '')}\n"

            if etapa.get('sistemas'):
                resposta += f"   💻 Sistemas: {', '.join(etapa['sistemas'])}\n"

            if etapa.get('tipo') == 'condicional':
                resposta += f"   🔀 Condicional ({etapa.get('tipo_condicional', '')})\n"
            else:
                resposta += f"   ➡️ Linear\n"

            resposta += "\n"

        total = len(estado['etapas'])
        resposta += f"**Total: {total} {'etapa' if total == 1 else 'etapas'}**\n\n"
        resposta += "_Digite a próxima etapa ou 'finalizar'_"

        return self.criar_resposta(
            resposta=resposta,
            novo_estado=estado,
            progresso=f"{total} {'etapa' if total == 1 else 'etapas'} mapeada{'s' if total > 1 else ''}"
        )

    def receber_dados(self, produto: str, dados: dict) -> dict:
        """Helena Etapas não recebe dados de outros produtos."""
        return self.criar_resposta(
            resposta="Helena Etapas não recebe dados de outros produtos.",
            novo_estado=self.inicializar_estado()
        )
