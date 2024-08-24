"""Functionality related to logging"""

import logging
from typing import Final

from src.custom_exceptions import AlreadyExistsError

BASE_LOGGER_FORMAT: Final[str] = "%(asctime)s : %(name)s : %(levelname)s : %(message)s"


def create_default_stream_logger(logger_name: str) -> logging.Logger:
    """TODO"""
    logger = logging.getLogger(logger_name)
    if logger.handlers:
        raise AlreadyExistsError(f"logger {logger_name} already exists")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(BASE_LOGGER_FORMAT))
    logger.addHandler(handler)
    return logger
