"""
Application layer - Adaptadores e helpers de UI
"""
from .adapters import adapter_etapas_ui
from .helpers import criar_resposta_padrao, handle_edition_complete

__all__ = ['adapter_etapas_ui', 'criar_resposta_padrao', 'handle_edition_complete']
