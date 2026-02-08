"""
Carregamento de Tipos de Documentos

Responsabilidade única: carregar tipos de documentos dos CSVs com fallback hardcoded.
Dois CSVs separados: requeridos (recebidos/analisados) e gerados (produzidos).
"""

import logging
import os
from typing import Dict, List

import pandas as pd

logger = logging.getLogger(__name__)

_BASE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    'documentos_base',
)


def _carregar_csv_documentos(csv_filename: str, fallback: List[Dict]) -> List[Dict]:
    """Carrega um CSV de tipos de documentos com fallback."""
    csv_path = os.path.join(_BASE_DIR, csv_filename)

    try:
        df = pd.read_csv(csv_path)
        df_ativos = df[df['ativo'] == True].sort_values('ordem')

        tipos = []
        for _, row in df_ativos.iterrows():
            tipos.append({
                'tipo': row['tipo'],
                'descricao': row.get('descricao', ''),
                'hint_detalhamento': row.get('hint_detalhamento', ''),
            })

        logger.info(f"[DOCUMENTOS] Carregados de {csv_filename}: {len(tipos)} tipos ativos")
        return tipos

    except Exception as e:
        logger.warning(f"Erro ao carregar {csv_filename} ({e}). Usando fallback.")
        return fallback


def carregar_tipos_documentos_requeridos() -> List[Dict]:
    """
    Carrega tipos de documentos requeridos/recebidos do CSV.

    Returns:
        List[Dict]: Lista de {tipo, descricao, hint_detalhamento}
    """
    return _carregar_csv_documentos(
        'tipos_documentos_requeridos.csv',
        fallback=[
            {'tipo': 'Requerimento', 'descricao': 'Solicitacao formal do interessado', 'hint_detalhamento': ''},
            {'tipo': 'Processo SEI', 'descricao': 'Processo administrativo eletronico no SEI', 'hint_detalhamento': ''},
            {'tipo': 'Documentos pessoais', 'descricao': 'CPF, RG, certidoes', 'hint_detalhamento': ''},
            {'tipo': 'Declaracao', 'descricao': 'Declaracao emitida por pessoa, empresa ou orgao', 'hint_detalhamento': ''},
            {'tipo': 'Certidao', 'descricao': 'Documento que certifica informacao oficial', 'hint_detalhamento': ''},
            {'tipo': 'Comprovante de pagamento', 'descricao': 'Boleto, recibo, fatura', 'hint_detalhamento': ''},
            {'tipo': 'Parecer', 'descricao': 'Opiniao tecnica ou juridica', 'hint_detalhamento': ''},
            {'tipo': 'Planilha / Dados', 'descricao': 'Dados estruturados para analise', 'hint_detalhamento': ''},
            {'tipo': 'Outro', 'descricao': 'Outro tipo de documento', 'hint_detalhamento': ''},
        ]
    )


def carregar_tipos_documentos_gerados() -> List[Dict]:
    """
    Carrega tipos de documentos gerados/produzidos do CSV.

    Returns:
        List[Dict]: Lista de {tipo, descricao, hint_detalhamento}
    """
    return _carregar_csv_documentos(
        'tipos_documentos_gerados.csv',
        fallback=[
            {'tipo': 'Nota Tecnica', 'descricao': 'Documento tecnico', 'hint_detalhamento': ''},
            {'tipo': 'Despacho', 'descricao': 'Decisao ou encaminhamento formal', 'hint_detalhamento': ''},
            {'tipo': 'Oficio', 'descricao': 'Comunicacao formal', 'hint_detalhamento': ''},
            {'tipo': 'Formulario', 'descricao': 'Documento estruturado', 'hint_detalhamento': ''},
            {'tipo': 'Tela de sistema', 'descricao': 'Interface de sistema', 'hint_detalhamento': ''},
            {'tipo': 'Outro', 'descricao': 'Outro tipo de documento', 'hint_detalhamento': ''},
        ]
    )
