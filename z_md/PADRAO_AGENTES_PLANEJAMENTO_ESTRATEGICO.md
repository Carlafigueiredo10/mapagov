# Padrão de Desenvolvimento - Agentes de Planejamento Estratégico

## Visão Geral

Este documento define o **padrão universal** para desenvolvimento de todos os agentes de planejamento estratégico do sistema Helena. As otimizações implementadas no `OKRAgent` servirão como **template base** para os demais agentes.

## Agentes do Sistema

1. ✅ **OKRAgent** - Objectives and Key Results (implementado com otimizações)
2. 🔄 **SWOTAgent** - Strengths, Weaknesses, Opportunities, Threats
3. 🔄 **BSCAgent** - Balanced Scorecard
4. 🔄 **TradicionalAgent** - Planejamento Estratégico Tradicional
5. 🔄 **CenariosAgent** - Análise de Cenários
6. 🔄 **Agent5W2H** - What, Who, When, Where, Why, How, How Much
7. 🔄 **HoshinAgent** - Hoshin Kanri (Desdobramento de Diretrizes)

---

## 1. Estrutura Base do Agente

Todos os agentes devem seguir esta estrutura:

```python
"""
{Nome} Agent - Agente especializado em {Metodologia}

Responsável por guiar a construção de {metodologia} de forma conversacional.
"""
import re
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate


class {Nome}Agent:
    """
    Agente especializado em construção de {Metodologia}

    Fluxo:
    1. {Etapa 1}
    2. {Etapa 2}
    3. {Etapa N}
    """

    def __init__(self, llm: ChatOpenAI = None):
        """
        Inicializa agente

        Args:
            llm: Instância LangChain (opcional)
        """
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    def processar_mensagem(self, mensagem: str, estrutura_atual: dict) -> dict:
        """
        Processa mensagem para construção

        Args:
            mensagem: Input do usuário
            estrutura_atual: Estado atual

        Returns:
            dict: {
                'campo': str,
                'valor': Any,
                'proxima_pergunta': str,
                'completo': bool,
                'percentual': int,
                'validacao_ok': bool  # NOVO
            }
        """
        # ... implementação
```

---

## 2. Otimizações Obrigatórias

### 2.1 Validação de Dados com Regex ✅

**Objetivo**: Garantir que respostas sejam específicas e mensuráveis.

```python
def _validar_resposta(self, texto: str, tipo_campo: str) -> tuple[bool, str]:
    """
    Valida se resposta atende critérios do campo

    Args:
        texto: Resposta do usuário
        tipo_campo: Tipo de validação ('mensuravel', 'especifico', 'livre')

    Returns:
        tuple: (valido: bool, mensagem_erro: str)
    """
    texto = texto.strip()

    if not texto:
        return False, "Resposta não pode estar vazia"

    # Validação de mensurabilidade (números, metas, indicadores)
    if tipo_campo == 'mensuravel':
        if not re.search(r'\d+|%|pontos|dias|horas|meses|anos|reais|r\$', texto.lower()):
            return False, "Deve conter meta mensurável (número, percentual ou prazo)"

    # Validação de especificidade (mínimo de palavras)
    elif tipo_campo == 'especifico':
        palavras = texto.split()
        if len(palavras) < 5:
            return False, "Resposta muito genérica. Por favor, seja mais específico (mínimo 5 palavras)"

    # Validação de lista (múltiplos itens)
    elif tipo_campo == 'lista':
        items = self._extrair_lista(texto)
        if len(items) < 3:
            return False, "Por favor, forneça pelo menos 3 itens (um por linha)"

    return True, ""
```

**Exemplo de uso no fluxo**:

```python
# Valida resposta antes de aceitar
valido, erro = self._validar_resposta(mensagem, 'mensuravel')

if not valido:
    return {
        'campo': 'erro_validacao',
        'valor': None,
        'proxima_pergunta': f"""❌ {erro}

Exemplo válido: "Aumentar satisfação de 70% para 90%"

Por favor, tente novamente:""",
        'completo': False,
        'percentual': percentual_atual,
        'validacao_ok': False
    }
```

---

### 2.2 Persistência de Múltiplos Itens ✅

**Objetivo**: Suportar adição de múltiplos elementos sem sobrescrever.

