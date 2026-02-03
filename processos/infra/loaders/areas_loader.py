"""
Carregamento de Áreas Organizacionais

Responsabilidade única: carregar áreas do CSV com fallback hardcoded.
"""

import logging
import os
from typing import Dict, Any

import pandas as pd

logger = logging.getLogger(__name__)


def _get_csv_path(env_var: str, filename: str) -> str:
    """Helper para construir caminho do CSV."""
    return os.environ.get(
        env_var,
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'documentos_base',
            filename
        )
    )


def carregar_areas_organizacionais() -> Dict[int, Dict[str, Any]]:
    """
    Carrega áreas do CSV com fallback hardcoded.

    Permite escalabilidade: mesmo código serve para DECIPEX, MGI, outros órgãos.
    Basta trocar o CSV ou usar variável de ambiente.

    Returns:
        Dict[int, Dict]: Mapa de ordem -> {codigo, sigla, nome, prefixo, tem_subareas, subareas}
    """
    csv_path = _get_csv_path('AREAS_CSV_PATH', 'areas_organizacionais.csv')

    try:
        df = pd.read_csv(csv_path, encoding='utf-8')

        # Filtrar apenas áreas ativas E que não sejam subáreas (area_pai vazio/NaN)
        if 'area_pai' in df.columns:
            df_ativas = df[(df['ativo'] == True) & (df['area_pai'].isna())].sort_values('ordem')
        else:
            df_ativas = df[df['ativo'] == True].sort_values('ordem')

        # Converter para dicionário no formato esperado
        areas_dict = {}
        for idx, row in df_ativas.iterrows():
            # Tratar prefixo corretamente (remover .0 de inteiros, manter decimais)
            prefixo_float = float(row['prefixo'])
            if prefixo_float == int(prefixo_float):
                prefixo_tratado = str(int(prefixo_float))
            else:
                prefixo_tratado = str(prefixo_float)

            area_info = {
                "codigo": row['codigo'],
                "sigla": row['codigo'],
                "nome": row['nome_completo'],
                "prefixo": prefixo_tratado
            }

            # Adicionar informações de subáreas se existirem
            if 'tem_subareas' in row and row['tem_subareas'] in [True, 'true', 'True']:
                area_info['tem_subareas'] = True
                if 'area_pai' in df.columns:
                    subareas = df[(df['ativo'] == True) & (df['area_pai'] == row['codigo'])]
                else:
                    subareas = pd.DataFrame()

                if not subareas.empty:
                    subareas_list = []
                    for _, sub in subareas.iterrows():
                        sub_prefixo_float = float(sub['prefixo'])
                        if sub_prefixo_float == int(sub_prefixo_float):
                            sub_prefixo = str(int(sub_prefixo_float))
                        else:
                            sub_prefixo = str(sub_prefixo_float)

                        subareas_list.append({
                            'codigo': sub['codigo'],
                            'nome': sub['nome_curto'],
                            'nome_completo': sub['nome_completo'],
                            'prefixo': sub_prefixo
                        })
                    area_info['subareas'] = subareas_list
            else:
                area_info['tem_subareas'] = False

            areas_dict[int(row['ordem'])] = area_info

        logger.info(f"[AREAS] Carregadas do CSV: {len(areas_dict)} areas ativas")
        return areas_dict

    except Exception as e:
        logger.warning(f"⚠️ Erro ao carregar CSV de áreas ({e}). Usando fallback hardcoded.")

        # FALLBACK: Dados hardcoded (segurança)
        return {
            1: {"codigo": "CGBEN", "sigla": "CGBEN", "nome": "Coordenação Geral de Benefícios", "prefixo": "1", "tem_subareas": False},
            2: {"codigo": "CGPAG", "sigla": "CGPAG", "nome": "Coordenação Geral de Pagamentos", "prefixo": "2", "tem_subareas": False},
            3: {"codigo": "COATE", "sigla": "COATE", "nome": "Coordenação de Atendimento", "prefixo": "3", "tem_subareas": False},
            4: {"codigo": "CGGAF", "sigla": "CGGAF", "nome": "Coordenação Geral de Gestão de Acervos Funcionais", "prefixo": "4", "tem_subareas": False},
            5: {"codigo": "DIGEP", "sigla": "DIGEP", "nome": "Divisão de Pessoal dos Ex-Territórios", "prefixo": "5", "tem_subareas": False},
            6: {"codigo": "CGRIS", "sigla": "CGRIS", "nome": "Coordenação Geral de Riscos e Controle", "prefixo": "6", "tem_subareas": False},
            7: {"codigo": "CGCAF", "sigla": "CGCAF", "nome": "Coordenação Geral de Gestão de Complementação da Folha", "prefixo": "7", "tem_subareas": False},
            8: {"codigo": "CGECO", "sigla": "CGECO", "nome": "Coordenação Geral de Extinção e Convênio", "prefixo": "8", "tem_subareas": False}
        }


def carregar_descricoes_areas() -> Dict[str, str]:
    """
    Carrega descrições personalizadas de cada área (do CSV).

    Returns:
        Dict[str, str]: {codigo: descricao}
    """
    csv_path = _get_csv_path('AREAS_CSV_PATH', 'areas_organizacionais.csv')

    try:
        df = pd.read_csv(csv_path)
        df_ativas = df[df['ativo'] == True]

        descricoes = {}
        for idx, row in df_ativas.iterrows():
            descricoes[row['codigo']] = row['descricao']

        return descricoes

    except Exception as e:
        logger.warning(f"⚠️ Erro ao carregar descrições ({e}). Usando fallback.")

        return {
            "CGBEN": "que cuida das concessões, manutenções e revisões de aposentadorias e pensões, garantindo direitos e segurança jurídica aos beneficiários.",
            "CGPAG": "responsável pela execução e controle da folha de pagamentos dos aposentados e pensionistas, garantindo que tudo ocorra com precisão e transparência.",
            "COATE": "que acolhe, orienta e soluciona as demandas dos cidadãos e servidores, garantindo um atendimento humano e eficiente.",
            "CGGAF": "que organiza, digitaliza e mantém o acervo funcional dos servidores, preservando a memória e o acesso seguro às informações.",
            "DIGEP": "que assegura os direitos dos servidores vinculados aos ex-territórios, conduzindo análises e gestões complexas com zelo e compromisso histórico.",
            "CGRIS": "que fortalece a governança, os controles internos e a integridade institucional, promovendo uma gestão pública mais segura e eficiente.",
            "CGCAF": "responsável pela gestão das complementações de aposentadorias e pensões, garantindo equilíbrio e correção dos pagamentos.",
            "CGECO": "que gerencia processos de encerramento de órgãos e acordos administrativos, preservando a continuidade institucional e a responsabilidade pública."
        }
