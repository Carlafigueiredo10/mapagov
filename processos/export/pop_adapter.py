"""
Adapter: converte dados do POP (frontend/SM) no formato esperado pelo PDFGenerator.

O PDFGenerator (utils.py) nao e alterado — este modulo apenas normaliza o INPUT.

Fluxo:
  dados_pop (frontend) -> preparar_pop_para_pdf() -> PDFGenerator.gerar_pop_completo()
"""
import logging
from datetime import datetime
from typing import Any, Dict, List

from processos.utils import FormatadorUtils, preparar_dados_para_pdf

logger = logging.getLogger(__name__)


def preparar_pop_para_pdf(dados_pop: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza dados do POP para o formato EXATO esperado por gerar_pop_completo().

    1. Chama preparar_dados_para_pdf() existente (sanitiza strings, etapas ricas)
    2. Pos-processa campos que mudaram de schema (documentos, fluxos, etc.)
    3. Garante defaults seguros em todos os campos

    Args:
        dados_pop: dict vindo do frontend (DadosPOP) ou de _preparar_dados_formulario()

    Returns:
        dict pronto para PDFGenerator.gerar_pop_completo()
    """
    # Passo 0: pre-normalizar etapas para evitar None em campos string
    # (preparar_dados_para_pdf chama limpar_texto_sistema que nao aceita None)
    if 'etapas' in dados_pop and isinstance(dados_pop.get('etapas'), list):
        dados_pop = dict(dados_pop)  # shallow copy para nao mutar original
        dados_pop['etapas'] = [_normalizar_etapa(e, i) for i, e in enumerate(dados_pop['etapas'], 1)]

    # Passo 1: sanitizacao base (etapas, operadores, sistemas, area, etc.)
    dados = preparar_dados_para_pdf(dados_pop)

    # Passo 2: campos que preparar_dados_para_pdf nao processa

    # --- codigo_cap / codigo_processo ---
    if not dados.get('codigo_processo') or dados['codigo_processo'] == 'X.X.X.X':
        dados['codigo_processo'] = dados_pop.get('codigo_cap', '') or dados_pop.get('codigo_processo', 'X.X.X.X')

    # --- fluxos_entrada / fluxos_saida ---
    dados['fluxos_entrada'] = _normalizar_lista_strings(dados_pop.get('fluxos_entrada', []))
    dados['fluxos_saida'] = _normalizar_lista_strings(dados_pop.get('fluxos_saida', []))

    # --- documentos_utilizados (novo schema: lista de objetos -> tabela no renderer) ---
    # Passa a lista crua para o renderer montar a tabela.
    # Fallback: se já é string (legado), o renderer trata.
    docs_raw = dados_pop.get('documentos_utilizados', dados.get('documentos_utilizados', []))
    if isinstance(docs_raw, list):
        dados['documentos_utilizados'] = docs_raw
    else:
        dados['documentos_utilizados'] = _formatar_documentos_para_pdf(docs_raw)

    # --- nome_usuario ---
    if not dados.get('nome_usuario') or dados['nome_usuario'] == '[Usuario]':
        dados['nome_usuario'] = dados_pop.get('nome_usuario', '[Usuario]')

    # --- versao, mes_ano, data_aprovacao ---
    if not dados.get('versao'):
        dados['versao'] = '1.0'
    agora = datetime.now()
    dados.setdefault('mes_ano', agora.strftime('%m/%Y'))
    dados.setdefault('data_aprovacao', agora.strftime('%d/%m/%Y'))
    dados.setdefault('data_criacao', agora.strftime('%d/%m/%Y'))

    # --- etapas: defaults defensivos + ordenacao deterministica ---
    if 'etapas' in dados and isinstance(dados['etapas'], list):
        dados['etapas'] = [_normalizar_etapa(e, i) for i, e in enumerate(dados['etapas'], 1)]
        dados['etapas'] = sorted(dados['etapas'], key=lambda e: _sort_key_etapa(e))

    # --- garantir que nenhuma string e None ---
    for chave in ('nome_processo', 'entrega_esperada', 'pontos_atencao',
                  'codigo_processo', 'nome_usuario', 'macroprocesso',
                  'processo_especifico', 'subprocesso'):
        if dados.get(chave) is None:
            dados[chave] = ''

    # --- area: garantir que e dict (renderer espera .get('nome')) ---
    area_raw = dados.get('area')
    if area_raw is None:
        dados['area'] = {}
    elif isinstance(area_raw, str):
        dados['area'] = {'nome': area_raw}

    logger.info(f"[pop_adapter] POP normalizado: {len(dados.get('etapas', []))} etapas, "
                f"{len(dados.get('fluxos_entrada', []))} entradas, "
                f"docs_utilizados={'(formatado)' if dados.get('documentos_utilizados') else '(vazio)'}")

    return dados


def _normalizar_lista_strings(valor: Any) -> List[str]:
    """Garante que o valor e uma lista de strings."""
    if isinstance(valor, list):
        return [FormatadorUtils.limpar_texto_sistema(str(v)) for v in valor if v]
    if isinstance(valor, str) and valor.strip():
        return [FormatadorUtils.limpar_texto_sistema(v.strip()) for v in valor.split(';') if v.strip()]
    return []


def _formatar_documentos_para_pdf(docs: Any) -> str:
    """
    Converte documentos_utilizados do novo schema (lista de objetos)
    para texto formatado que _gerar_secao_conteudo() renderiza como string.

    Input (novo):  [{tipo_documento: "Nota Tecnica", descricao: "assunto", tipo_uso: "Gerado"}, ...]
    Input (legado): "Requerimento, CPF, Contrato" (string)
    Input (vazio):  [] ou None

    Output: texto formatado com bullets
    """
    if not docs:
        return '[Nao informado]'

    # Legado: ja e string
    if isinstance(docs, str):
        return docs if docs.strip() else '[Nao informado]'

    # Novo schema: lista de objetos
    if isinstance(docs, list):
        linhas = []
        for doc in docs:
            if isinstance(doc, dict):
                tipo = doc.get('tipo_documento', 'Documento')
                descricao = doc.get('descricao', '')
                uso = doc.get('tipo_uso', '')
                linha = tipo
                if descricao:
                    linha += f": {descricao}"
                if uso:
                    linha += f" ({uso})"
                linhas.append(linha)
            elif isinstance(doc, str) and doc.strip():
                linhas.append(doc.strip())

        if not linhas:
            return '[Nao informado]'

        return '\n'.join(f"- {linha}" for linha in linhas)

    return '[Nao informado]'


def _sort_key_etapa(etapa: Dict[str, Any]) -> float:
    """Chave de ordenacao para etapas. Converte numero para float, fallback 10^9."""
    try:
        return float(etapa.get('numero', 10**9))
    except (ValueError, TypeError):
        return 10**9


def _normalizar_etapa(etapa: Dict[str, Any], numero_fallback: int) -> Dict[str, Any]:
    """
    Garante defaults defensivos em uma etapa para evitar crashes no PDF.
    Nao altera a estrutura — apenas garante que campos existem.
    """
    if not isinstance(etapa, dict):
        return {'numero': numero_fallback, 'descricao': str(etapa)}

    # Defaults para campos string (setdefault + None -> fallback)
    for campo, default in [('numero', numero_fallback), ('descricao', '[Sem descricao]'),
                           ('operador_nome', ''), ('tempo_estimado', '')]:
        if etapa.get(campo) is None:
            etapa[campo] = default

    # Garantir que listas sao listas (nunca string ou None)
    for campo_lista in ('sistemas', 'docs_requeridos', 'docs_gerados', 'detalhes'):
        val = etapa.get(campo_lista)
        if val is None:
            etapa[campo_lista] = []
        elif isinstance(val, str):
            etapa[campo_lista] = [v.strip() for v in val.split(',') if v.strip()] if val.strip() else []

    if etapa.get('tipo') == 'condicional':
        etapa.setdefault('tipo_condicional', 'binario')
        etapa.setdefault('pergunta_decisao', 'Condicao de decisao')
        etapa.setdefault('antes_decisao', {'numero': '', 'descricao': ''})
        # Garantir antes_decisao e dict
        if not isinstance(etapa['antes_decisao'], dict):
            etapa['antes_decisao'] = {'numero': '', 'descricao': str(etapa['antes_decisao'])}
        etapa.setdefault('cenarios', [])
        # Garantir subetapas em cada cenario
        for cenario in etapa.get('cenarios', []):
            if isinstance(cenario, dict):
                cenario.setdefault('numero', '')
                cenario.setdefault('descricao', '')
                cenario.setdefault('subetapas', [])
                for sub in cenario.get('subetapas', []):
                    if isinstance(sub, dict):
                        sub.setdefault('numero', '')
                        sub.setdefault('descricao', '')
    else:
        etapa.setdefault('detalhes', [])

    return etapa