```python
# ETAPA: Verificar se quer adicionar novo item
if 'novo' in mensagem.lower() and '{palavra_chave}' in mensagem.lower():
    # Adiciona novo item ao array existente
    if '{campo}' not in estrutura_atual:
        estrutura_atual['{campo}'] = []

    estrutura_atual['{campo}'].append({
        'titulo': '',
        '{subcampos}': [],
        'completo': False
    })

    return {
        'campo': 'adicionar_{item}',
        'valor': True,
        'proxima_pergunta': f"""Novo {item} #{len(estrutura_atual['{campo}'])}

Qual o título deste {item}?""",
        'completo': False,
        'percentual': self.calcular_progresso(estrutura_atual),
        'validacao_ok': True
    }
```

**Exemplo OKR**:
```python
if 'novo' in mensagem.lower() and 'objetivo' in mensagem.lower():
    estrutura_atual['objetivos'].append({
        'titulo': '',
        'resultados_chave': [],
        'iniciativas': []
    })
```

**Exemplo SWOT**:
```python
if 'nova' in mensagem.lower() and 'oportunidade' in mensagem.lower():
    estrutura_atual['oportunidades'].append({
        'descricao': '',
        'impacto': '',
        'viabilidade': ''
    })
```

---

### 2.3 Reengajamento de Contexto ✅

**Objetivo**: Permitir que usuário peça resumo a qualquer momento.

```python
def processar_mensagem(self, mensagem: str, estrutura_atual: dict) -> dict:
    # 🔄 REENGAJAMENTO: Primeira checagem
    palavras_resumo = ['resumo', 'status', 'como está', 'mostre', 'onde estamos', 'progresso']
    if any(palavra in mensagem.lower() for palavra in palavras_resumo):
        return self._gerar_resumo_parcial(estrutura_atual)

    # ... resto do fluxo
```

```python
def _gerar_resumo_parcial(self, estrutura: dict) -> dict:
    """
    Gera resumo do progresso atual

    Args:
        estrutura: Estado atual

    Returns:
        dict: Resposta com resumo
    """
    resumo = f"📊 **Resumo do seu {self.NOME_METODOLOGIA} até agora:**\n\n"

    # Adiciona informações contextuais
    if estrutura.get('campo_contexto'):
        resumo += f"**{campo_contexto}:** {estrutura['campo_contexto']}\n\n"

    # Lista itens criados
    if estrutura.get('itens_principais'):
        resumo += f"**Itens criados:** {len(estrutura['itens_principais'])}\n\n"

        for i, item in enumerate(estrutura['itens_principais'], 1):
            resumo += f"### Item {i}: {item.get('titulo', '(sem título)')}\n"

            subitems = item.get('subitems', [])
            if subitems:
                resumo += f"**Subitens:** {len(subitems)}\n"
                for subitem in subitems:
                    resumo += f"- {subitem}\n"
            else:
                resumo += "*(sem subitens ainda)*\n"

            resumo += "\n"
    else:
        resumo += "*(Nenhum item criado ainda)*\n\n"

    resumo += "\n\nDeseja continuar? Digite 'novo {item}' ou 'finalizar'."

    return {
        'campo': 'resumo',
        'valor': None,
        'proxima_pergunta': resumo,
        'completo': False,
        'percentual': self.calcular_progresso(estrutura),
        'validacao_ok': True
    }
```

---

### 2.4 Resumo Final Estruturado ✅

**Objetivo**: Gerar relatório markdown completo ao finalizar.

```python
def _gerar_resumo_final(self, estrutura: dict) -> str:
    """
    Gera resumo final completo

    Args:
        estrutura: Estrutura finalizada

    Returns:
        str: Markdown formatado com checklists
    """
    resumo = f"# ✅ {self.NOME_METODOLOGIA} Completo\n\n"

    # Contexto
    if estrutura.get('contexto'):
        resumo += f"**Contexto:** {estrutura['contexto']}\n\n"

    # Itens principais com checkboxes
    for i, item in enumerate(estrutura.get('itens_principais', []), 1):
        resumo += f"## Item {i}: {item['titulo']}\n\n"

        if item.get('subitems'):
            resumo += "### Subitens:\n"
            for subitem in item['subitems']:
                resumo += f"- [ ] {subitem}\n"
            resumo += "\n"

    # Estatísticas
    resumo += "---\n\n"
    total_items = len(estrutura.get('itens_principais', []))
    total_subitems = sum(len(item.get('subitems', [])) for item in estrutura.get('itens_principais', []))

    resumo += f"**Total de {self.NOME_ITEM_PRINCIPAL}:** {total_items}\n"
    resumo += f"**Total de {self.NOME_SUBITEM}:** {total_subitems}\n\n"
    resumo += "🎯 Seu planejamento foi salvo com sucesso!"

    return resumo
```

