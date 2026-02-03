"""
Módulo de Governança - Regras de negócio para gestão de atividades

Responsabilidades:
- Geração de CAP (Código na Arquitetura de Processos)
- Detecção de duplicatas via TF-IDF
- Persistência de atividades sugeridas
- Versionamento do CSV de arquitetura
"""

from .cap_generator import gerar_cap_provisorio_seguro
from .duplicatas import detectar_atividades_similares
from .atividade_sugerida import salvar_atividade_sugerida
from .versionamento_csv import criar_versao_csv, atualizar_changelog, injetar_atividade_no_csv

__all__ = [
    'gerar_cap_provisorio_seguro',
    'detectar_atividades_similares',
    'salvar_atividade_sugerida',
    'criar_versao_csv',
    'atualizar_changelog',
    'injetar_atividade_no_csv',
]
