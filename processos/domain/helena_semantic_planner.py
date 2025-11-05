"""
Helena Semantic Planner v1.0
------------------------------------
Camada de tradução semântica de linguagem natural para conceitos de gestão pública.
Usada por agentes como OKRAgent, RiskAgent, ActionPlanAgent, etc.

Função central: interpretar mensagens livres e identificar sua intenção de gestão.

Exemplo:
    "Estamos com muito retrabalho"
    → {'tipo': 'problema', 'conceito': 'ineficiência', 'proposta': 'Reduzir retrabalho'}

Autor: MapaGov + Claude
Data: 2025-01
"""

import re
from typing import Dict, Any, List


class HelenaSemanticPlanner:
    """
    Traduz linguagem natural em conceitos formais de planejamento estratégico.

    Atua como interpretador neutro (sem depender de método específico OKR, SWOT, etc.)
    Fornece biblioteca de padrões e funções reutilizáveis para todos os agentes.
    """

    # ═══════════════════════════════════════════════════════════════
    # 📚 VOCABULÁRIO DE REFERÊNCIA (Expansível)
    # ═══════════════════════════════════════════════════════════════

    PADROES_OBJETIVO = [
        'melhorar', 'aumentar', 'fortalecer', 'reduzir', 'garantir',
        'tornar', 'modernizar', 'transformar', 'consolidar', 'ampliar',
        'otimizar', 'aprimorar', 'elevar', 'impulsionar', 'desenvolver',
        'expandir', 'promover', 'fomentar', 'assegurar', 'instituir',
        'objetivo', 'objetivos', 'meta', 'metas', 'propósito', 'intenção'
    ]

    PADROES_RESULTADO = [
        'atingir', 'alcançar', 'meta', 'resultado', 'indicador',
        'de .* para', 'em .* %', 'até', 'pelo menos', 'no mínimo',
        r'\d+%', r'\d+ pontos', r'\d+ dias', r'\d+ horas',
        'crescer', 'diminuir', 'chegar a', 'elevar para',
        'kr', 'krs', 'key result', 'resultado-chave', 'resultados-chave'
    ]

    PADROES_PROBLEMA = [
        'problema', 'dificuldade', 'gargalo', 'demora', 'atraso',
        'não funciona', 'falha', 'erro', 'reclamação', 'insatisfação',
        'cada um por conta', 'cada uma por conta', 'por conta própria',
        'desorganizado', 'sem padrão', 'retrabalho', 'queria que', 'seria bom se',
        'precisa parar', 'tem que parar', 'ineficiência', 'lenta', 'lento',
        'devagar', 'travado', 'emperrado', 'não tem', 'falta', 'está ruim',
        'preciso saber', 'quero saber', 'necessito', 'seria importante',
        'falta clareza', 'não sei', 'difícil de', 'complicado',
        # Padrões de desejo/necessidade (convertem em objetivos)
        'quero', 'preciso', 'desejo', 'almejo', 'gostaria', 'queria', 'seria bom',
        'eu quero', 'eu preciso', 'eu desejo', 'eu almejo', 'eu gostaria', 'eu queria',
        'não consigo', 'nao consigo', 'tenho dificuldade', 'não está claro',
        'estamos com', 'há muito', 'não sei o que cada', 'não sei quem faz',
        'confusão', 'alocar', 'distribuir melhor', 'saber o que', 'saber quem'
    ]

    PADROES_RISCO = [
        'risco', 'ameaça', 'vulnerabilidade', 'incerteza',
        'pode acontecer', 'possibilidade de', 'chance de',
        'probabilidade', 'exposição'
    ]

    PADROES_VALOR = [
        'valor público', 'benefício', 'impacto', 'importância', 'relevância',
        'cidadão', 'sociedade', 'transparência', 'eficiência', 'qualidade',
        'resultado para sociedade'
    ]

    # Contextos setoriais (setor público brasileiro)
    CONTEXTOS_SETORIAIS = {
        'atendimento': [
            'atendimento', 'cidadão', 'usuário', 'cliente', 'canal',
            'demanda', 'solicitação', 'protocolo', 'SAC'
        ],
        'processos': [
            'processo', 'tramitação', 'workflow', 'procedimento',
            'fluxo', 'etapa', 'rotina', 'atividade'
        ],
        'colaboracao': [
            'equipe', 'time', 'colabor', 'integr', 'junto',
            'cada um por conta', 'compartilhar', 'cooperar'
        ],
        'dados': [
            'dado', 'informação', 'métrica', 'indicador', 'dashboard',
            'relatório', 'análise', 'monitoramento'
        ],
        'financeiro': [
            'orçamento', 'recurso', 'verba', 'custo', 'investimento',
            'gasto', 'despesa', 'economia'
        ],
        'tecnologia': [
            'sistema', 'TI', 'tecnologia', 'software', 'digital',
            'automação', 'ferramenta', 'plataforma'
        ]
    }

    def __init__(self):
        """Inicializa o planejador semântico"""
        pass

    # ═══════════════════════════════════════════════════════════════
    # 🧠 MOTOR DE INTERPRETAÇÃO
    # ═══════════════════════════════════════════════════════════════

    def interpretar(self, mensagem: str) -> Dict[str, Any]:
        """
        Interpreta uma frase livre e classifica em tipo de conceito de gestão.

        Args:
            mensagem: Frase do usuário em linguagem natural

        Returns:
            dict: {
                'tipo': str,  # 'objetivo', 'resultado', 'problema', 'risco', 'valor', 'neutro'
                'texto_original': str,
                'contexto_setorial': str,  # 'atendimento', 'processos', etc.
                'confianca': float,  # 0.0-1.0
                'proposta': str  # Sugestão de formulação
            }
        """
        texto = mensagem.lower().strip()

        # Score de correspondência por categoria
        scores = {
            'objetivo': 0,
            'resultado': 0,
            'problema': 0,
            'risco': 0,
            'valor': 0
        }

        # ⚠️ PROBLEMA tem prioridade (peso 2x)
        for padrao in self.PADROES_PROBLEMA:
            if padrao in texto:
                scores['problema'] += 2

        # Verifica padrões de OBJETIVO
        for padrao in self.PADROES_OBJETIVO:
            if padrao in texto:
                scores['objetivo'] += 1

        # Verifica padrões de RESULTADO (inclui regex)
        for padrao in self.PADROES_RESULTADO:
            if re.search(padrao, texto):
                scores['resultado'] += 1

        # Verifica padrões de RISCO
        for padrao in self.PADROES_RISCO:
            if padrao in texto:
                scores['risco'] += 1

        # Verifica padrões de VALOR
        for padrao in self.PADROES_VALOR:
            if padrao in texto:
                scores['valor'] += 1

        # Detecta contexto setorial
        contexto_setorial = self._detectar_contexto_setorial(texto)

        # Classifica tipo dominante
        tipo_detectado = max(scores, key=scores.get)
        score_max = scores[tipo_detectado]

        # 🔍 FALLBACK: Palavras isoladas (objetivo, resultado, kr)
        if score_max == 0:
            # Detecta intenção semântica mínima em frases curtas
            if texto in ["objetivo", "objetivos"]:
                tipo_detectado = "objetivo"
                score_max = 1
            elif texto in ["resultado", "resultados", "kr", "krs", "resultado-chave", "resultados-chave"]:
                tipo_detectado = "resultado"
                score_max = 1
            else:
                tipo_detectado = 'neutro'

        # Calcula confiança
        total_scores = sum(scores.values())
        confianca = score_max / total_scores if total_scores > 0 else 0.0

        # Gera proposta contextual
        proposta = self._gerar_proposta(tipo_detectado, mensagem, contexto_setorial)

        return {
            'tipo': tipo_detectado,
            'texto_original': mensagem,
            'contexto_setorial': contexto_setorial,
            'confianca': confianca,
            'proposta': proposta
        }

    def _detectar_contexto_setorial(self, texto: str) -> str:
        """
        Detecta área setorial da frase (para buscar exemplos contextualizados)

        Args:
            texto: Texto em lowercase

        Returns:
            str: 'atendimento', 'processos', 'colaboracao', 'dados', etc.
        """
        for contexto, palavras_chave in self.CONTEXTOS_SETORIAIS.items():
            if any(palavra in texto for palavra in palavras_chave):
                return contexto

        return 'geral'

    def _gerar_proposta(self, tipo: str, mensagem: str, contexto: str) -> str:
        """
        Gera uma formulação sugerida conforme tipo identificado

        Args:
            tipo: Tipo de conceito ('objetivo', 'problema', etc.)
            mensagem: Mensagem original
            contexto: Contexto setorial

        Returns:
            str: Proposta de reformulação
        """
        msg_limpa = mensagem.strip().capitalize()

        if tipo == 'objetivo':
            return f"🎯 Isso parece um **objetivo estratégico**:\n\n> {msg_limpa}\n\nPode ser formulado como:\n**'{self._refinar_objetivo_generico(mensagem)}'**"

        elif tipo == 'resultado':
            return f"📊 Isso soa como um **resultado mensurável**:\n\n> {msg_limpa}\n\nExemplo formatado:\n**'{msg_limpa} (de X para Y)'**"

        elif tipo == 'problema':
            objetivo_invertido = self._inverter_problema_generico(mensagem)
            return f"⚠️ Identifiquei um **problema/necessidade**:\n\n> {msg_limpa}\n\nPodemos transformá-lo em objetivo estratégico:\n**'{objetivo_invertido}'**"

        elif tipo == 'risco':
            return f"🚨 Isso expressa um **risco ou incerteza**:\n\n> {msg_limpa}\n\nPode virar um registro de risco:\n**'Risco de {msg_limpa.lower()}'**"

        elif tipo == 'valor':
            return f"💎 Isso reflete um **valor público** ou impacto desejado:\n\n> {msg_limpa}\n\n**'Gerar valor público por meio de {msg_limpa.lower()}'**"

        else:
            return f"💬 Essa frase pode ser traduzida para planejamento:\n\n> {msg_limpa}\n\nPode se tornar um objetivo, risco ou valor."

    # ═══════════════════════════════════════════════════════════════
    # 🔧 FUNÇÕES AUXILIARES DE TRADUÇÃO
    # ═══════════════════════════════════════════════════════════════

    def _inverter_problema_generico(self, texto: str) -> str:
        """
        Inverte problema/necessidade em objetivo positivo (versão genérica)

        Args:
            texto: Problema descrito em linguagem natural

        Returns:
            str: Objetivo positivo
        """
        texto_lower = texto.lower()

        # Padrões de inversão específicos
        if 'cada um por conta' in texto_lower or 'cada uma por conta' in texto_lower or 'por conta própria' in texto_lower:
            return "Fortalecer a integração e o trabalho colaborativo"

        if 'demora' in texto_lower or 'lento' in texto_lower or 'lenta' in texto_lower or 'devagar' in texto_lower:
            return "Acelerar os processos e reduzir tempo de resposta"

        if 'desorganizado' in texto_lower or 'bagunça' in texto_lower:
            return "Estruturar e organizar os processos"

        if 'retrabalho' in texto_lower:
            return "Eliminar retrabalhos e padronizar processos"

        if 'insatisfação' in texto_lower or 'reclamação' in texto_lower:
            return "Elevar a satisfação e a qualidade"

        if 'transparência' in texto_lower or 'transparente' in texto_lower:
            return "Fortalecer a transparência e a prestação de contas"

        if 'atendimento' in texto_lower and any(palavra in texto_lower for palavra in ['melhorar', 'precisa', 'queremos']):
            return "Melhorar a experiência do cidadão no atendimento"

        # Necessidade de informação/visibilidade
        if any(palavra in texto_lower for palavra in ['preciso saber', 'quero saber', 'saber o que', 'saber quem', 'não consigo ver', 'nao consigo ver', 'ver quem faz', 'quem faz o']):
            if any(palavra in texto_lower for palavra in ['equipe', 'pessoa', 'cada um', 'quem faz', 'atividade', 'fazendo']):
                return "Aumentar a visibilidade sobre as atividades e responsabilidades da equipe"
            else:
                return "Melhorar o acesso e a clareza das informações"

        # Alocação e distribuição
        if 'alocar' in texto_lower or 'distribuir' in texto_lower:
            if 'equipe' in texto_lower or 'pessoa' in texto_lower or 'time' in texto_lower:
                return "Otimizar a alocação e distribuição de recursos da equipe"
            else:
                return "Otimizar a alocação de recursos"

        # Clareza nos processos
        if 'clareza' in texto_lower or 'claro' in texto_lower:
            if 'processo' in texto_lower:
                return "Aumentar a clareza e padronização dos processos"
            else:
                return "Aumentar a clareza e transparência"

        # Colaboração e integração
        if 'colabora' in texto_lower or 'integra' in texto_lower:
            return "Fortalecer a colaboração e integração da equipe"

        # Fallback genérico: busca verbos de problema e inverte
        if any(verbo in texto_lower for verbo in ['falha', 'erro', 'não funciona']):
            return "Garantir o funcionamento adequado"

        # Remove prefixos de desejo antes do fallback
        prefixos_desejo = [
            'eu quero ', 'eu preciso ', 'eu desejo ', 'eu almejo ', 'eu gostaria ', 'eu queria ',
            'quero ', 'preciso ', 'desejo ', 'almejo ', 'gostaria ', 'queria ',
            'seria bom ', 'seria importante '
        ]

        texto_limpo = texto.strip()
        texto_limpo_lower = texto_limpo.lower()

        for prefixo in prefixos_desejo:
            if texto_limpo_lower.startswith(prefixo):
                texto_limpo = texto_limpo[len(prefixo):].strip()
                break

        # Se não detectou padrão específico, capitaliza e retorna com verbo apropriado
        if texto_limpo:
            return texto_limpo[0].upper() + texto_limpo[1:]

        return f"Melhorar {texto.strip()}"

    def _refinar_objetivo_generico(self, texto: str) -> str:
        """
        Refina objetivo em linguagem natural para formato mais técnico

        Args:
            texto: Objetivo em linguagem natural

        Returns:
            str: Objetivo refinado
        """
        texto_limpo = texto.strip()
        texto_lower = texto_limpo.lower()

        # Remove prefixos conversacionais
        prefixos_remover = [
            'queremos ', 'quero ', 'precisamos ', 'preciso ',
            'gostaríamos de ', 'gostaria de ', 'vamos ',
            'temos que ', 'tenho que '
        ]

        for prefixo in prefixos_remover:
            if texto_lower.startswith(prefixo):
                texto_limpo = texto_limpo[len(prefixo):].strip()
                texto_lower = texto_limpo.lower()
                break

        # Garante que começa com verbo no infinitivo
        verbos_validos = [
            'melhorar', 'aumentar', 'fortalecer', 'reduzir', 'garantir',
            'tornar', 'modernizar', 'transformar', 'consolidar', 'ampliar',
            'otimizar', 'aprimorar', 'elevar', 'impulsionar', 'desenvolver'
        ]

        if len(texto_limpo.split()) > 0:
            primeira_palavra = texto_limpo.split()[0].lower()

            if primeira_palavra in verbos_validos:
                return texto_limpo.capitalize()

        # Se não começa com verbo, adiciona "Fortalecer" como fallback
        return f"Fortalecer {texto_limpo.lower()}"

    def extrair_lista(self, mensagem: str) -> List[str]:
        """
        Extrai lista de items da mensagem (útil para KRs, ações, etc.)

        Suporta:
        - Lista com bullets (-, *, •)
        - Lista numerada (1., 2., 3.)
        - Lista separada por quebras de linha

        Args:
            mensagem: Texto com lista

        Returns:
            List[str]: Items extraídos
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

    def validar_mensurabilidade(self, texto: str) -> bool:
        """
        Valida se um texto contém elementos mensuráveis (número, %, prazo)

        Args:
            texto: Texto a validar

        Returns:
            bool: True se mensurável
        """
        tem_numero = bool(re.search(r'\d+', texto))
        tem_percentual = '%' in texto
        tem_prazo = any(palavra in texto.lower() for palavra in ['dias', 'horas', 'meses', 'anos', 'prazo'])

        return tem_numero or tem_percentual or tem_prazo