---

### 2.5 Tratamento de Erros Padronizado ✅

```python
# Padrão de resposta de erro
def _criar_resposta_erro(self, tipo_erro: str, mensagem_erro: str, percentual_atual: int) -> dict:
    """Cria resposta padronizada de erro"""

    mensagens_ajuda = {
        'validacao': """
Lembre-se das boas práticas:
- Seja específico e mensurável
- Use números e metas claras
- Evite termos genéricos""",

        'entrada_invalida': """
Por favor, revise sua resposta e tente novamente.""",

        'timeout': """
Sessão expirada. Inicie uma nova sessão."""
    }

    return {
        'campo': f'erro_{tipo_erro}',
        'valor': None,
        'proxima_pergunta': f"""❌ {mensagem_erro}

{mensagens_ajuda.get(tipo_erro, '')}

Digite 'resumo' para ver o progresso ou continue respondendo:""",
        'completo': False,
        'percentual': percentual_atual,
        'validacao_ok': False
    }
```

---

## 3. Métodos Auxiliares Obrigatórios

### 3.1 Extração de Lista

```python
def _extrair_lista(self, mensagem: str) -> List[str]:
    """
    Extrai lista de items da mensagem

    Suporta:
    - Lista com bullets (-, *, •)
    - Lista numerada (1., 2., 3.)
    - Lista separada por quebras de linha
    """
    items = []

    for linha in mensagem.split('\n'):
        linha = linha.strip()

        # Remove bullets e numeração
        linha = re.sub(r'^[-*•]\s*', '', linha)
        linha = re.sub(r'^\d+\.\s*', '', linha)

        if linha:
            items.append(linha)

    return items
```

### 3.2 Cálculo de Progresso

```python
def calcular_progresso(self, estrutura: dict) -> int:
    """
    Calcula percentual de conclusão

    Args:
        estrutura: Estado atual

    Returns:
        int: 0-100
    """
    # Exemplo genérico - ajustar para cada agente
    campos_obrigatorios = ['contexto', 'itens_principais']
    campos_completos = sum(1 for campo in campos_obrigatorios if estrutura.get(campo))

    percentual_base = (campos_completos / len(campos_obrigatorios)) * 60

    # Adiciona peso dos itens criados
    if estrutura.get('itens_principais'):
        num_items = len(estrutura['itens_principais'])
        percentual_items = min(num_items * 10, 40)
        return min(int(percentual_base + percentual_items), 100)

    return int(percentual_base)
```

### 3.3 Validação de Estrutura

```python
def validar_estrutura(self, estrutura: dict) -> tuple[bool, str]:
    """
    Valida se estrutura está completa e bem formada

    Args:
        estrutura: Estrutura para validar

    Returns:
        tuple: (valido: bool, mensagem_erro: str)
    """
    # Campos obrigatórios específicos de cada agente
    campos_obrigatorios = self.CAMPOS_OBRIGATORIOS

    for campo in campos_obrigatorios:
        if not estrutura.get(campo):
            return False, f"Falta definir: {campo}"

    # Validações específicas
    if estrutura.get('itens_principais'):
        for i, item in enumerate(estrutura['itens_principais'], 1):
            if not item.get('titulo'):
                return False, f"Item {i} sem título"

            if not item.get('subitems') or len(item['subitems']) < self.MIN_SUBITEMS:
                return False, f"Item {i} precisa de pelo menos {self.MIN_SUBITEMS} subitems"

    return True, "Estrutura válida"
```

---

## 4. Constantes e Configurações

Cada agente deve definir suas constantes:

```python
class {Nome}Agent:
    # Identificação
    NOME_METODOLOGIA = "{Nome Completo}"
    NOME_CURTO = "{sigla}"

    # Estrutura
    NOME_ITEM_PRINCIPAL = "{nome do item principal}"  # ex: "Objetivos", "Perspectivas"
    NOME_SUBITEM = "{nome do subitem}"  # ex: "KRs", "Indicadores"

    # Validação
    MIN_SUBITEMS = 3  # Mínimo de subitems por item principal
    CAMPOS_OBRIGATORIOS = ['campo1', 'campo2']

    # Exemplos para guiar usuário
    EXEMPLOS = {
        'item_principal': [
            "Exemplo 1",
            "Exemplo 2",
            "Exemplo 3"
        ],
        'subitem': [
            "Subexemplo 1",
            "Subexemplo 2"
        ]
    }
```

