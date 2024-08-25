"""Functionality related to logging"""

import functools
import json
import logging
import time
from typing import Any, Callable, Final, Optional, Self

from src.custom_exceptions import AlreadyExistsError

BASE_LOGGER_FORMAT: Final[str] = "%(asctime)s : %(name)s : %(levelname)s : %(message)s"


def create_default_stream_logger(logger_name: str) -> logging.Logger:
    """Creates a new logger with default settings"""
    logger = logging.getLogger(logger_name)
    if logger.handlers:
        raise AlreadyExistsError(f"logger {logger_name} already exists")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(BASE_LOGGER_FORMAT))
    logger.addHandler(handler)
    return logger


def change_logger_format(logger: logging.Logger, new_format: str) -> None:
    """Changes the format of the provided logger (in all of it's handlers)"""
    new_formatter = logging.Formatter(new_format)
    for handler in logger.handlers:
        handler.setFormatter(new_formatter)


def str_truncate(input_str: str, max_nchar: int) -> str:
    """Returns a truncated version of `input_str` if it is longer than `max_nchar`"""
    assert isinstance(input_str, str)
    if len(input_str) > max_nchar:
        return f"{input_str[:max_nchar]}..."
    return input_str


def dynamic_str_truncate(input_element: Any, max_nchar: int) -> str:
    """Returns a string version of `input_element`, possibly truncating it (or the
    items within it) based on its length and type"""
    match input_element:
        case list():
            return json.dumps(
                [str_truncate(str(x), max_nchar) for x in input_element], indent=4
            )
        case dict():
            return json.dumps(
                {
                    str_truncate(str(k), max_nchar): str_truncate(str(v), max_nchar)
                    for k, v in input_element.items()
                },
                indent=4,
            )
        case tuple():
            return json.dumps(
                tuple([str_truncate(str(x), max_nchar) for x in input_element]),
                indent=4,
            )
        case set():
            return (
                "set(["
                + json.dumps(
                    [str_truncate(str(x), max_nchar) for x in input_element], indent=4
                )[1:-1]
                + "])"
            )
        case _:
            return str_truncate(str(input_element), max_nchar)


def log_function_or_method_call(
    logger: logging.Logger,
    log_inputs: bool = False,
    log_outputs: bool = False,
    log_inputs_max_len: int = 50,
    log_outputs_max_len: int = 50,
):
    """A function decorator which generates a log message when the function is run"""

    def decorator_log_function_call(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper_log_function_call(*args, **kwargs):
            log_message: str = f"Called {func.__name__}("
            # other stuff here #
            log_message += ")"
            logger.info(log_message)
            return func(*args, **kwargs)

        return wrapper_log_function_call

    return decorator_log_function_call


class CodeSectionTimer:
    def __init__(self) -> None:
        self.logger: Optional[logging.Logger] = None
        self.sections: dict[str, dict] = {}
        self.current_section: Optional[str] = None

    def set_logger(self, logger: logging.Logger) -> None:
        self.logger = logger

    def section(self, section_name: str) -> Self:
        if section_name not in self.sections:
            self.sections[section_name] = {"start_time": None, "end_time": None}
        self.current_section = section_name
        return self

    def start(self) -> None:
        if self.sections[self.current_section]["start_time"] is not None:
            raise AlreadyExistsError(
                f"section '{self.current_section}' has already started"
            )
        self.sections[self.current_section]["start_time"] = time.perf_counter()
        self.logger.info("Started section '%s'", self.current_section)

    def end(self) -> None:
        if self.sections[self.current_section]["end_time"] is not None:
            raise AlreadyExistsError(
                f"section '{self.current_section}' has already finished"
            )
        self.sections[self.current_section]["end_time"] = time.perf_counter()
        seconds_elapsed = (
            self.sections[self.current_section]["end_time"]
            - self.sections[self.current_section]["start_time"]
        )
        self.logger.info(
            "Finished section '%s' (total runtime %s seconds = %s minutes)",
            self.current_section,
            f"{seconds_elapsed:,.0f}",
            f"{(seconds_elapsed/60):,.2f}",
        )


code_section_timer = CodeSectionTimer()
