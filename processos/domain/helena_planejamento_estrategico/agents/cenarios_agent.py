"""
Cenários Agent - Planejamento por Cenários

Placeholder: Este agente será expandido futuramente.
"""
from typing import Dict, Any
from langchain_openai import ChatOpenAI


class CenariosAgent:
    """Agente Cenários (em desenvolvimento)"""

    def __init__(self, llm: ChatOpenAI = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.7, request_timeout=30)

    def processar_mensagem(self, mensagem: str, estrutura_atual: dict) -> dict:
        return {
            'campo': 'erro',
            'valor': None,
            'proxima_pergunta': "⚠️ Planejamento por Cenários ainda em desenvolvimento. Em breve!",
            'completo': False,
            'percentual': 0
        }

    def calcular_progresso(self, estrutura: dict) -> int:
        return 0

    def validar_estrutura(self, estrutura: dict) -> tuple[bool, str]:
        return False, "Cenários em desenvolvimento"

    def gerar_resumo(self, estrutura: dict) -> str:
        return "# Planejamento por Cenários (em desenvolvimento)\n"