---

## 5. Integração com Sistema

### 5.1 Registro no Orquestrador

Todos os agentes devem ser registrados em `pe_orchestrator.py`:

```python
from processos.domain.helena_planejamento_estrategico.agents.okr_agent import OKRAgent
from processos.domain.helena_planejamento_estrategico.agents.swot_agent import SWOTAgent
from processos.domain.helena_planejamento_estrategico.agents.bsc_agent import BSCAgent
# ... imports dos demais agentes

class HelenaPlanejamentoEstrategico:
    def __init__(self):
        # Registry de agentes
        self.agents = {
            'tradicional': TradicionalAgent(),
            'bsc': BSCAgent(),
            'okr': OKRAgent(),
            'swot': SWOTAgent(),
            'cenarios': CenariosAgent(),
            '5w2h': Agent5W2H(),
            'hoshin': HoshinAgent()
        }
```

### 5.2 Chamada no Estado CONSTRUCAO_MODELO

```python
def _handle_construcao_modelo(self, mensagem: str, session_data: dict) -> dict:
    """Delega para agente especializado"""

    modelo = session_data.get('modelo_selecionado')

    if modelo not in self.agents:
        return {'resposta': f'Modelo {modelo} não implementado', 'session_data': session_data}

    # Pega estrutura atual
    estrutura = session_data.get('estrutura_planejamento', {})

    # Processa com agente
    resultado = self.agents[modelo].processar_mensagem(mensagem, estrutura)

    # Atualiza session_data
    if resultado.get('valor') is not None:
        campo = resultado['campo']

        # Lógica de atualização da estrutura
        if campo == 'adicionar_{item}':
            # Já foi adicionado pelo agente
            pass
        elif campo in ['erro_validacao', 'erro', 'resumo']:
            # Não atualiza estrutura em caso de erro ou resumo
            pass
        else:
            # Atualiza campo específico
            self._atualizar_estrutura(estrutura, campo, resultado['valor'])

    session_data['estrutura_planejamento'] = estrutura
    session_data['percentual_conclusao'] = resultado['percentual']

    # Marca como completo se agente finalizou
    if resultado.get('completo'):
        session_data['estado_atual'] = EstadoPlanejamento.REVISAO_ANALISE

    return {
        'resposta': resultado['proxima_pergunta'] or resultado.get('mensagem_final', 'Concluído!'),
        'session_data': session_data,
        'progresso': f"{resultado['percentual']}%"
    }
```

---

## 6. Testes Unitários Padrão

Cada agente deve ter testes cobrindo:

```python
import pytest
from processos.domain.helena_planejamento_estrategico.agents.{nome}_agent import {Nome}Agent


class Test{Nome}Agent:
    """Testes do {Nome}Agent"""

    @pytest.fixture
    def agent(self):
        return {Nome}Agent()

    @pytest.fixture
    def estrutura_inicial(self):
        return {}

    def test_validacao_mensuravel(self, agent):
        """Testa validação de dados mensuráveis"""
        valido, _ = agent._validar_resposta("Aumentar de 50% para 80%", "mensuravel")
        assert valido is True

        valido, _ = agent._validar_resposta("Melhorar processos", "mensuravel")
        assert valido is False

    def test_persistencia_multiplos_items(self, agent, estrutura_inicial):
        """Testa adição de múltiplos itens"""
        # Adiciona primeiro item
        resultado1 = agent.processar_mensagem("Item 1", estrutura_inicial)
        assert len(estrutura_inicial['{campo}']) == 1

        # Adiciona segundo item
        resultado2 = agent.processar_mensagem("novo {item}", estrutura_inicial)
        resultado3 = agent.processar_mensagem("Item 2", estrutura_inicial)
        assert len(estrutura_inicial['{campo}']) == 2

    def test_reengajamento_contexto(self, agent, estrutura_inicial):
        """Testa resumo parcial"""
        resultado = agent.processar_mensagem("resumo", estrutura_inicial)
        assert resultado['campo'] == 'resumo'
        assert '📊' in resultado['proxima_pergunta']

    def test_extracao_lista(self, agent):
        """Testa extração de lista"""
        texto = """
        - Item 1
        - Item 2
        - Item 3
        """
        items = agent._extrair_lista(texto)
        assert len(items) == 3
        assert "Item 1" in items

    def test_calculo_progresso(self, agent):
        """Testa cálculo de percentual"""
        estrutura = {'{campo}': ['item1', 'item2']}
        percentual = agent.calcular_progresso(estrutura)
        assert 0 <= percentual <= 100
```

