"""
Enums para Analise de Riscos (Domain Layer)

Re-exporta do modulo neutro processos/analise_riscos_enums.py
para manter compatibilidade com codigo existente no domain.

Arquitetura:
- processos/analise_riscos_enums.py (fonte de verdade, sem dependencias)
- domain/.../enums.py (este arquivo, re-exporta)
- models usa processos/analise_riscos_enums.py diretamente
"""

# Re-export de todos os enums do modulo neutro
from processos.analise_riscos_enums import (
    StatusAnalise,
    ModoEntrada,
    TipoOrigem,
    EstrategiaResposta,
    NivelRisco,
    GrauConfianca,
    CategoriaRisco,
)

# Expoe tudo para imports existentes
__all__ = [
    "StatusAnalise",
    "ModoEntrada",
    "TipoOrigem",
    "EstrategiaResposta",
    "NivelRisco",
    "GrauConfianca",
    "CategoriaRisco",
]
