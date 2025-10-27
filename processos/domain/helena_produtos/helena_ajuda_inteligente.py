# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

"""
Helena - Ajuda Inteligente para Arquitetura de Processos
Sistema que analisa descrição do usuário e sugere classificação completa
da arquitetura (Macroprocesso → Processo → Subprocesso → Atividade → Resultado)
"""

import json
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

def analisar_atividade_com_helena(descricao_usuario, nivel_atual, contexto_ja_selecionado=None):
    """
    Analisa a descrição da atividade do usuário e sugere classificação completa.

    Args:
        descricao_usuario (str): Descrição livre da atividade do usuário
        nivel_atual (str): Nível onde a ajuda foi solicitada ('macro', 'processo', 'subprocesso', 'atividade', 'resultado')
        contexto_ja_selecionado (dict): Contexto já definido pelo usuário
            {
                'macroprocesso': 'Gestão de Aposentadorias',
                'processo': 'Concessão de aposentadorias',
                ...
            }

    Returns:
        dict: {
            'sucesso': True/False,
            'sugestao': {
                'macroprocesso': 'Nome do macroprocesso',
                'processo': 'Nome do processo',
                'subprocesso': 'Nome do subprocesso',
                'atividade': 'Nome da atividade',
                'resultado_final': 'Nome do resultado'
            },
            'justificativa': 'Explicação da Helena sobre a classificação',
            'confianca': 'alta' | 'media' | 'baixa'
        }
    """

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Montar contexto baseado no que já foi selecionado
        contexto_texto = ""
        if contexto_ja_selecionado:
            contexto_texto = "\n\n**CONTEXTO JÁ DEFINIDO PELO USUÁRIO:**\n"
            if contexto_ja_selecionado.get('macroprocesso'):
                contexto_texto += f"- Macroprocesso: {contexto_ja_selecionado['macroprocesso']}\n"
            if contexto_ja_selecionado.get('processo'):
                contexto_texto += f"- Processo: {contexto_ja_selecionado['processo']}\n"
            if contexto_ja_selecionado.get('subprocesso'):
                contexto_texto += f"- Subprocesso: {contexto_ja_selecionado['subprocesso']}\n"
            if contexto_ja_selecionado.get('atividade'):
                contexto_texto += f"- Atividade: {contexto_ja_selecionado['atividade']}\n"

        # Prompt para o GPT-4
        prompt = f"""Você é Helena, assistente especialista em mapeamento de processos do serviço público brasileiro.

Um usuário precisa classificar sua atividade na arquitetura de processos, mas está com dúvida.

**Arquitetura de Processos (4 níveis):**
1. **Macroprocesso**: Conjunto amplo de processos relacionados (ex: "Gestão de Aposentadorias", "Gestão de Benefícios")
2. **Processo**: Conjunto de atividades relacionadas (ex: "Concessão de aposentadorias", "Manutenção de aposentadorias")
3. **Subprocesso**: Divisão específica do processo (ex: "Análise de documentos", "Cálculo de proventos")
4. **Atividade**: Tarefa específica executada (ex: "Validar tempo de contribuição", "Calcular valor da aposentadoria")
5. **Resultado Final**: O que é entregue ao final (ex: "Aposentadoria concedida", "Parecer de indeferimento")
{contexto_texto}
**Descrição do usuário sobre o que ele faz:**
"{descricao_usuario}"

**Sua tarefa:**
Analise a descrição e sugira a classificação completa nos 5 níveis. Se algum nível já foi definido pelo contexto, MANTENHA o valor do contexto.

**IMPORTANTE:**
- Use linguagem clara e objetiva do setor público
- Se não houver contexto definido, sugira TODOS os 5 níveis
- Se houver contexto parcial (ex: Macroprocesso já definido), sugira apenas os níveis seguintes
- Seja específico e use terminologia do serviço público
- Avalie sua confiança: alta (muito claro), média (provável), baixa (incerto)

Retorne APENAS um JSON válido no seguinte formato:
{{
    "macroprocesso": "Nome do macroprocesso",
    "processo": "Nome do processo",
    "subprocesso": "Nome do subprocesso",
    "atividade": "Nome da atividade",
    "resultado_final": "Nome do resultado final",
    "justificativa": "Explicação breve de por que você classificou assim",
    "confianca": "alta" ou "media" ou "baixa"
}}"""

        # Chamar GPT-4
        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "Você é Helena, assistente especialista em mapeamento de processos do serviço público brasileiro. Sempre retorne JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )

        resposta_helena = response.choices[0].message.content.strip()

        # Tentar parsear JSON
        # Remover markdown se houver
        if "```json" in resposta_helena:
            resposta_helena = resposta_helena.split("```json")[1].split("```")[0].strip()
        elif "```" in resposta_helena:
            resposta_helena = resposta_helena.split("```")[1].split("```")[0].strip()

        sugestao = json.loads(resposta_helena)

        # Garantir que contexto já definido seja mantido
        if contexto_ja_selecionado:
            for campo in ['macroprocesso', 'processo', 'subprocesso', 'atividade']:
                if contexto_ja_selecionado.get(campo):
                    sugestao[campo] = contexto_ja_selecionado[campo]

        return {
            'sucesso': True,
            'sugestao': sugestao,
            'justificativa': sugestao.get('justificativa', 'Classificação baseada na análise da descrição fornecida.'),
            'confianca': sugestao.get('confianca', 'media')
        }

    except json.JSONDecodeError as e:
        return {
            'sucesso': False,
            'erro': f'Erro ao processar resposta da IA: {str(e)}',
            'resposta_bruta': resposta_helena if 'resposta_helena' in locals() else None
        }
    except Exception as e:
        return {
            'sucesso': False,
            'erro': f'Erro ao analisar atividade: {str(e)}'
        }