---

## 7. Exemplo Completo: Template de Novo Agente

```python
"""
SWOT Agent - Agente especializado em Análise SWOT

Responsável por guiar a construção de análise SWOT de forma conversacional.
"""
import re
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI


class SWOTAgent:
    """Agente especializado em construção de SWOT"""

    # Constantes
    NOME_METODOLOGIA = "Análise SWOT"
    NOME_CURTO = "SWOT"
    NOME_ITEM_PRINCIPAL = "Quadrantes"
    NOME_SUBITEM = "Itens"
    MIN_SUBITEMS = 3
    CAMPOS_OBRIGATORIOS = ['forcas', 'fraquezas', 'oportunidades', 'ameacas']

    EXEMPLOS = {
        'forcas': [
            "Equipe técnica altamente qualificada",
            "Processos bem documentados",
            "Tecnologia moderna e escalável"
        ],
        'fraquezas': [
            "Baixa capacitação em gestão de projetos",
            "Infraestrutura de TI defasada",
            "Alto turnover de pessoal"
        ]
        # ... demais exemplos
    }

    def __init__(self, llm: ChatOpenAI = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    def processar_mensagem(self, mensagem: str, estrutura_atual: dict) -> dict:
        # 🔄 REENGAJAMENTO
        if any(palavra in mensagem.lower() for palavra in ['resumo', 'status', 'mostre']):
            return self._gerar_resumo_parcial(estrutura_atual)

        # ETAPA 1: Forças
        if not estrutura_atual.get('forcas'):
            forcas = self._extrair_lista(mensagem)

            valido, erro = self._validar_lista(forcas, 'especifico')
            if not valido:
                return self._criar_resposta_erro('validacao', erro, 0)

            return {
                'campo': 'forcas',
                'valor': forcas,
                'proxima_pergunta': f"""Forças registradas! ✅ ({len(forcas)} itens)

Agora liste as **Fraquezas** da organização.

Exemplos:
{chr(10).join([f'- {ex}' for ex in self.EXEMPLOS['fraquezas']])}

Liste as fraquezas (uma por linha):""",
                'completo': False,
                'percentual': 25,
                'validacao_ok': True
            }

        # ETAPA 2: Fraquezas
        if not estrutura_atual.get('fraquezas'):
            # ... similar ao anterior
            pass

        # ETAPA 3: Oportunidades
        # ETAPA 4: Ameaças
        # ETAPA 5: Finalizar

        # ... implementação completa

    # Métodos auxiliares obrigatórios
    def _validar_resposta(self, texto: str, tipo_campo: str) -> tuple[bool, str]:
        # ... implementação
        pass

    def _extrair_lista(self, mensagem: str) -> List[str]:
        # ... implementação
        pass

    def _gerar_resumo_parcial(self, estrutura: dict) -> dict:
        # ... implementação
        pass

    def _gerar_resumo_final(self, estrutura: dict) -> str:
        # ... implementação
        pass

    def calcular_progresso(self, estrutura: dict) -> int:
        # ... implementação
        pass

    def validar_estrutura(self, estrutura: dict) -> tuple[bool, str]:
        # ... implementação
        pass
```

---

## 8. Helena Semantic Planner - Módulo Reutilizável 🧠

### 8.1 Visão Geral

O `HelenaSemanticPlanner` é uma **camada de tradução semântica** reutilizável que pode ser usada por **todos os agentes** para interpretar linguagem natural e traduzir em conceitos formais de gestão.

**Localização**: `processos/domain/helena_semantic_planner.py`

**Objetivo**: Permitir que agentes entendam frases em linguagem coloquial e as transformem automaticamente em objetivos, resultados, problemas, riscos ou valores.

### 8.2 Funcionalidades Principais

