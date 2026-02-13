"""
Carregamento de Operadores

Responsabilidade única: carregar operadores do CSV com fallback hardcoded.
"""

import logging
import os
from typing import List

import pandas as pd

logger = logging.getLogger(__name__)


def carregar_operadores() -> List[str]:
    """
    Carrega operadores do CSV com fallback hardcoded.

    Permite escalabilidade: mesmo código serve para DECIPEX, MGI, outros órgãos.
    Basta trocar o CSV ou usar variável de ambiente.

    Returns:
        List[str]: Lista de operadores disponíveis
    """
    csv_path = os.environ.get(
        'OPERADORES_CSV_PATH',
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'documentos_base',
            'operadores.csv'
        )
    )

    try:
        df = pd.read_csv(csv_path)

        # Filtrar apenas operadores ativos
        df_ativos = df[df['ativo'] == True].sort_values('ordem')

        # Converter para lista no formato esperado
        operadores_list = df_ativos['nome'].tolist()

        logger.info(f"[OPERADORES] Carregados do CSV: {len(operadores_list)} operadores ativos")
        return operadores_list

    except Exception as e:
        logger.warning(f"⚠️ Erro ao carregar CSV de operadores ({e}). Usando fallback hardcoded.")

        # FALLBACK: Dados hardcoded (segurança)
        return [
            "Analista",
            "Coordenador-Geral",
            "Coordenador",
            "Apoio-gabinete",
            "Equipe técnica",
            "Outros (especificar)"
        ]
