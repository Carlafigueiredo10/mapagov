"""
PATCH: Corrigir encoding UTF-8 no Windows
=========================================

Este módulo DEVE ser importado no __init__.py ou settings.py do Django
ANTES de qualquer logger ser criado.

Aplica automaticamente um filtro que remove caracteres não-ASCII dos logs
quando executando em Windows (evita UnicodeEncodeError com CP1252).
"""

import logging
import sys
import re


class SafeUTF8Filter(logging.Filter):
    """
    Remove caracteres não-ASCII dos logs no console Windows.

    Isso evita erros como:
    UnicodeEncodeError: 'charmap' codec can't encode character '\u2265'

    Caracteres filtrados: emojis (🚀✅❌), símbolos matemáticos (≥≤), etc.
    """
    def filter(self, record):
        try:
            # Remove tudo que não seja ASCII puro (0x00-0x7F)
            if hasattr(record, 'msg'):
                record.msg = re.sub(r'[^\x00-\x7F]+', '', str(record.msg))
            if hasattr(record, 'args') and record.args:
                # Também filtrar os argumentos (caso formatação use %)
                record.args = tuple(
                    re.sub(r'[^\x00-\x7F]+', '', str(arg)) if isinstance(arg, str) else arg
                    for arg in record.args
                )
        except Exception:
            # Fallback de segurança (nunca quebra logging)
            if hasattr(record, 'msg'):
                record.msg = str(record.msg).encode('ascii', 'ignore').decode('ascii')
        return True


def apply_windows_logging_patch():
    """
    Aplica o patch de encoding em todos os loggers do sistema.

    IMPORTANTE: Chamar essa função no início da aplicação Django,
    antes de qualquer log ser emitido.
    """
    if not sys.platform.startswith('win'):
        return  # Patch só é necessário no Windows

    utf8_filter = SafeUTF8Filter()

    # 1. Adicionar filtro no root logger
    root_logger = logging.getLogger()
    root_logger.addFilter(utf8_filter)

    # 2. Adicionar filtro em todos os handlers existentes
    for handler in root_logger.handlers:
        handler.addFilter(utf8_filter)

    # 3. Configurar logging basicConfig para aplicar automaticamente
    #    em novos handlers criados posteriormente
    logging.basicConfig(level=logging.INFO, force=True)
    for handler in logging.getLogger().handlers:
        handler.addFilter(utf8_filter)

    print("[LOGGING] SafeUTF8Filter ativo — caracteres não-ASCII serão filtrados no console Windows")
    print("[LOGGING] Caracteres afetados: emojis, símbolos matemáticos (≥, ≤, etc.)")


# Aplicar automaticamente ao importar o módulo
apply_windows_logging_patch()