```python
from processos.domain.helena_semantic_planner import HelenaSemanticPlanner

# Criar instância
planner = HelenaSemanticPlanner()

# Interpretar frase do usuário
resultado = planner.interpretar("Eu queria que as pessoas parassem de trabalhar cada uma por conta própria")

# Retorna:
{
    'tipo': 'problema',
    'texto_original': '...',
    'contexto_setorial': 'colaboracao',
    'confianca': 0.85,
    'proposta': '⚠️ Identifiquei um **problema/necessidade**:...'
}
```

### 8.3 Categorias Detectadas

O planner identifica automaticamente 5 categorias:

1. **objetivo** - Intenções estratégicas ("melhorar", "fortalecer", "modernizar")
2. **resultado** - Metas mensuráveis ("atingir 80%", "de 50 para 90")
3. **problema** - Dificuldades e gargalos ("retrabalho", "demora", "desorganizado")
4. **risco** - Ameaças e incertezas ("risco de", "possibilidade de")
5. **valor** - Benefícios e impactos ("valor público", "benefício ao cidadão")

### 8.4 Contextos Setoriais

Detecta automaticamente 6 contextos do setor público:

- **atendimento** - Relacionado a cidadãos, canais, demandas
- **processos** - Workflows, tramitação, procedimentos
- **colaboracao** - Equipes, integração, trabalho conjunto
- **dados** - Informações, métricas, indicadores
- **financeiro** - Orçamento, custos, investimentos
- **tecnologia** - Sistemas, TI, automação

### 8.5 Como Usar nos Agentes

#### Exemplo 1: Detecção de Objetivo vs Problema

```python
from processos.domain.helena_semantic_planner import HelenaSemanticPlanner

class SeuAgent:
    def __init__(self):
        self.planner = HelenaSemanticPlanner()

    def processar_mensagem(self, mensagem: str, estrutura: dict) -> dict:
        # Interpreta semanticamente
        interpretacao = self.planner.interpretar(mensagem)

        if interpretacao['tipo'] == 'problema':
            # Converte problema em objetivo
            objetivo = self.planner._inverter_problema_generico(mensagem)

            return {
                'campo': 'objetivo',
                'valor': objetivo,
                'proxima_pergunta': f"""💡 Transformei o problema em objetivo:

**"{objetivo}"**

Deseja confirmar?"""
            }

        elif interpretacao['tipo'] == 'objetivo':
            # Refina objetivo
            objetivo_refinado = self.planner._refinar_objetivo_generico(mensagem)
            # ... continua
```

#### Exemplo 2: Validação de Mensurabilidade

```python
# Verificar se texto tem métricas
if self.planner.validar_mensurabilidade(mensagem):
    # É um resultado mensurável
    krs.append(mensagem)
else:
    # Pedir métrica
    return self._pedir_metrica(mensagem)
```

#### Exemplo 3: Extração de Lista

```python
# Extrair lista de items automaticamente
items = self.planner.extrair_lista(mensagem)

# Retorna lista limpa:
# ['Item 1', 'Item 2', 'Item 3']
```

### 8.6 Métodos Disponíveis

| Método | Descrição | Retorno |
|--------|-----------|---------|
| `interpretar(mensagem)` | Classifica frase em categoria de gestão | Dict com tipo, contexto, proposta |
| `_inverter_problema_generico(texto)` | Converte problema em objetivo positivo | String |
| `_refinar_objetivo_generico(texto)` | Melhora formulação de objetivo | String |
| `extrair_lista(mensagem)` | Extrai lista de items | List[str] |
| `validar_mensurabilidade(texto)` | Verifica se tem números/métricas | Bool |

### 8.7 Padrões de Vocabulário

O módulo vem com bibliotecas prontas de padrões:

```python
# Padrões de Objetivo (20 verbos)
PADROES_OBJETIVO = ['melhorar', 'aumentar', 'fortalecer', 'reduzir', ...]

# Padrões de Resultado (12 indicadores)
PADROES_RESULTADO = ['atingir', 'alcançar', 'meta', r'\d+%', ...]

# Padrões de Problema (16 sinalizadores)
PADROES_PROBLEMA = ['problema', 'gargalo', 'demora', 'retrabalho', ...]

# Padrões de Risco (8 sinalizadores)
PADROES_RISCO = ['risco', 'ameaça', 'vulnerabilidade', ...]

# Padrões de Valor (11 termos)
PADROES_VALOR = ['valor público', 'benefício', 'impacto', ...]
```

