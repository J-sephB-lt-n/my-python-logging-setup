"""A module containing useful functions"""

import logging

import src.log_setup

logger = logging.getLogger(__name__)
src.log_setup.default_logger_setup(logger)

logger.info("imported src/a_useful_module.py")
