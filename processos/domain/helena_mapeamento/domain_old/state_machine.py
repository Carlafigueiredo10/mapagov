"""
Máquina de estados para construção incremental de etapas
Substitui 8 flags booleanas por estados explícitos
"""
import json
from typing import Dict, Any, List, Optional
from .enums import EstadoEtapa
from .models import Etapa, Cenario, Subetapa


class EtapaStateMachine:
    """
    Máquina de estados para coletar uma etapa completa (linear ou condicional)

    Estados possíveis:
    - DESCRICAO → OPERADOR → PERGUNTA_CONDICIONAL
      ├─ (se não tem condicionais) → DETALHES → FINALIZADA
      └─ (se tem condicionais) → TIPO_CONDICIONAL → ANTES_DECISAO → CENARIOS → SUBETAPAS_CENARIO → FINALIZADA

    Benefícios:
    - Elimina 8 flags booleanas interdependentes
    - Reduz complexidade ciclomática de 40 para ~5
    - Facilita testes unitários
    - Previne bugs de estado inconsistente
    """

    def __init__(self, numero_etapa: int, operadores_disponiveis: List[str]):
        self.numero = numero_etapa
        self.operadores_disponiveis = operadores_disponiveis
        self.estado = EstadoEtapa.DESCRICAO

        # Dados coletados
        self.descricao = ""
        self.operador: Optional[str] = None
        self.tem_condicionais: Optional[bool] = None
        self.tipo_condicional: Optional[str] = None  # "binario" ou "multiplos"
        self.antes_decisao: Optional[str] = None
        self.cenarios: List[Cenario] = []
        self.detalhes: List[str] = []

        # Controle interno
        self._cenario_index = 0  # Índice do cenário sendo detalhado

    def processar(self, mensagem: str) -> Dict[str, Any]:
        """
        Processa mensagem do usuário e transita entre estados

        Args:
            mensagem: Entrada do usuário (texto ou JSON)

        Returns:
            Dicionário com sinais para o adaptador UI:
            - {"proximo": "OPERADOR"} → avançou para próximo estado
            - {"pergunta": "tem_condicionais?"} → fazer pergunta ao usuário
            - {"status": "etapa_finalizada"} → etapa completa
        """
        handlers = {
            EstadoEtapa.DESCRICAO: self._processar_descricao,
            EstadoEtapa.OPERADOR: self._processar_operador,
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
                detalhes=self.detalhes
            )

    def obter_dict(self) -> Dict[str, Any]:
        """Retorna dicionário no formato esperado pelo backend/frontend"""
        return self.obter_etapa().to_dict()

    def obter_estado_interno(self) -> Dict[str, Any]:
        """
        Serializa estado interno da StateMachine SEM valores default.
        Usado para salvar/restaurar estado entre requisições.

        IMPORTANTE: Não usa obter_etapa() porque aquele método aplica
        valores padrão como 'Não especificado', o que quebra a lógica
        de detecção de estado ao restaurar.
        """
        return {
            'numero': self.numero,
            'descricao': self.descricao,
            'operador': self.operador,  # ✅ None se não foi definido
            'tem_condicionais': self.tem_condicionais,  # ✅ None se não foi perguntado
            'tipo_condicional': self.tipo_condicional,
            'antes_decisao': self.antes_decisao,
            'detalhes': self.detalhes,
            'cenarios': [
                {
                    'numero': c.numero,
                    'descricao': c.descricao,
                    'subetapas': [
                        {'numero': s.numero, 'descricao': s.descricao}
                        for s in c.subetapas
                    ]
                }
                for c in self.cenarios
            ] if self.cenarios else [],
            '_cenario_index': self._cenario_index  # ✅ FIX: Salvar índice do cenário atual
        }

    # =========================================================================
    # HANDLERS INTERNOS (um por estado)
    # =========================================================================

    def _processar_descricao(self, mensagem: str) -> Dict[str, Any]:
        """Estado: DESCRICAO - coleta descrição da etapa"""
        self.descricao = mensagem.strip()
        self.estado = EstadoEtapa.OPERADOR
        return {"proximo": "OPERADOR", "descricao": self.descricao}

    def _processar_operador(self, mensagem: str) -> Dict[str, Any]:
        """Estado: OPERADOR - coleta responsável pela execução"""
        self.operador = mensagem.strip()
        self.estado = EstadoEtapa.PERGUNTA_CONDICIONAL
        return {"pergunta": "tem_condicionais?", "operador": self.operador}

    def _processar_pergunta_condicional(self, mensagem: str) -> Dict[str, Any]:
        """Estado: PERGUNTA_CONDICIONAL - verifica se etapa tem decisões"""
        resposta = mensagem.lower().strip()
        self.tem_condicionais = resposta in {"sim", "s", "yes", "tem", "possui"}

        if self.tem_condicionais:
            self.estado = EstadoEtapa.TIPO_CONDICIONAL
            return {"pergunta": "tipo_condicional"}
        else:
            self.estado = EstadoEtapa.DETALHES
            return {"pergunta": "detalhes"}

    def _processar_tipo_condicional(self, mensagem: str) -> Dict[str, Any]:
        """Estado: TIPO_CONDICIONAL - coleta tipo (binário ou múltiplos)"""
        resposta = mensagem.lower().strip()
        if "bin" in resposta or "2" in resposta:
            self.tipo_condicional = "binario"
        else:
            self.tipo_condicional = "multiplos"

        self.estado = EstadoEtapa.ANTES_DECISAO
        return {"pergunta": "antes_decisao", "tipo": self.tipo_condicional}

    def _processar_antes_decisao(self, mensagem: str) -> Dict[str, Any]:
        """Estado: ANTES_DECISAO - coleta ação antes da decisão"""
        self.antes_decisao = mensagem.strip()
        self.estado = EstadoEtapa.CENARIOS
        return {"pergunta": "cenarios_descricoes", "antes_decisao": self.antes_decisao}

    def _processar_cenarios(self, mensagem: str) -> Dict[str, Any]:
        """
        Estado: CENARIOS - coleta descrições dos cenários (JSON)

        Formato esperado:
        {"cenarios": [{"descricao": "Documentação completa"}, {"descricao": "Documentação incompleta"}]}
        """
        try:
            data = json.loads(mensagem)
            cenarios_data = data.get("cenarios", [])

            self.cenarios = [
                Cenario(
                    numero=f"{self.numero}.1.{i+1}",
                    descricao=c["descricao"]
                )
                for i, c in enumerate(cenarios_data)
            ]

            self._cenario_index = 0
            self.estado = EstadoEtapa.SUBETAPAS_CENARIO
            return {
                "pergunta": "subetapas",
                "cenario_atual": self.cenarios[0].numero,
                "cenario_descricao": self.cenarios[0].descricao
            }
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            return {"erro": f"Formato inválido de cenários: {e}"}

    def _processar_subetapas_cenario(self, mensagem: str) -> Dict[str, Any]:
        """Estado: SUBETAPAS_CENARIO - coleta subetapas de um cenário"""
        cenario = self.cenarios[self._cenario_index]

        # Processar subetapas (uma por linha)
        if mensagem.lower().strip() not in {"pular", "skip", "não", "nao", "sem subetapas"}:
            linhas = [l.strip() for l in mensagem.strip().split('\n') if l.strip()]
            for i, descricao in enumerate(linhas, 1):
                cenario.subetapas.append(
                    Subetapa(
                        numero=f"{cenario.numero}.{i}",
                        descricao=descricao
                    )
                )

        # Avançar para próximo cenário ou finalizar
        self._cenario_index += 1

        if self._cenario_index < len(self.cenarios):
            proximo_cenario = self.cenarios[self._cenario_index]
            return {
                "pergunta": "subetapas",
                "cenario_atual": proximo_cenario.numero,
                "cenario_descricao": proximo_cenario.descricao
            }
        else:
            self.estado = EstadoEtapa.FINALIZADA
            return {"status": "etapa_condicional_finalizada"}

    def _processar_detalhes(self, mensagem: str) -> Dict[str, Any]:
        """Estado: DETALHES - coleta detalhes de etapa linear"""
        resposta = mensagem.lower().strip()

        if resposta in {"não", "nao", "fim", "finalizar"}:
            self.estado = EstadoEtapa.FINALIZADA
            return {"status": "etapa_linear_finalizada"}

        # Adicionar detalhe numerado
        numero_detalhe = f"{self.numero}.{len(self.detalhes) + 1}"
        self.detalhes.append(f"{numero_detalhe} {mensagem.strip()}")
        return {"pergunta": "mais_detalhes", "detalhe_adicionado": self.detalhes[-1]}