### 8.8 Exemplo de Uso Completo

```python
from processos.domain.helena_semantic_planner import HelenaSemanticPlanner

class OKRAgent:
    def __init__(self):
        self.planner = HelenaSemanticPlanner()

    def processar_objetivo(self, mensagem: str) -> dict:
        # 1. Interpreta a frase
        interpretacao = self.planner.interpretar(mensagem)

        # 2. Detectou problema? Inverte em objetivo
        if interpretacao['tipo'] == 'problema':
            objetivo = self.planner._inverter_problema_generico(mensagem)

            # 3. Busca contexto e sugere KRs
            contexto = interpretacao['contexto_setorial']
            krs_sugeridos = self._buscar_krs_contextuais(contexto)

            return {
                'objetivo_proposto': objetivo,
                'explicacao': interpretacao['proposta'],
                'krs_sugeridos': krs_sugeridos
            }

        # 4. Já é objetivo? Apenas refina
        elif interpretacao['tipo'] == 'objetivo':
            objetivo_refinado = self.planner._refinar_objetivo_generico(mensagem)
            return {'objetivo_proposto': objetivo_refinado}

        # 5. Não identificou? Fluxo manual
        else:
            return {'objetivo_proposto': mensagem.strip()}
```

### 8.9 Vantagens para os Agentes

✅ **Reutilização**: Uma vez criado, todos os agentes usam
✅ **Consistência**: Mesma lógica de interpretação em todo sistema
✅ **Manutenibilidade**: Atualizar padrões em um lugar só
✅ **Extensibilidade**: Fácil adicionar novos padrões e contextos
✅ **Independência**: Funciona sem LLM (apenas heurísticas)

### 8.10 Quando Usar

**Use HelenaSemanticPlanner quando**:
- Quiser interpretar linguagem natural do usuário
- Precisar converter problemas em objetivos
- Necessitar validar se texto tem métricas
- Quiser extrair listas automaticamente
- Desejar detectar contexto setorial

**Não use quando**:
- Já tem texto estruturado e formal
- Não precisa de interpretação semântica
- Está apenas validando formato (use regex direto)

### 8.11 Expansão Futura

O módulo pode ser expandido com:

1. **Dicionário setorial específico** (ex: termos da área previdenciária)
2. **Log de traduções** para dashboard de aprendizado
3. **Integração com LLM** para casos complexos
4. **Tradução para outros métodos** (SWOT, BSC, etc.)

---

## 9. Checklist de Implementação

Para cada novo agente, verificar:

- [ ] Herda estrutura padrão (constantes, métodos auxiliares)
- [ ] Implementa validação de dados com regex
- [ ] Suporta persistência de múltiplos itens
- [ ] Implementa reengajamento de contexto (resumo)
- [ ] Gera resumo final estruturado
- [ ] Trata erros de forma padronizada
- [ ] Calcula progresso corretamente
- [ ] Valida estrutura completa
- [ ] Registrado no orquestrador
- [ ] Testes unitários criados
- [ ] Documentação atualizada

---

## 9. Roadmap de Implementação

### Fase 1: Agentes Simples (1-2 dias cada)
1. **5W2HAgent** - Estrutura linear simples
2. **SWOTAgent** - 4 quadrantes independentes

### Fase 2: Agentes Intermediários (2-3 dias cada)
3. **TradicionalAgent** - Visão, Missão, Valores, Objetivos Estratégicos
4. **CenariosAgent** - Análise de múltiplos cenários

### Fase 3: Agentes Avançados (3-5 dias cada)
5. **BSCAgent** - 4 perspectivas com indicadores complexos
6. **HoshinAgent** - Desdobramento hierárquico de diretrizes

---

## 10. Referências

- **OKR Agent (Implementado)**: `processos/domain/helena_planejamento_estrategico/agents/okr_agent.py`
- **Orquestrador**: `processos/domain/helena_planejamento_estrategico/pe_orchestrator.py`
- **Schemas**: `processos/domain/helena_planejamento_estrategico/schemas.py`
- **API**: `processos/api/planejamento_estrategico_api.py`

---

## Contato

Dúvidas sobre o padrão? Consulte o OKR Agent como referência ou abra issue no repositório.

**Data de Criação**: 02/11/2025
**Versão**: 1.0
**Status**: ✅ Aprovado para replicação
