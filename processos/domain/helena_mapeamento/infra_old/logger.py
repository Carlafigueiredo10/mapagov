"""
Sistema de logging centralizado - substitui prints dispersos
"""
import logging
import sys


def get_logger(name: str = "helena") -> logging.Logger:
    """
    Retorna logger configurado com níveis e formatação padronizados

    Args:
        name: Nome do logger (ex: "helena.pop", "helena.state_machine")

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)

    # Evitar configuração duplicada
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)  # Captura tudo, handler filtra

    # Handler para console
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)  # Produção: INFO+, Dev: DEBUG

    # Formato: [INFO] helena.pop - Mensagem
    formatter = logging.Formatter(
        fmt="[%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
