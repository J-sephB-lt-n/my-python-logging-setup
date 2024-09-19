"""The entrypoint script for the daily ELT process"""

import logging
import sys

from src.extract import extract_data, get_standard_period_dates
from src.log import (
    code_section_timer,
    create_default_logger,
)

logger = create_default_logger(__name__)
# automatically log all errors raised outside of a try/except except block
sys.excepthook = lambda err_type, err_value, err_traceback: logger.error(
    "Uncaught exception", exc_info=(err_type, err_value, err_traceback)
)
code_section_timer.set_logger(logger)

try:
    code_section_timer.section("Daily ELT process").start()

    code_section_timer.section("Extract").start()
    period_start_incl, period_end_excl = get_standard_period_dates()
    for data_source_name in ("pos_system", "mobile_events", "web_events"):
        extract_data(data_source_name, period_start_incl, period_end_excl)
    code_section_timer.section("Extract").end()

    code_section_timer.section("Daily ELT process").end()

except:
    code_section_timer.section("FAILED to complete daily ELT process").end(
        logging.ERROR
    )
    logger.exception("Error in daily ELT process")
    raise
