"""
BSC Agent - Balanced Scorecard Público

Placeholder: Este agente será expandido futuramente.
Por enquanto, retorna mensagem de "em desenvolvimento".
"""
from typing import Dict, Any
from langchain_openai import ChatOpenAI


class BSCAgent:
    """Agente BSC (em desenvolvimento)"""

    def __init__(self, llm: ChatOpenAI = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.7, request_timeout=30)

    def processar_mensagem(self, mensagem: str, estrutura_atual: dict) -> dict:
        return {
            'campo': 'erro',
            'valor': None,
            'proxima_pergunta': "⚠️ BSC Público ainda em desenvolvimento. Em breve!",
            'completo': False,
            'percentual': 0
        }

    def calcular_progresso(self, estrutura: dict) -> int:
        return 0

    def validar_estrutura(self, estrutura: dict) -> tuple[bool, str]:
        return False, "BSC em desenvolvimento"

    def gerar_resumo(self, estrutura: dict) -> str:
        return "# BSC Público (em desenvolvimento)\n"
