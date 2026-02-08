"""
Módulo de Loaders - Carregamento de dados de CSVs

Responsabilidades:
- Carregar áreas organizacionais
- Carregar sistemas
- Carregar operadores
- Carregar órgãos centralizados
- Carregar canais de atendimento
- Carregar arquitetura DECIPEX
- Carregar tipos de documentos (requeridos e gerados)
"""

from .areas_loader import carregar_areas_organizacionais, carregar_descricoes_areas
from .sistemas_loader import carregar_sistemas
from .operadores_loader import carregar_operadores
from .orgaos_canais_loader import carregar_orgaos_centralizados, carregar_canais_atendimento
from .arquitetura_loader import ArquiteturaDecipex, carregar_arquitetura_csv
from .documentos_loader import carregar_tipos_documentos_requeridos, carregar_tipos_documentos_gerados

__all__ = [
    'carregar_areas_organizacionais',
    'carregar_descricoes_areas',
    'carregar_sistemas',
    'carregar_operadores',
    'carregar_orgaos_centralizados',
    'carregar_canais_atendimento',
    'ArquiteturaDecipex',
    'carregar_arquitetura_csv',
    'carregar_tipos_documentos_requeridos',
    'carregar_tipos_documentos_gerados',
]
