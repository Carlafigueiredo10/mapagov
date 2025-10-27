"""
Infrastructure layer - Logging, parsers, repositórios
"""
from .logger import get_logger
from .parsers import parse_documentos, parse_fluxos, normalizar_texto

__all__ = ['get_logger', 'parse_documentos', 'parse_fluxos', 'normalizar_texto']
