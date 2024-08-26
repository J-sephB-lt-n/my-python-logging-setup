"""The entrypoint script for the project"""

import datetime
import logging

from src.extract import extract_data
import src.log
from src.log import (
    change_logger_format,
    code_section_timer,
    create_default_logger,
)

logger = create_default_logger(__name__)
code_section_timer.set_logger(logger)

try:
    code_section_timer.section("Daily ELT process").start()

    period_start_incl: datetime.datetime = (
        datetime.datetime.now(tz=datetime.UTC) - datetime.timedelta(days=1)
    ).replace(hour=0, minute=0, second=0, microsecond=0)
    period_end_excl: datetime.datetime = period_start_incl + datetime.timedelta(days=1)

    code_section_timer.section("Extract").start()
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
