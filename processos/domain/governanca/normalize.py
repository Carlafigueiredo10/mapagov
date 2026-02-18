"""
Normalização de prefixos SNI (Sistema de Numeração Institucional).

Funções puras, sem dependências externas.
Usadas por loaders, pipelines, migrações, cap_generator e cp_generator.
"""


def normalize_area_prefix(prefix: str) -> str:
    """
    Normaliza prefixo de área para formato SNI (sempre 2 dígitos).

    '1'     -> '01'
    '9'     -> '09'
    '10'    -> '10'
    '01'    -> '01'
    '5.1'   -> '05.01'
    '05.01' -> '05.01'
    ' 5.1 ' -> '05.01'
    """
    s = (prefix or "").strip()
    if not s:
        return s

    if "." in s:
        parts = s.split(".", 1)
        a, b = parts[0], parts[1]
        if a.isdigit() and b.isdigit():
            return f"{int(a):02d}.{int(b):02d}"
        return s

    if s.isdigit():
        return f"{int(s):02d}"

    return s


def normalize_cap(cap: str) -> str:
    """
    Normaliza só o primeiro segmento (área) de um CAP.

    '1.02.03.04.108'  -> '01.02.03.04.108'
    '01.02.03.04.108' -> '01.02.03.04.108'
    """
    s = (cap or "").strip()
    if not s:
        return s

    parts = s.split(".")
    if len(parts) >= 2 and parts[0].isdigit():
        parts[0] = f"{int(parts[0]):02d}"

    return ".".join(parts)


def normalize_numero_csv(numero: str) -> str:
    """
    Normaliza Numero do CSV de arquitetura para formato SNI com padding.

    CSV tem: '1.1.1.1' (macro.processo.sub.atividade, sem padding)
    SNI pede: '01.01.01.001' (MM.PP.SS.III com 2+2+2+3 dígitos)

    '1.1.1.1'     -> '01.01.01.001'
    '1.1.2.8'     -> '01.01.02.008'
    '8.1.1.1'     -> '08.01.01.001'
    '01.01.01.001' -> '01.01.01.001' (já normalizado)
    """
    s = (numero or "").strip()
    if not s:
        return s

    parts = s.split(".")
    if len(parts) != 4:
        return s

    try:
        mm = int(parts[0])
        pp = int(parts[1])
        ss = int(parts[2])
        iii = int(parts[3])
        return f"{mm:02d}.{pp:02d}.{ss:02d}.{iii:03d}"
    except ValueError:
        return s


def resolve_prefixo_cap(area_codigo: str, areas_map: dict) -> str:
    """
    Retorna o prefixo correto para compor CAP.

    Subáreas usam o prefixo da área pai (2 dígitos), não o próprio (4 dígitos).
    CAP nunca embute subárea — subárea fica em campo separado.

    'CGBEN'    -> '01' (direto)
    'DIGEP'    -> '05' (direto)
    'DIGEP-RO' -> '05' (usa área pai DIGEP, não 05.01)
    """
    prefixo = areas_map.get(area_codigo, area_codigo)

    # Se prefixo tem ponto (é subárea como 05.01), usar só a parte antes do ponto
    if "." in prefixo:
        return prefixo.split(".")[0]

    return prefixo


def resolve_prefixo_cp(area_codigo: str, areas_map: dict) -> str:
    """
    Retorna prefixo completo para compor CP (Código de Produto).

    Diferente do CAP, CP INCLUI subárea.
    Falha alto se área desconhecida (evita CP tipo "COATE.01.001").

    'CGBEN'    -> '01'    (área normal)
    'DIGEP-RO' -> '05.01' (subárea completa)
    'XPTO'     -> ValueError (área desconhecida)
    """
    prefixo = areas_map.get(area_codigo)
    if not prefixo:
        raise ValueError(f"area_codigo desconhecida para CP: {area_codigo}")
    return normalize_area_prefix(prefixo)
