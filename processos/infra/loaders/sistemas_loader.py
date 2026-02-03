"""
Carregamento de Sistemas

Responsabilidade única: carregar sistemas do CSV com fallback hardcoded.
"""

import logging
import os
from typing import Dict, List

import pandas as pd

logger = logging.getLogger(__name__)


def carregar_sistemas() -> Dict[str, List[str]]:
    """
    Carrega sistemas do CSV com fallback hardcoded.

    Permite escalabilidade: mesmo código serve para DECIPEX, MGI, outros órgãos.
    Basta trocar o CSV ou usar variável de ambiente.

    Returns:
        Dict[str, List[str]]: Sistemas agrupados por categoria
    """
    csv_path = os.environ.get(
        'SISTEMAS_CSV_PATH',
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'documentos_base',
            'sistemas.csv'
        )
    )

    try:
        df = pd.read_csv(csv_path)

        # Filtrar apenas sistemas ativos
        df_ativos = df[df['ativo'] == True].sort_values('ordem')

        # Agrupar por categoria
        sistemas_dict = {}
        for categoria in df_ativos['categoria'].unique():
            sistemas_da_categoria = df_ativos[df_ativos['categoria'] == categoria]['nome'].tolist()
            sistemas_dict[categoria] = sistemas_da_categoria

        logger.info(f"[SISTEMAS] Carregados do CSV: {len(df_ativos)} sistemas em {len(sistemas_dict)} categorias")
        return sistemas_dict

    except Exception as e:
        logger.warning(f"⚠️ Erro ao carregar CSV de sistemas ({e}). Usando fallback hardcoded.")

        # FALLBACK: Dados hardcoded (segurança)
        return {
            "gestao_pessoal": ["SIAPE", "E-SIAPE", "SIGEPE", "SIGEP - AFD", "E-Pessoal TCU", "SIAPNET", "SIGAC"],
            "documentos": ["SEI", "DOINET", "DOU", "SOUGOV", "PETRVS"],
            "transparencia": ["Portal da Transparência", "CNIS", "Site CGU-PAD", "Sistema de Pesquisa Integrada do TCU", "Consulta CPF RFB"],
            "previdencia": ["SISTEMA COMPREV", "BG COMPREV"],
            "comunicacao": ["TEAMS", "OUTLOOK"],
            "outros": ["DW"]
        }
