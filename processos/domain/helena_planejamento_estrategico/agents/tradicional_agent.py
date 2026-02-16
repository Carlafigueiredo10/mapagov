"""
Tradicional Agent - Agente para Planejamento Estratégico Tradicional

Responsável por guiar a construção de Planejamento Estratégico Tradicional:
- Missão
- Visão
- Valores
- Objetivos Estratégicos
"""
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI


class TradicionalAgent:
    """
    Agente especializado em Planejamento Estratégico Tradicional

    Fluxo:
    1. Missão (razão de existir)
    2. Visão (onde queremos chegar)
    3. Valores (princípios orientadores)
    4. Objetivos Estratégicos (3-5 objetivos de longo prazo)
    """

    CAMPOS_ORDEM = ['missao', 'visao', 'valores', 'objetivos_estrategicos']

    def __init__(self, llm: ChatOpenAI = None):
        """
        Inicializa agente Tradicional

        Args:
            llm: Instância LangChain (opcional)
        """
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.7, request_timeout=30)

    def processar_mensagem(self, mensagem: str, estrutura_atual: dict) -> dict:
        """
        Processa mensagem para construção do Planejamento Tradicional

        Args:
            mensagem: Input do usuário
            estrutura_atual: Estado atual
                {
                    'missao': 'Texto da missão',
                    'visao': 'Texto da visão',
                    'valores': ['Valor 1', 'Valor 2', ...],
                    'objetivos_estrategicos': ['Objetivo 1', ...]
                }

        Returns:
            dict: {
                'campo': str,
                'valor': Any,
                'proxima_pergunta': str,
                'completo': bool,
                'percentual': int
            }
        """

        # Determina campo atual
        campo_atual = None
        for campo in self.CAMPOS_ORDEM:
            if not estrutura_atual.get(campo):
                campo_atual = campo
                break

        if not campo_atual:
            return {
                'campo': 'completo',
                'valor': None,
                'proxima_pergunta': None,
                'completo': True,
                'percentual': 100
            }

        # Perguntas por campo
        perguntas_seguintes = {
            'missao': """Missão definida!

Agora a **Visão** (onde queremos chegar):

Exemplo: "Ser reconhecido como órgão modelo em gestão pública até 2030"

Qual a visão da sua organização?""",

            'visao': """Visão registrada!

Agora os **Valores** organizacionais:

Liste 5-7 valores que guiam a organização.

Exemplo:
- Transparência
- Eficiência
- Inovação
- Foco no cidadão""",

            'valores': """Valores registrados!

Por fim, os **Objetivos Estratégicos**:

Liste 3-5 objetivos de longo prazo.

Exemplo:
- Modernizar processos de atendimento
- Ampliar canais digitais de serviço
- Fortalecer gestão de pessoas"""
        }

        # Extrai valor
        if campo_atual == 'valores' or campo_atual == 'objetivos_estrategicos':
            valor = [v.strip() for v in mensagem.split('\n') if v.strip()]
        else:
            valor = mensagem.strip()

        percentual = (self.CAMPOS_ORDEM.index(campo_atual) + 1) / len(self.CAMPOS_ORDEM) * 100

        return {
            'campo': campo_atual,
            'valor': valor,
            'proxima_pergunta': perguntas_seguintes.get(campo_atual),
            'completo': False,
            'percentual': int(percentual)
        }

    def calcular_progresso(self, estrutura: dict) -> int:
        """Calcula percentual de conclusão"""
        preenchidos = sum(1 for campo in self.CAMPOS_ORDEM if estrutura.get(campo))
        return int((preenchidos / len(self.CAMPOS_ORDEM)) * 100)

    def validar_estrutura(self, estrutura: dict) -> tuple[bool, str]:
        """Valida se planejamento está completo"""
        for campo in self.CAMPOS_ORDEM:
            if not estrutura.get(campo):
                return False, f"Campo '{campo}' está vazio"
        return True, "Planejamento Tradicional válido"

    def gerar_resumo(self, estrutura: dict) -> str:
        """Gera resumo markdown"""
        resumo = "# Planejamento Estratégico Tradicional\n\n"
        resumo += f"## 🎯 Missão\n{estrutura.get('missao', '')}\n\n"
        resumo += f"## 🔭 Visão\n{estrutura.get('visao', '')}\n\n"
        resumo += "## 💎 Valores\n"
        for valor in estrutura.get('valores', []):
            resumo += f"- {valor}\n"
        resumo += "\n## 🎯 Objetivos Estratégicos\n"
        for i, obj in enumerate(estrutura.get('objetivos_estrategicos', []), 1):
            resumo += f"{i}. {obj}\n"
        return resumo