def validar_sugestao_contra_csv(sugestao, arquitetura):
    """
    Valida se a sugestão existe no CSV de arquitetura.
    Se não existir, retorna como texto customizado.

    Args:
        sugestao (dict): Sugestão da Helena com os 5 níveis
        arquitetura: Instância de ArquiteturaProcessos

    Returns:
        dict: {
            'macroprocesso': {'existe': True/False, 'valor': 'nome'},
            'processo': {'existe': True/False, 'valor': 'nome'},
            ...
        }
    """
    from .dados_decipex import ArquiteturaDecipex

    if not arquitetura:
        arquitetura = ArquiteturaDecipex()

    validacao = {}

    # Validar Macroprocesso
    macros = arquitetura.obter_macroprocessos_unicos()
    validacao['macroprocesso'] = {
        'existe': sugestao['macroprocesso'] in macros,
        'valor': sugestao['macroprocesso']
    }

    # Validar Processo
    if validacao['macroprocesso']['existe']:
        processos = arquitetura.obter_processos_por_macro(sugestao['macroprocesso'])
        validacao['processo'] = {
            'existe': sugestao['processo'] in processos,
            'valor': sugestao['processo']
        }
    else:
        validacao['processo'] = {
            'existe': False,
            'valor': sugestao['processo']
        }

    # Validar Subprocesso
    if validacao['processo']['existe']:
        subprocessos = arquitetura.obter_subprocessos_por_processo(
            sugestao['macroprocesso'],
            sugestao['processo']
        )
        validacao['subprocesso'] = {
            'existe': sugestao['subprocesso'] in subprocessos,
            'valor': sugestao['subprocesso']
        }
    else:
        validacao['subprocesso'] = {
            'existe': False,
            'valor': sugestao['subprocesso']
        }

    # Validar Atividade
    if validacao['subprocesso']['existe']:
        atividades = arquitetura.obter_atividades_por_subprocesso(
            sugestao['macroprocesso'],
            sugestao['processo'],
            sugestao['subprocesso']
        )
        validacao['atividade'] = {
            'existe': sugestao['atividade'] in atividades,
            'valor': sugestao['atividade']
        }
    else:
        validacao['atividade'] = {
            'existe': False,
            'valor': sugestao['atividade']
        }

    # Resultado final sempre é customizado
    validacao['resultado_final'] = {
        'existe': False,  # Sempre customizado
        'valor': sugestao['resultado_final']
    }

    return validacao
