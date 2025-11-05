# processos/domain/helena_recepcao/__init__.py
"""
Helena Recepção - Módulo de Direcionamento e Orientação GRC
Arquitetura com orquestrador + agentes especializados
"""

from .reception_orchestrator import HelenaRecepcaoOrchestrator

__all__ = ['HelenaRecepcaoOrchestrator']
