"""
Normalizador canonico de Etapa.

Funcao pura: recebe dict de etapa (qualquer versao) e retorna dict normalizado.

Regras:
- Gera `id` (UUID4) se nao existir
- Gera `ordem` a partir de fallback se nao existir
- Rename: descricao -> acao_principal (mantendo alias)
- Rename: detalhes -> verificacoes (mantendo alias)
- Rename: operador -> operador_nome
- Garante listas sao listas (nunca None/string)
- Forward-compatible: nao dropa campos desconhecidos
- Seta schema_version = 1
- Schema guard: se schema_version > 1, preserva sem normalizar (evita regressao)
- Unicidade de id: normalizar_etapas() detecta duplicatas e regenera UUID

Usado em:
- helena_pop._processar_etapa_form()
- helena_pop (legacy append, merge condicional, finalizar)
- pop_adapter.preparar_pop_para_pdf()
- views.autosave_pop()
"""

import logging
import uuid
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Versao maxima que este normalizador sabe tratar
_MAX_SCHEMA_VERSION = 1


def normalizar_etapa(etapa: Dict[str, Any], ordem_fallback: int = 1) -> Dict[str, Any]:
    """
    Normaliza um dict de etapa para o schema canonico.

    Args:
        etapa: dict de etapa (qualquer versao/origem)
        ordem_fallback: posicao default se 'ordem' nao existir

    Returns:
        dict normalizado (mutado in-place + retornado)
    """
    if not isinstance(etapa, dict):
        return {
            'id': str(uuid.uuid4()),
            'ordem': ordem_fallback,
            'numero': str(ordem_fallback),
            'acao_principal': str(etapa),
            'descricao': str(etapa),
            'operador_nome': '',
            'sistemas': [],
            'docs_requeridos': [],
            'docs_gerados': [],
            'verificacoes': [],
            'detalhes': [],
            'schema_version': 1,
        }

    # --- Schema guard: versao futura — preservar, nao normalizar ---
    sv = etapa.get('schema_version')
    if isinstance(sv, (int, float)) and sv > _MAX_SCHEMA_VERSION:
        logger.warning(
            "[normalizar_etapa] schema_version=%s > %s — preservando sem normalizar (id=%s)",
            sv, _MAX_SCHEMA_VERSION, etapa.get('id', '?')
        )
        # Garantir apenas id e ordem existem (minimo para o pipeline funcionar)
        if not etapa.get('id'):
            etapa['id'] = str(uuid.uuid4())
        if etapa.get('ordem') is None:
            etapa['ordem'] = ordem_fallback
        return etapa

    # --- ID estavel (UUID) ---
    if not etapa.get('id'):
        etapa['id'] = str(uuid.uuid4())

    # --- Ordem explicita ---
    if etapa.get('ordem') is None:
        etapa['ordem'] = ordem_fallback

    # --- Numero (display) ---
    if not etapa.get('numero'):
        etapa['numero'] = str(etapa['ordem'])

    # --- RENAME: descricao -> acao_principal ---
    if not etapa.get('acao_principal'):
        etapa['acao_principal'] = etapa.get('descricao', '[Sem descricao]')
    # Manter alias para retrocompat
    etapa['descricao'] = etapa.get('descricao') or etapa.get('acao_principal', '')

    # --- RENAME: detalhes -> verificacoes ---
    if not etapa.get('verificacoes'):
        etapa['verificacoes'] = etapa.get('detalhes', [])
    # Manter alias para retrocompat
    etapa['detalhes'] = etapa.get('detalhes') or etapa.get('verificacoes', [])

    # --- RENAME: operador -> operador_nome ---
    if not etapa.get('operador_nome'):
        etapa['operador_nome'] = etapa.get('operador', '')
    if etapa['operador_nome'] is None:
        etapa['operador_nome'] = ''

    # --- Garantir listas sao listas ---
    for campo_lista in ('sistemas', 'docs_requeridos', 'docs_gerados', 'verificacoes', 'detalhes'):
        val = etapa.get(campo_lista)
        if val is None:
            etapa[campo_lista] = []
        elif isinstance(val, str):
            etapa[campo_lista] = [v.strip() for v in val.split(',') if v.strip()] if val.strip() else []

    # --- Defaults para strings ---
    if etapa.get('tempo_estimado') is None:
        etapa['tempo_estimado'] = ''
    if etapa.get('acao_principal') is None:
        etapa['acao_principal'] = '[Sem descricao]'

    # --- Condicionais: defaults defensivos ---
    if etapa.get('tipo') == 'condicional':
        etapa.setdefault('tipo_condicional', 'binario')
        etapa.setdefault('antes_decisao', {'numero': '', 'descricao': ''})
        if not isinstance(etapa['antes_decisao'], dict):
            etapa['antes_decisao'] = {'numero': '', 'descricao': str(etapa['antes_decisao'])}
        etapa.setdefault('cenarios', [])
        for cenario in etapa.get('cenarios', []):
            if isinstance(cenario, dict):
                cenario.setdefault('numero', '')
                cenario.setdefault('descricao', '')
                cenario.setdefault('subetapas', [])
                for sub in cenario.get('subetapas', []):
                    if isinstance(sub, dict):
                        sub.setdefault('numero', '')
                        sub.setdefault('descricao', '')

    # --- Schema version ---
    etapa['schema_version'] = 1

    return etapa


def normalizar_etapas(etapas: Any) -> list:
    """
    Normaliza uma lista de etapas. Aceita None, lista, ou valor invalido.
    Garante unicidade de id — duplicatas recebem novo UUID.

    Returns:
        list de dicts normalizados
    """
    if not isinstance(etapas, list):
        return []

    resultado = []
    ids_vistos: set = set()

    for i, e in enumerate(etapas, 1):
        etapa = normalizar_etapa(e, i)
        etapa_id = etapa.get('id')

        if etapa_id in ids_vistos:
            novo_id = str(uuid.uuid4())
            logger.warning(
                "[normalizar_etapas] id duplicado detectado: %s (etapa #%d) — regenerando para %s",
                etapa_id, i, novo_id
            )
            etapa['id'] = novo_id
            etapa_id = novo_id

        ids_vistos.add(etapa_id)
        resultado.append(etapa)

    return resultado
