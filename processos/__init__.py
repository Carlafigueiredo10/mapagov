"""
Pacote de processos do MapaGov.

IMPORTANTE: Este módulo importa o bootstrap de logging do Windows
para reconfigurar sys.stdout com UTF-8 e evitar UnicodeEncodeError.
"""

# Importar bootstrap de logging ANTES de qualquer outra coisa
import processos.infra.logging_bootstrap  # noqa
