"""
Carregamento de Órgãos Centralizados e Canais de Atendimento

Responsabilidade única: carregar órgãos e canais dos CSVs com fallback hardcoded.
"""

import logging
import os
from typing import Dict, List

import pandas as pd

logger = logging.getLogger(__name__)


def carregar_orgaos_centralizados() -> List[Dict[str, str]]:
    """
    Carrega órgãos centralizados do CSV com fallback hardcoded.

    Returns:
        List[Dict]: Lista de dicionários com sigla, nome_completo, observacao
    """
    csv_path = os.environ.get(
        'ORGAOS_CENTRALIZADOS_CSV_PATH',
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'documentos_base',
            'orgaos_centralizados.csv'
        )
    )

    try:
        df = pd.read_csv(csv_path, encoding='utf-8')

        # Filtrar apenas órgãos ativos
        if 'ativo' in df.columns:
            df_ativos = df[df['ativo'] == True]
        else:
            df_ativos = df

        # Converter para lista de dicionários
        orgaos_list = []
        for _, row in df_ativos.iterrows():
            orgaos_list.append({
                'sigla': row['sigla'],
                'nome_completo': row['nome_completo'],
                'observacao': row.get('observacao', '')
            })

        logger.info(f"[ORGAOS] Centralizados carregados do CSV: {len(orgaos_list)} órgãos ativos")
        return orgaos_list

    except Exception as e:
        logger.warning(f"⚠️ Erro ao carregar CSV de órgãos centralizados ({e}). Usando fallback hardcoded.")

        # FALLBACK: Dados hardcoded (segurança)
        return [
            {'sigla': 'MGI', 'nome_completo': 'Ministério da Gestão e da Inovação em Serviços Públicos', 'observacao': ''},
            {'sigla': 'MF', 'nome_completo': 'Ministério da Fazenda', 'observacao': ''},
            {'sigla': 'MPO', 'nome_completo': 'Ministério do Planejamento e Orçamento', 'observacao': ''},
            {'sigla': 'INSS', 'nome_completo': 'Instituto Nacional do Seguro Social', 'observacao': 'Médicos peritos'},
            {'sigla': 'RFB', 'nome_completo': 'Receita Federal do Brasil', 'observacao': ''},
        ]


def carregar_canais_atendimento() -> List[Dict[str, str]]:
    """
    Carrega canais de atendimento do CSV com fallback hardcoded.

    Returns:
        List[Dict]: Lista de dicionários com codigo, nome, descricao
    """
    csv_path = os.environ.get(
        'CANAIS_ATENDIMENTO_CSV_PATH',
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'documentos_base',
            'canais_atendimento.csv'
        )
    )

    try:
        df = pd.read_csv(csv_path, encoding='utf-8')

        # Filtrar apenas canais ativos
        if 'ativo' in df.columns:
            df_ativos = df[df['ativo'] == True]
        else:
            df_ativos = df

        # Converter para lista de dicionários
        canais_list = []
        for _, row in df_ativos.iterrows():
            canais_list.append({
                'codigo': row['codigo'],
                'nome': row['nome'],
                'descricao': row.get('descricao', '')
            })

        logger.info(f"[CANAIS] Atendimento carregados do CSV: {len(canais_list)} canais ativos")
        return canais_list

    except Exception as e:
        logger.warning(f"⚠️ Erro ao carregar CSV de canais de atendimento ({e}). Usando fallback hardcoded.")

        # FALLBACK: Dados hardcoded (segurança)
        return [
            {'codigo': 'SOUGOV', 'nome': 'SouGov.br', 'descricao': 'Portal de serviços do governo federal'},
            {'codigo': 'CENTRAL_TEL', 'nome': 'Central de Atendimento Telefônico', 'descricao': 'Atendimento por telefone (call center)'},
            {'codigo': 'ATEND_PRES', 'nome': 'Atendimento Presencial', 'descricao': 'Atendimento em balcão/guichê'},
            {'codigo': 'PROTOCOLO_DIG', 'nome': 'Protocolo Digital', 'descricao': 'Sistema de protocolo eletrônico'},
            {'codigo': 'ENT_REPRES', 'nome': 'Entidade Representativa', 'descricao': 'Sindicatos e associações de classe'},
            {'codigo': 'EMAIL', 'nome': 'E-mail', 'descricao': 'Atendimento por correio eletrônico'},
        ]
