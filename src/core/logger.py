"""
Logger do projeto.

    from src.core.logger import get_logger
    logger = get_logger(__name__)
"""

import logging

from src.core.settings import settings

LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s | %(message)s"

_configured = False

def _configure() -> None:
    """Configura o handler raiz uma única vez, no primeiro get_logger."""
    global _configured
    if _configured:
        return

    logging.basicConfig(
        level=logging.DEBUG if settings.is_dev else logging.INFO,
        format=LOG_FORMAT,
    )
    _configured = True

def get_logger(name: str) -> logging.Logger:
    _configure()
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if settings.is_dev else logging.INFO)
    return logger

def mask_cpf(cpf: str | None) -> str:
    """CPF parcialmente oculto, para não deixar dado pessoal completo em log."""
    if not cpf:
        return "-"
    return f"{cpf[:3]}***{cpf[-2:]}" if len(cpf) >= 5 else "***"
