"""
Carregamento da Arquitetura DECIPEX

Responsabilidade única: carregar e consultar arquitetura de processos.
"""

import logging
import os
from typing import Dict, Any, List

import pandas as pd

logger = logging.getLogger(__name__)


class ArquiteturaDecipex:
    """Carrega e consulta arquitetura de processos da DECIPEX"""

    def __init__(self, caminho_csv: str = None):
        if caminho_csv is None:
            caminho_csv = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                'documentos_base',
                'Arquitetura_DECIPEX_mapeada.csv'
            )

        try:
            self.df = pd.read_csv(caminho_csv)
        except FileNotFoundError:
            logger.warning(f"Arquivo CSV não encontrado: {caminho_csv}")
            self.df = pd.DataFrame(columns=['Macroprocesso', 'Processo', 'Subprocesso', 'Atividade'])
        except Exception as e:
            logger.error(f"Erro ao carregar CSV: {e}")
            self.df = pd.DataFrame(columns=['Macroprocesso', 'Processo', 'Subprocesso', 'Atividade'])

    def obter_macroprocessos_unicos(self) -> List[str]:
        return self.df['Macroprocesso'].unique().tolist()

    def obter_processos_por_macro(self, macro: str) -> List[str]:
        return self.df[self.df['Macroprocesso'] == macro]['Processo'].unique().tolist()

    def obter_subprocessos_por_processo(self, macro: str, processo: str) -> List[str]:
        filtro = (self.df['Macroprocesso'] == macro) & (self.df['Processo'] == processo)
        return self.df[filtro]['Subprocesso'].unique().tolist()

    def obter_atividades_por_subprocesso(self, macro: str, processo: str, subprocesso: str) -> List[str]:
        filtro = (
            (self.df['Macroprocesso'] == macro) &
            (self.df['Processo'] == processo) &
            (self.df['Subprocesso'] == subprocesso)
        )
        return self.df[filtro]['Atividade'].unique().tolist()


def carregar_arquitetura_csv() -> Dict[str, Any]:
    """
    Carrega CSV com atividades mapeadas e estrutura hierarquicamente.

    Returns:
        dict: Estrutura hierárquica {
            'macroprocessos': {
                'Gestão de Benefícios Previdenciários': {
                    'processos': {
                        'Gestão de Aposentadorias': {
                            'subprocessos': {
                                'Concessão de aposentadorias': {
                                    'atividades': ['Conceder benefício...', ...]
                                }
                            }
                        }
                    }
                }
            },
            'flat_list': [  # Lista plana para busca rápida
                {
                    'macroprocesso': '...',
                    'processo': '...',
                    'subprocesso': '...',
                    'atividade': '...'
                }
            ]
        }
    """
    csv_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        'documentos_base',
        'Arquitetura_DECIPEX_mapeada.csv'
    )

    try:
        df = pd.read_csv(csv_path, encoding='utf-8')

        # Estrutura hierárquica
        hierarquia = {}
        lista_plana = []

        for _, row in df.iterrows():
            macro = row['Macroprocesso']
            processo = row['Processo']
            subprocesso = row['Subprocesso']
            atividade = row['Atividade']

            # Pular linhas vazias
            if pd.isna(macro) or pd.isna(atividade):
                continue

            # Adicionar à lista plana
            lista_plana.append({
                'macroprocesso': macro,
                'processo': processo,
                'subprocesso': subprocesso,
                'atividade': atividade
            })

            # Construir hierarquia
            if macro not in hierarquia:
                hierarquia[macro] = {'processos': {}}

            if processo not in hierarquia[macro]['processos']:
                hierarquia[macro]['processos'][processo] = {'subprocessos': {}}

            if subprocesso not in hierarquia[macro]['processos'][processo]['subprocessos']:
                hierarquia[macro]['processos'][processo]['subprocessos'][subprocesso] = {'atividades': []}

            hierarquia[macro]['processos'][processo]['subprocessos'][subprocesso]['atividades'].append(atividade)

        logger.info(f"[ATIVIDADES] CSV carregado: {len(lista_plana)} atividades em hierarquia")

        return {
            'macroprocessos': hierarquia,
            'flat_list': lista_plana
        }

    except Exception as e:
        logger.error(f"❌ Erro ao carregar CSV de arquitetura: {e}")
        return {'macroprocessos': {}, 'flat_list': []}
