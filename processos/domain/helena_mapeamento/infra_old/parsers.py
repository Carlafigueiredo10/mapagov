"""
Parsers e validadores de entrada - normalização de JSON/texto
"""
import json
import unicodedata
from typing import List, Dict, Any


def normalizar_texto(texto: str) -> str:
    """
    Normaliza texto removendo acentos, convertendo para lowercase

    Args:
        texto: String a normalizar

    Returns:
        String normalizada (sem acentos, lowercase, stripped)
    """
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto.lower().strip())
        if unicodedata.category(c) != 'Mn'
    )


def parse_documentos(mensagem: str) -> List[Dict[str, Any]]:
    """
    Parseia lista de documentos (JSON estruturado ou texto livre)

    Formato esperado (JSON):
    [
        {
            "tipo_documento": "Formulário",
            "tipo_uso": "Gerado",
            "obrigatorio": true,
            "descricao": "Requerimento de auxílio",
            "sistema": null
        },
        ...
    ]

    Fallback (texto livre):
    "Requerimento de auxílio"

    Args:
        mensagem: String contendo JSON ou texto livre

    Returns:
        Lista de dicionários representando documentos
    """
    mensagem = mensagem.strip()

    # Tentar parsear como JSON estruturado
    if mensagem.startswith('['):
        try:
            documentos = json.loads(mensagem)
            if isinstance(documentos, list):
                return documentos
        except json.JSONDecodeError:
            pass

    # Fallback: texto livre simples
    return [{"descricao": mensagem}]


def parse_fluxos(mensagem: str) -> List[str]:
    """
    Parseia fluxos de entrada/saída (JSON estruturado ou texto livre)

    Formato esperado (JSON):
    {
        "destinos_selecionados": [
            {"tipo": "CGBEN", "especificacao": "Setor X"},
            {"tipo": "CGPAG", "especificacao": null}
        ],
        "outros_destinos": "Área externa não listada"
    }

    OU (fluxos de entrada):
    {
        "origens_selecionadas": [...],
        "outras_origens": "..."
    }

    Fallback (texto livre):
    "CGBEN, CGPAG"

    Args:
        mensagem: String contendo JSON ou texto livre

    Returns:
        Lista de strings representando fluxos
    """
    mensagem = mensagem.strip()

    # Tentar parsear como JSON estruturado
    try:
        data = json.loads(mensagem)
        if isinstance(data, dict):
            fluxos = []

            # Fluxos de saída
            destinos = data.get("destinos_selecionados", [])
            for destino in destinos:
                texto = destino["tipo"]
                if destino.get("especificacao"):
                    texto += f": {destino['especificacao']}"
                fluxos.append(texto)

            # Fluxos de entrada
            origens = data.get("origens_selecionadas", [])
            for origem in origens:
                texto = origem["tipo"]
                if origem.get("especificacao"):
                    texto += f": {origem['especificacao']}"
                fluxos.append(texto)

            # Outros (campo livre)
            outros = data.get("outros_destinos") or data.get("outras_origens")
            if outros:
                fluxos.append(outros)

            return fluxos
    except json.JSONDecodeError:
        pass

    # Fallback: texto livre (separado por vírgula ou linha)
    if ',' in mensagem:
        return [f.strip() for f in mensagem.split(',') if f.strip()]
    elif '\n' in mensagem:
        return [f.strip() for f in mensagem.split('\n') if f.strip()]
    else:
        return [mensagem]
