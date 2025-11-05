"""
SWOT Agent - Agente especializado em Análise SWOT/FOFA

Responsável por guiar a construção de análise SWOT de forma conversacional:
- Forças (Strengths)
- Fraquezas (Weaknesses)
- Oportunidades (Opportunities)
- Ameaças (Threats)
- Estratégias Cruzadas (FO, FA, DO, DA)
"""
import json
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate


class SWOTAgent:
    """
    Agente especializado em construção de matriz SWOT

    Fluxo:
    1. Forças (pontos fortes internos)
    2. Fraquezas (pontos fracos internos)
    3. Oportunidades (fatores externos positivos)
    4. Ameaças (fatores externos negativos)
    5. Estratégias cruzadas (opcional, gerado por IA)
    """

    def __init__(self, llm: ChatOpenAI = None):
        """
        Inicializa agente SWOT

        Args:
            llm: Instância LangChain para gerar estratégias cruzadas
        """
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    def processar_mensagem(self, mensagem: str, estrutura_atual: dict) -> dict:
        """
        Processa mensagem para construção de SWOT

        Args:
            mensagem: Input do usuário
            estrutura_atual: Estado atual do SWOT sendo construído
                {
                    'forcas': ['Força 1', 'Força 2', ...],
                    'fraquezas': ['Fraqueza 1', ...],
                    'oportunidades': ['Oportunidade 1', ...],
                    'ameacas': ['Ameaça 1', ...],
                    'estrategias_cruzadas': {'fo': [...], 'fa': [...], 'do': [...], 'da': [...]}
                }

        Returns:
            dict: {
                'campo': str,  # Campo que foi preenchido
                'valor': List[str],  # Lista de itens extraídos
                'proxima_pergunta': str,  # Próxima pergunta
                'completo': bool,  # Se SWOT está completo
                'percentual': int  # 0-100
            }
        """

        # ETAPA 1: Coletar Forças
        if not estrutura_atual.get('forcas') or len(estrutura_atual['forcas']) == 0:
            itens = self._extrair_lista(mensagem)

            return {
                'campo': 'forcas',
                'valor': itens,
                'proxima_pergunta': f"""Forças registradas! ✅

{len(itens)} forças identificadas.

Agora as **Fraquezas** (pontos fracos internos):

Exemplos:
- Infraestrutura tecnológica defasada
- Falta de capacitação da equipe
- Processos burocráticos lentos
- Rotatividade alta de servidores

Liste 3-5 fraquezas que limitam a organização:""",
                'completo': False,
                'percentual': 25
            }

        # ETAPA 2: Coletar Fraquezas
        if not estrutura_atual.get('fraquezas') or len(estrutura_atual['fraquezas']) == 0:
            itens = self._extrair_lista(mensagem)

            return {
                'campo': 'fraquezas',
                'valor': itens,
                'proxima_pergunta': f"""Fraquezas registradas! ✅

{len(itens)} fraquezas identificadas.

Agora as **Oportunidades** (fatores externos positivos):

Exemplos:
- Novas políticas públicas favoráveis
- Crescimento da demanda por serviços digitais
- Parcerias com outras instituições
- Orçamento adicional aprovado

Liste 3-5 oportunidades que a organização pode aproveitar:""",
                'completo': False,
                'percentual': 50
            }

        # ETAPA 3: Coletar Oportunidades
        if not estrutura_atual.get('oportunidades') or len(estrutura_atual['oportunidades']) == 0:
            itens = self._extrair_lista(mensagem)

            return {
                'campo': 'oportunidades',
                'valor': itens,
                'proxima_pergunta': f"""Oportunidades registradas! ✅

{len(itens)} oportunidades identificadas.

Por fim, as **Ameaças** (fatores externos negativos):

Exemplos:
- Cortes orçamentários
- Mudanças legislativas desfavoráveis
- Crescimento da demanda além da capacidade
- Concorrência com iniciativa privada

Liste 3-5 ameaças que podem impactar a organização:""",
                'completo': False,
                'percentual': 75
            }

        # ETAPA 4: Coletar Ameaças
        if not estrutura_atual.get('ameacas') or len(estrutura_atual['ameacas']) == 0:
            itens = self._extrair_lista(mensagem)

            return {
                'campo': 'ameacas',
                'valor': itens,
                'proxima_pergunta': f"""Ameaças registradas! ✅

**Matriz SWOT completa!** 🎉

Posso gerar **estratégias cruzadas** automaticamente usando IA:
• **FO (Ofensiva):** Usar forças para aproveitar oportunidades
• **FA (Defesa):** Usar forças para mitigar ameaças
• **DO (Reforço):** Corrigir fraquezas para aproveitar oportunidades
• **DA (Sobrevivência):** Minimizar fraquezas e evitar ameaças

Digite:
- "gerar estratégias" → IA cria estratégias automaticamente
- "finalizar" → Concluir sem estratégias cruzadas""",
                'completo': False,
                'percentual': 90
            }

        # ETAPA 5: Gerar estratégias ou finalizar
        if 'gerar' in mensagem.lower() and 'estrategia' in mensagem.lower():
            # Gera estratégias via IA
            estrategias = self.gerar_estrategias_cruzadas(estrutura_atual)

            return {
                'campo': 'estrategias_cruzadas',
                'valor': estrategias,
                'proxima_pergunta': None,
                'completo': True,
                'percentual': 100
            }

        # ETAPA 6: Finalizar sem estratégias
        if 'finalizar' in mensagem.lower() or 'concluir' in mensagem.lower():
            return {
                'campo': 'completo',
                'valor': None,
                'proxima_pergunta': None,
                'completo': True,
                'percentual': 100
            }

        # FALLBACK: Não entendeu
        return {
            'campo': 'erro',
            'valor': None,
            'proxima_pergunta': """Não entendi. Digite:
- "gerar estratégias" → IA cria estratégias cruzadas
- "finalizar" → Concluir análise SWOT""",
            'completo': False,
            'percentual': 90
        }

    def _extrair_lista(self, mensagem: str) -> List[str]:
        """
        Extrai lista de items da mensagem

        Suporta:
        - Lista com bullets (-, *, •)
        - Lista numerada (1., 2., 3.)
        - Lista separada por quebras de linha
        - Lista separada por vírgulas ou ponto-e-vírgula
        """
        itens = []

        # Tenta quebra por linha primeiro
        if '\n' in mensagem:
            for linha in mensagem.split('\n'):
                linha = linha.strip()
                # Remove bullets e numeração
                linha = linha.lstrip('-*•').strip()
                linha = linha.lstrip('0123456789.').strip()
                if linha:
                    itens.append(linha)
            return itens

        # Tenta separadores
        for separador in [';', ',']:
            if separador in mensagem:
                itens = [item.strip() for item in mensagem.split(separador) if item.strip()]
                return itens

        # Item único
        return [mensagem.strip()]

    def gerar_estrategias_cruzadas(self, estrutura: dict) -> dict:
        """
        Gera estratégias cruzadas usando LLM

        Args:
            estrutura: Matriz SWOT completa

        Returns:
            dict: Estratégias FO, FA, DO, DA
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Você é especialista em planejamento estratégico público.

Analise a matriz SWOT e gere 2-3 estratégias cruzadas para cada quadrante:

**FO (Ofensiva):** Use forças para aproveitar oportunidades
**FA (Defesa):** Use forças para mitigar ameaças
**DO (Reforço):** Corrija fraquezas para aproveitar oportunidades
**DA (Sobrevivência):** Minimize fraquezas e evite ameaças

Retorne JSON válido:
{{
  "fo": ["estratégia 1", "estratégia 2"],
  "fa": ["estratégia 1", "estratégia 2"],
  "do": ["estratégia 1", "estratégia 2"],
  "da": ["estratégia 1", "estratégia 2"]
}}"""),
            ("human", """Matriz SWOT:

**Forças:**
{forcas}

**Fraquezas:**
{fraquezas}

**Oportunidades:**
{oportunidades}

**Ameaças:**
{ameacas}""")
        ])

        chain = prompt | self.llm
        resposta = chain.invoke({
            'forcas': '\n'.join(f"- {f}" for f in estrutura.get('forcas', [])),
            'fraquezas': '\n'.join(f"- {f}" for f in estrutura.get('fraquezas', [])),
            'oportunidades': '\n'.join(f"- {o}" for o in estrutura.get('oportunidades', [])),
            'ameacas': '\n'.join(f"- {a}" for a in estrutura.get('ameacas', []))
        })

        try:
            return json.loads(resposta.content)
        except Exception as e:
            # Fallback manual se JSON falhar
            return {
                'fo': [
                    'Usar pontos fortes para aproveitar oportunidades identificadas',
                    'Expandir capacidades existentes baseado em demandas externas'
                ],
                'fa': [
                    'Usar fortalezas para se defender de ameaças externas',
                    'Aproveitar vantagens competitivas para mitigar riscos'
                ],
                'do': [
                    'Corrigir fraquezas para capitalizar oportunidades',
                    'Desenvolver áreas deficientes que bloqueiam crescimento'
                ],
                'da': [
                    'Minimizar fraquezas para reduzir vulnerabilidade a ameaças',
                    'Criar plano de contingência para pontos fracos críticos'
                ]
            }

    def calcular_progresso(self, estrutura: dict) -> int:
        """
        Calcula percentual de conclusão do SWOT

        Args:
            estrutura: Estrutura atual do SWOT

        Returns:
            int: 0-100
        """
        campos = ['forcas', 'fraquezas', 'oportunidades', 'ameacas']
        preenchidos = sum(1 for c in campos if estrutura.get(c) and len(estrutura[c]) > 0)

        if preenchidos == 0:
            return 0
        elif preenchidos == 1:
            return 25
        elif preenchidos == 2:
            return 50
        elif preenchidos == 3:
            return 75
        elif preenchidos == 4:
            if estrutura.get('estrategias_cruzadas'):
                return 100
            else:
                return 90
        return 0

    def validar_estrutura(self, estrutura: dict) -> tuple[bool, str]:
        """
        Valida se SWOT está completo e bem formado

        Args:
            estrutura: SWOT para validar

        Returns:
            tuple: (valido: bool, mensagem_erro: str)
        """
        campos_obrigatorios = ['forcas', 'fraquezas', 'oportunidades', 'ameacas']

        for campo in campos_obrigatorios:
            if not estrutura.get(campo) or len(estrutura[campo]) == 0:
                return False, f"Campo '{campo}' está vazio"

        return True, "SWOT válido"

    def gerar_resumo(self, estrutura: dict) -> str:
        """
        Gera resumo markdown do SWOT

        Args:
            estrutura: SWOT completo

        Returns:
            str: Markdown formatado
        """
        resumo = "# Análise SWOT\n\n"

        # Forças
        resumo += "## 💪 Forças (Strengths)\n"
        for item in estrutura.get('forcas', []):
            resumo += f"- {item}\n"
        resumo += "\n"

        # Fraquezas
        resumo += "## ⚠️ Fraquezas (Weaknesses)\n"
        for item in estrutura.get('fraquezas', []):
            resumo += f"- {item}\n"
        resumo += "\n"

        # Oportunidades
        resumo += "## 🌟 Oportunidades (Opportunities)\n"
        for item in estrutura.get('oportunidades', []):
            resumo += f"- {item}\n"
        resumo += "\n"

        # Ameaças
        resumo += "## ⚡ Ameaças (Threats)\n"
        for item in estrutura.get('ameacas', []):
            resumo += f"- {item}\n"
        resumo += "\n"

        # Estratégias Cruzadas
        if estrutura.get('estrategias_cruzadas'):
            resumo += "## 🎯 Estratégias Cruzadas\n\n"

            ec = estrutura['estrategias_cruzadas']

            if ec.get('fo'):
                resumo += "### FO (Ofensiva - Forças + Oportunidades)\n"
                for est in ec['fo']:
                    resumo += f"- {est}\n"
                resumo += "\n"

            if ec.get('fa'):
                resumo += "### FA (Defesa - Forças + Ameaças)\n"
                for est in ec['fa']:
                    resumo += f"- {est}\n"
                resumo += "\n"

            if ec.get('do'):
                resumo += "### DO (Reforço - Fraquezas + Oportunidades)\n"
                for est in ec['do']:
                    resumo += f"- {est}\n"
                resumo += "\n"

            if ec.get('da'):
                resumo += "### DA (Sobrevivência - Fraquezas + Ameaças)\n"
                for est in ec['da']:
                    resumo += f"- {est}\n"
                resumo += "\n"

        return resumo
