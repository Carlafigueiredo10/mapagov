"""
Geração de CAP (Código na Arquitetura de Processos)

Responsabilidade única: gerar identificadores únicos com lock transacional.
"""

import logging
import pandas as pd
from django.db import transaction

from processos.models_new import ControleIndices

logger = logging.getLogger(__name__)


def _carregar_prefixos_area() -> dict:
    """Carrega prefixos do model Area (fonte de verdade). Fallback SNI se banco indisponível."""
    try:
        from processos.models import Area
        return {a.codigo: a.prefixo for a in Area.objects.filter(ativo=True)}
    except Exception:
        return {
            "CGBEN": "01", "CGPAG": "02", "COATE": "03", "CGGAF": "04",
            "DIGEP": "05", "DIGEP-RO": "05.01", "DIGEP-RR": "05.02", "DIGEP-AP": "05.03",
            "CGRIS": "06", "CGCAF": "07", "CGECO": "08",
            "COADM": "09", "COGES": "10", "CDGEP": "11",
        }


def gerar_cap_provisorio_seguro(
    area_codigo: str,
    macroprocesso: str,
    processo: str,
    subprocesso: str,
    atividade: str,
    hierarquia_df: pd.DataFrame
) -> str:
    """
    Gera CAP provisório com lock transacional para evitar race conditions.

    Formato: AA.MM.PP.SS.III (SNI)

    Exemplo: 01.02.03.04.108
    - 01 = CGBEN
    - 02 = índice do macroprocesso
    - 03 = índice do processo
    - 04 = índice do subprocesso
    - 108 = próximo índice de atividade (107 + 1)

    Args:
        area_codigo: Código da área (ex: 'CGBEN')
        macroprocesso: Nome do macroprocesso
        processo: Nome do processo
        subprocesso: Nome do subprocesso
        atividade: Nome da atividade
        hierarquia_df: DataFrame com a arquitetura completa para indexação

    Returns:
        CAP provisório único (ex: '01.02.03.04.108')
    """
    from processos.domain.governanca.normalize import resolve_prefixo_cap
    prefixos = _carregar_prefixos_area()
    prefixo_area = resolve_prefixo_cap(area_codigo, prefixos)

    # Buscar numeração diretamente do CSV (coluna 'Numero')
    try:
        filtro = (
            (hierarquia_df['Macroprocesso'] == macroprocesso) &
            (hierarquia_df['Processo'] == processo) &
            (hierarquia_df['Subprocesso'] == subprocesso) &
            (hierarquia_df['Atividade'] == atividade)
        )
        linha_encontrada = hierarquia_df[filtro]

        if not linha_encontrada.empty and 'Numero' in linha_encontrada.columns:
            # Ler número hierárquico do CSV (ex: "01.01.01.001")
            numero_csv = str(linha_encontrada.iloc[0]['Numero'])
            partes = numero_csv.split('.')

            if len(partes) >= 4:
                idx_macro = int(partes[0])
                idx_processo = int(partes[1])
                idx_subprocesso = int(partes[2])
                idx_atividade = int(partes[3])
            else:
                # Fallback: gerar dinamicamente
                raise ValueError("Formato de numeração inválido no CSV")
        else:
            # Fallback: gerar dinamicamente (nova atividade)
            raise ValueError("Atividade não encontrada no CSV")

    except (ValueError, IndexError, KeyError):
        # Fallback: gerar índices dinamicamente (para novas atividades)
        logger.warning(f"[GOVERNANÇA] Numeração não encontrada no CSV, gerando dinamicamente")

        # 1. Índice do macroprocesso
        macros_unicos = hierarquia_df['Macroprocesso'].unique().tolist()
        idx_macro = macros_unicos.index(macroprocesso) + 1 if macroprocesso in macros_unicos else len(macros_unicos) + 1

        # 2. Índice do processo dentro do macroprocesso
        processos_no_macro = hierarquia_df[hierarquia_df['Macroprocesso'] == macroprocesso]['Processo'].unique().tolist()
        idx_processo = processos_no_macro.index(processo) + 1 if processo in processos_no_macro else len(processos_no_macro) + 1

        # 3. Índice do subprocesso dentro do processo
        subs_no_processo = hierarquia_df[
            (hierarquia_df['Macroprocesso'] == macroprocesso) &
            (hierarquia_df['Processo'] == processo)
        ]['Subprocesso'].unique().tolist()
        idx_subprocesso = subs_no_processo.index(subprocesso) + 1 if subprocesso in subs_no_processo else len(subs_no_processo) + 1

        # 4. Índice da atividade - obter próximo com lock transacional
        with transaction.atomic():
            controle, created = ControleIndices.objects.select_for_update().get_or_create(
                area_codigo=area_codigo,
                defaults={'ultimo_indice': 107}
            )

            proximo_indice = controle.ultimo_indice + 1
            controle.ultimo_indice = proximo_indice
            controle.save()

            idx_atividade = proximo_indice

    # Montar CAP com zero-padding
    cap_provisorio = f"{prefixo_area}.{idx_macro:02d}.{idx_processo:02d}.{idx_subprocesso:02d}.{idx_atividade:03d}"

    logger.info(f"[GOVERNANÇA] CAP provisório gerado: {cap_provisorio} para área {area_codigo}")

    return cap_provisorio
