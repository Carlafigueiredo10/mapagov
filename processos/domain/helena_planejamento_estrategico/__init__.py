"""
Helena Planejamento Estratégico - Módulo Refatorado

Estrutura modular para criação de planejamentos estratégicos
com suporte a 7 metodologias diferentes.

Exports principais:
- HelenaPlanejamentoEstrategico: Orquestrador principal
- EstadoPlanejamento: Enum de estados da máquina
- MODELOS_ESTRATEGICOS: Configuração dos modelos
- PERGUNTAS_DIAGNOSTICO: Perguntas do diagnóstico guiado
"""

# Imports principais
from .pe_orchestrator import HelenaPlanejamentoEstrategico
from .schemas import EstadoPlanejamento, MODELOS_ESTRATEGICOS, PERGUNTAS_DIAGNOSTICO

__version__ = "2.0.0-refactored"
__all__ = [
    'HelenaPlanejamentoEstrategico',
    'EstadoPlanejamento',
    'MODELOS_ESTRATEGICOS',
    'PERGUNTAS_DIAGNOSTICO',
]
