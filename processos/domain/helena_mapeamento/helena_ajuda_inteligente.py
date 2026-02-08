# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

"""
Helena - Ajuda Inteligente para Arquitetura de Processos + Método CAP

Sistema que:
1. PRIORIZA busca no CSV oficial (match exato/fuzzy)
2. Só chama IA quando não encontrar no CSV
3. Gera CAP oficial (CSV) ou provisório (nova atividade)
4. Integra com rastreabilidade completa

Ordem de prioridade:
1. Match exato no CSV (≈99% dos casos)
2. Match fuzzy >= 85% (similaridade textual)
3. IA generativa (casos novos/ambíguos)
"""

import json
from openai import OpenAI
from dotenv import load_dotenv
import os
import pandas as pd
from rapidfuzz import process, fuzz
from datetime import datetime
import hashlib
from django.db import transaction
import logging

load_dotenv()
logger = logging.getLogger(__name__)

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

        # Carregar os 12 macroprocessos oficiais do CSV
        import pandas as pd
        csv_path = 'documentos_base/Arquitetura_DECIPEX_mapeada.csv'
        df = pd.read_csv(csv_path)
        macros_oficiais = df['Macroprocesso'].unique().tolist()
        lista_macros = "\n".join([f"{i+1}. {macro}" for i, macro in enumerate(macros_oficiais)])

        # Prompt para o GPT-4
        prompt = f"""Você é Helena, assistente especialista em mapeamento de processos do serviço público brasileiro.

**RESTRIÇÃO CRÍTICA - MACROPROCESSOS OFICIAIS:**
Você DEVE escolher OBRIGATORIAMENTE um dos seguintes 12 macroprocessos oficiais da DECIPEX:

{lista_macros}

❌ NÃO INVENTE novos macroprocessos.
❌ NÃO USE nomes diferentes dos listados acima.
✅ Use EXATAMENTE um dos nomes acima (copie o texto exato).

**Arquitetura de Processos (5 níveis):**
1. **Macroprocesso**: OBRIGATORIAMENTE um dos 12 listados acima
2. **Processo**: Conjunto de atividades relacionadas
3. **Subprocesso**: Divisão específica do processo
4. **Atividade**: Tarefa específica executada
5. **Resultado Final**: O que é entregue ao final
{contexto_texto}
**Descrição do usuário sobre o que ele faz:**
"{descricao_usuario}"

**Sua tarefa:**
Analise a descrição e sugira a classificação completa nos 5 níveis.

**REGRAS:**
- Macroprocesso: copie EXATAMENTE um dos 12 nomes listados acima
- Processo/Subprocesso: devem ser compatíveis com a estrutura oficial
- Se contexto já definido, MANTENHA os valores
- Avalie confiança: alta (muito claro), media (provável), baixa (incerto)

Retorne APENAS um JSON válido:
{{
    "macroprocesso": "Nome EXATO de um dos 12 acima",
    "processo": "Nome do processo",
    "subprocesso": "Nome do subprocesso",
    "atividade": "Nome da atividade",
    "resultado_final": "Nome do resultado final",
    "justificativa": "Breve explicação",
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


# ============================================================================
# INTEGRAÇÃO HELENA + MÉTODO CAP
# ============================================================================

def classificar_e_gerar_cap(descricao_usuario, area_codigo, contexto=None, autor_dados=None):
    """
    Classifica atividade e gera CAP (oficial ou provisório)

    PRIORIDADE:
    1. Match exato no CSV → retorna CAP oficial
    2. Match fuzzy >= 85% → retorna CAP oficial
    3. Não encontrou → IA sugere → gera CAP provisório

    Args:
        descricao_usuario (str): Descrição da atividade
        area_codigo (str): Código da área (ex: 'CGBEN', 'CGPAG')
        contexto (dict): Contexto já selecionado (opcional)
        autor_dados (dict): Dados do autor para rastreabilidade
            {
                'cpf': '12345678900',
                'nome': 'João Silva',
                'area': 'CGBEN'
            }

    Returns:
        dict: {
            'sucesso': True/False,
            'tipo_cap': 'oficial' | 'provisorio',
            'origem_fluxo': 'match_exato' | 'match_fuzzy' | 'nova_atividade_ia',
            'cap': '1.02.03.04.XXX',
            'macroprocesso': str,
            'processo': str,
            'subprocesso': str,
            'atividade': str,
            'resultado_final': str,
            'justificativa': str,
            'confianca': 'alta' | 'media' | 'baixa'
        }
    """

    try:
        # 1️⃣ Carregar CSV
        csv_path = 'documentos_base/Arquitetura_DECIPEX_mapeada.csv'
        df = pd.read_csv(csv_path)

        # 🔍 DIAGNÓSTICO: Logs detalhados para debug
        logger.info("="*80)
        logger.info("[BUSCA] DIAGNÓSTICO DE BUSCA NO CSV")
        logger.info("="*80)
        logger.info(f"[INFO] Colunas do CSV: {df.columns.tolist()}")
        logger.info(f"[INFO] Total de linhas: {len(df)}")
        logger.info(f"[INFO] Primeiras 3 linhas:\n{df.head(3)}")
        logger.info(f"[BUSCA] Buscando: '{descricao_usuario}' (len={len(descricao_usuario)}, type={type(descricao_usuario)})")

        df = df.fillna('')

        # Verificar tipos e amostras das colunas de busca
        colunas_busca = ['Macroprocesso', 'Processo', 'Subprocesso', 'Atividade']
        for col in colunas_busca:
            if col in df.columns:
                logger.info(f"[DEBUG] Coluna '{col}':")
                logger.info(f"   - Tipo: {df[col].dtype}")
                logger.info(f"   - Valores únicos: {df[col].nunique()}")
                if len(df[col]) > 0:
                    amostra = df[col].iloc[0]
                    logger.info(f"   - Amostra [0]: '{amostra}' (len={len(str(amostra))})")
                    logger.info(f"   - Encoding bytes: {amostra.encode('utf-8') if isinstance(amostra, str) else 'N/A'}")
            else:
                logger.warning(f"⚠️ Coluna '{col}' NÃO ENCONTRADA no CSV!")

        logger.info("="*80)

        # 2️⃣ Match EXATO (case insensitive) - busca em todas colunas relevantes
        logger.info("[BUSCA] Tentando MATCH EXATO...")
        for col in colunas_busca:
            if col not in df.columns:
                continue
            logger.info(f"   Buscando em '{col}'...")
            descricao_lower = descricao_usuario.lower().strip()
            logger.info(f"   Termo normalizado: '{descricao_lower}'")
            match_exato = df[df[col].str.lower().str.strip() == descricao_lower]
            logger.info(f"   Resultados encontrados: {len(match_exato)}")
            if not match_exato.empty:
                linha = match_exato.iloc[0]
                logger.info(f"[OK] Match exato encontrado em '{col}'!")
                logger.info(f"   Linha matched: {linha.to_dict()}")

                return {
                    'sucesso': True,
                    'tipo_cap': 'oficial',
                    'origem_fluxo': 'match_exato',
                    'cap': _gerar_cap_oficial(linha, area_codigo),
                    'macroprocesso': linha['Macroprocesso'],
                    'processo': linha['Processo'],
                    'subprocesso': linha['Subprocesso'],
                    'atividade': linha['Atividade'],
                    'resultado_final': f"{linha['Atividade']} concluída",  # Inferir resultado
                    'justificativa': f"Encontrado no catálogo oficial (correspondência exata em '{col}').",
                    'confianca': 'alta'
                }

        logger.info("[ERRO] Nenhum match exato encontrado")

        # 3️⃣ Match FUZZY >= 85% (busca por similaridade)
        logger.info("[BUSCA] Tentando MATCH FUZZY (threshold >= 85%)...")
        todas_atividades = df['Atividade'].tolist()
        logger.info(f"   Total de atividades para comparar: {len(todas_atividades)}")
        logger.info(f"   Primeiras 3 atividades: {todas_atividades[:3]}")

        if todas_atividades:
            match_result = process.extractOne(
                descricao_usuario,
                todas_atividades,
                scorer=fuzz.token_sort_ratio
            )
            logger.info(f"   Resultado do fuzzy: {match_result}")

            if match_result:
                match_texto, score, idx = match_result
                logger.info(f"   Melhor match: '{match_texto}' (score: {score}%, índice: {idx})")

                if score >= 85:
                    linha = df.iloc[idx]
                    logger.info(f"[OK] Match fuzzy encontrado: '{match_texto}' (score: {score}%)")
                    logger.info(f"   Linha matched: {linha.to_dict()}")

                    return {
                        'sucesso': True,
                        'tipo_cap': 'oficial',
                        'origem_fluxo': 'match_fuzzy',
                        'cap': _gerar_cap_oficial(linha, area_codigo),
                        'macroprocesso': linha['Macroprocesso'],
                        'processo': linha['Processo'],
                        'subprocesso': linha['Subprocesso'],
                        'atividade': linha['Atividade'],
                        'resultado_final': f"{linha['Atividade']} concluída",
                        'justificativa': f"Encontrado no catálogo oficial (similaridade de {score:.1f}% com '{match_texto}').",
                        'confianca': 'media' if score < 95 else 'alta'
                    }
                else:
                    logger.info(f"[AVISO] Melhor match: '{match_texto}' ({score}%) - abaixo do limite (85%)")
            else:
                logger.info("[AVISO] process.extractOne retornou None")
        else:
            logger.info("[AVISO] Lista de atividades está vazia")

        logger.info("[ERRO] Nenhum match fuzzy encontrado")

        # 4️⃣ Não encontrou → retornar "não encontrado" para o pipeline decidir
        logger.info("="*80)
        logger.info("[CAMADA 1] Nenhum match no CSV - retornando 'encontrado=False'")
        logger.info("[CAMADA 1] Pipeline decidirá próximas camadas (semântica/RAG)")
        logger.info("="*80)

        return {
            'sucesso': True,
            'encontrado': False
        }

    except Exception as e:
        logger.error(f"❌ Erro em classificar_e_gerar_cap: {e}")
        import traceback
        traceback.print_exc()

        return {
            'sucesso': False,
            'erro': str(e)
        }


def _gerar_cap_oficial(linha_csv, area_codigo):
    """
    Retorna CAP oficial da linha do CSV, com prefixo da área.

    Formato: PREFIXO_AREA.NUMERO_CSV  (ex: 3.7.1.1.1 para COATE)

    REGRA: Camadas 1-3 SEMPRE retornam CAP do CSV oficial.
    CAP é obrigatório - se não existir, lança exceção.
    """
    import pandas as pd

    # Verificar se campo Numero existe e está preenchido
    if 'Numero' not in linha_csv.index:
        raise ValueError("Campo 'Numero' não encontrado no CSV oficial.")

    numero_csv = linha_csv['Numero']

    # Validar que CAP não é vazio/None
    if pd.isna(numero_csv) or not str(numero_csv).strip():
        raise ValueError(
            f"Atividade '{linha_csv.get('Atividade', 'N/A')}' não possui CAP registrado no CSV oficial. "
            f"Todas as atividades nas Camadas 1-3 devem ter CAP obrigatório."
        )

    numero = str(numero_csv).strip()

    # Adicionar prefixo da área (ex: COATE -> "3", CGRIS -> "6")
    if area_codigo:
        from processos.infra.loaders import carregar_areas_organizacionais
        areas = carregar_areas_organizacionais()
        prefixo = None
        for info in areas.values():
            if info.get('codigo') == area_codigo:
                prefixo = info.get('prefixo')
                break
        if prefixo:
            return f"{prefixo}.{numero}"

    return numero


# FUNÇÃO _gerar_cap_provisorio() REMOVIDA
# Motivo: CAP provisório foi abolido. RAG agora gera CAP sequencial oficial.
# Ref: Correção v3.5 - Todas as atividades têm CAP oficial desde a criação.
