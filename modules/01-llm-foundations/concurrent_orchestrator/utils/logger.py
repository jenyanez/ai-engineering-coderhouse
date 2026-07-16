"""
logger.py — Configuración centralizada de logging para el orquestador.

Usa formato con timestamps para evidenciar la concurrencia en los logs.
"""

import logging
import sys


def setup_logger(name: str = "orquestador", level: int = logging.INFO) -> logging.Logger:
    """
    Crea y configura un logger con formato timestamp + nombre de tarea.

    Args:
        name: Nombre del logger.
        level: Nivel de logging (default: INFO).

    Returns:
        Logger configurado.
    """
    logger = logging.getLogger(name)

    # Evitar duplicar handlers si se llama más de una vez
    if logger.handlers:
        return logger

    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Formato con timestamp de alta resolución para ver concurrencia
    formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d | %(levelname)-7s | %(message)s",
        datefmt="%H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger