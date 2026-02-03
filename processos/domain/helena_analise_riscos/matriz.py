"""
Calculos da Matriz de Risco 5x5 (Domain Layer)

Re-exporta do modulo neutro processos/analise_riscos_matriz.py
e adiciona funcoes de UI (cores) localmente.

Arquitetura:
- processos/analise_riscos_matriz.py (fonte de verdade, logica core)
- domain/.../matriz.py (este arquivo, re-exporta + UI concerns)
"""

# Re-export do modulo neutro (logica core)
from processos.analise_riscos_matriz import (
    RANGES_NIVEL,
    calcular_score,
    calcular_nivel,
)

# UI concerns (definidos localmente, nao no modulo neutro)
CORES_NIVEL = {
    "BAIXO": "#22c55e",
    "MEDIO": "#eab308",
    "ALTO": "#f97316",
    "CRITICO": "#ef4444",
}


def get_cor_nivel(nivel: str) -> str:
    """
    Retorna cor hex para o nivel.

    Args:
        nivel: BAIXO, MEDIO, ALTO ou CRITICO

    Returns:
        Cor hexadecimal
    """
    return CORES_NIVEL.get(nivel, "#6b7280")


__all__ = [
    "RANGES_NIVEL",
    "calcular_score",
    "calcular_nivel",
    "CORES_NIVEL",
    "get_cor_nivel",
]
