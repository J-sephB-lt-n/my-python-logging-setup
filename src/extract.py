"""Functions for extracting data from raw data sources"""

import datetime
import logging
import random
import time

from src.log import (
    BASE_LOGGER_FORMAT,
    change_logger_format,
    create_default_logger,
    log_function_or_method_call,
)

logger: logging.Logger = create_default_logger(__name__)
change_logger_format(
    logger,
    BASE_LOGGER_FORMAT.replace("%(message)s", "[extract] %(message)s"),
)


@log_function_or_method_call(logger, log_outputs=True)
def extract_from_pos_system(
    start_datetime: datetime.datetime, end_datetime: datetime.datetime
):
    """Extract data from POS system"""
    time.sleep(random.randint(1, 5))
    return {"status": "SUCCESS", "nrows": 6_239}


@log_function_or_method_call(logger, log_outputs=True)
def extract_mobile_events_data(
    start_datetime: datetime.datetime, end_datetime: datetime.datetime
):
    """Extract mobile events data"""
    time.sleep(random.randint(1, 5))
    return {"status": "FAILURE", "nrows": None}


@log_function_or_method_call(logger, log_outputs=True)
def extract_web_events_data(
    start_datetime: datetime.datetime, end_datetime: datetime.datetime
):
    """Extract web events data"""
    time.sleep(random.randint(1, 5))
    return {"status": "SUCCESS", "nrows": 867_111}


@log_function_or_method_call(logger, log_inputs=True, log_outputs=True)
def extract_data(
    source_name: str, start_datetime: datetime.datetime, end_datetime: datetime.datetime
):
    match source_name:
        case "pos_system":
            extract_from_pos_system(start_datetime, end_datetime)
        case "mobile_events":
            extract_mobile_events_data(start_datetime, end_datetime)
        case "web_events":
            extract_web_events_data(start_datetime, end_datetime)
        case _:
            raise ValueError(f"Unknown source_name: {source_name}")
