"""
Domain layer - Modelos de negócio puros (sem dependências externas)
"""
from .enums import EstadoConversacao, RespostaSN, EstadoEtapa, TipoInterface
from .models import Subetapa, Cenario, Etapa

__all__ = [
    'EstadoConversacao',
    'RespostaSN',
    'EstadoEtapa',
    'TipoInterface',
    'Subetapa',
    'Cenario',
    'Etapa',
]
