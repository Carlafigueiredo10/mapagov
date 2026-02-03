"""
Calculos da Matriz de Risco 5x5

Este modulo fica em processos/ (camada de infra/models) e NAO depende de domain.
Contem apenas logica de calculo necessaria para os models.

Usado por:
- models_analise_riscos.py (calculo de score/nivel no save)
- domain/helena_analise_riscos/matriz.py (re-exporta)
"""

# Ranges para nivel de risco (score = prob * impacto)
RANGES_NIVEL = {
    "BAIXO": (1, 5),
    "MEDIO": (6, 10),
    "ALTO": (11, 19),
    "CRITICO": (20, 25),
}


def calcular_score(probabilidade: int, impacto: int) -> int:
    """
    Calcula score de risco.

    Args:
        probabilidade: 1-5
        impacto: 1-5

    Returns:
        Score entre 1-25
    """
    if not (1 <= probabilidade <= 5):
        raise ValueError("Probabilidade deve ser entre 1 e 5")
    if not (1 <= impacto <= 5):
        raise ValueError("Impacto deve ser entre 1 e 5")
    return probabilidade * impacto


def calcular_nivel(score: int) -> str:
    """
    Retorna nivel de risco baseado no score.

    Args:
        score: 1-25

    Returns:
        BAIXO, MEDIO, ALTO ou CRITICO
    """
    for nivel, (min_val, max_val) in RANGES_NIVEL.items():
        if min_val <= score <= max_val:
            return nivel
    return "BAIXO"
