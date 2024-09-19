"""Functionality related to logging"""

import functools
import json
import logging
import time
from types import SimpleNamespace
from typing import Any, Callable, Final, Optional, Self

import google.cloud.logging

from src.custom_exceptions import AlreadyExistsError

BASE_LOGGER_FORMAT: Final[str] = (
    "%(asctime)s : %(name)s : %(levelname)s : [daily ELT] %(message)s"
)

gcp_logging_client = google.cloud.logging.Client()

log_handlers = SimpleNamespace(
    gcp=google.cloud.logging.handlers.CloudLoggingHandler(
        gcp_logging_client  # writes to GCP Cloud Logging
    ),
    stream=logging.StreamHandler(),  # writes to standard out
    file=logging.FileHandler("main.log"),  # writes to local file
)
for handler in log_handlers.__dict__.values():
    handler.setFormatter(logging.Formatter(BASE_LOGGER_FORMAT))


def create_default_logger(
    logger_name: str,
    handlers: list[logging.Handler] = [log_handlers.stream],
) -> logging.Logger:
    """Creates a new logger with default settings"""
    logger = logging.getLogger(logger_name)
    if logger.handlers:
        raise AlreadyExistsError(f"logger {logger_name} already exists")
    logger.setLevel(logging.INFO)
    for handler in handlers:
        logger.addHandler(handler)
    return logger


def change_logger_format(logger: logging.Logger, new_format: str) -> None:
    """Changes the format of the provided logger (in all of it's handlers)"""
    new_formatter = logging.Formatter(new_format)
    for handler in logger.handlers:
        handler.setFormatter(new_formatter)


def str_truncate(input_obj: Any, max_nchar: int) -> str:
    """Returns a truncated string version of `input_obj` if it is longer than `max_nchar`"""
    if isinstance(input_obj, (int, float)):
        input_str: str = str(input_obj)
    else:
        input_str: str = f"'{input_obj}'"
    if len(input_str) > max_nchar:
        return f"{input_str[:max_nchar]}..."
    return input_str


def dynamic_str_truncate(input_element: Any, max_nchar: int) -> str:
    """Returns a string version of `input_element`, possibly truncating it (or the
    items within it) based on its length and type"""
    match input_element:
        case list():
            return json.dumps(
                [str_truncate(x, max_nchar) for x in input_element], indent=4
            )
        case dict():
            return json.dumps(
                {
                    str_truncate(k, max_nchar): str_truncate(v, max_nchar)
                    for k, v in input_element.items()
                },
                indent=4,
            )
        case tuple():
            return json.dumps(
                tuple([str_truncate(x, max_nchar) for x in input_element]),
                indent=4,
            )
        case set():
            return (
                "set(["
                + json.dumps(
                    [str_truncate(x, max_nchar) for x in input_element], indent=4
                )[1:-1]
                + "])"
            )
        case _:
            return str_truncate(input_element, max_nchar)


def log_function_or_method_call(
    logger: logging.Logger,
    loglevel: int = logging.INFO,
    log_inputs: bool = False,
    log_outputs: bool = False,
    log_inputs_max_nchar: int = 50,
    log_outputs_max_nchar: int = 50,
    log_runtime_metrics: bool = False,
):
    """A function decorator which generates log messages when the function/method is run

    Args:
        logger (logging.Logger): Log messages will be logged using this logger
        loglevel (int, optional): Log messages will be logged at this level (e.g. logging.DEBUG, logging.INFO)
        log_inputs (bool, optional): If True, input argument values to the function/method will be logged (long values truncated)
        log_outputs (bool, optional): If True, the output of the function/method will be logged (long values truncated)
        log_inputs_max_nchar (int, optional): Input argument values longer than this (after conversion to a str) are truncated in the log message
        log_outputs_max_nchar (int, optional): Values in the function output longer than this (after conversion to a str) are truncated in the log message
        log_runtime_metrics (bool, optional): If True, logs the total execution time of the function (in future, I want to log memory and compute statistics as well)
    """

    def decorator_log_function_call(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper_log_function_call(*args, **kwargs):
            prerun_log_message: str = f"Called {func.__name__}("
            if log_inputs:
                prerun_log_message += ", ".join(
                    [dynamic_str_truncate(arg, log_inputs_max_nchar) for arg in args]
                )
                prerun_log_message += ", ".join(
                    [
                        f"{dynamic_str_truncate(key, log_inputs_max_nchar)}={dynamic_str_truncate(value, log_inputs_max_nchar)}"
                        for key, value in kwargs.items()
                    ]
                )
            prerun_log_message += ")"
            logger.log(loglevel, prerun_log_message)

            start_time: float = time.perf_counter()
            func_output = func(*args, **kwargs)
            end_time: float = time.perf_counter()
            total_execution_time_n_seconds: float = end_time - start_time

            postrun_log_message: str = f"Finished function/method {func.__name__}()"
            if log_outputs:
                postrun_log_message += f"""
    --Function/method Output--
{dynamic_str_truncate(func_output, log_outputs_max_nchar)}"""
            if log_runtime_metrics:
                postrun_log_message += f"""
    --Runtime metrics--
    Total execution time: {total_execution_time_n_seconds:.2f} seconds = {(total_execution_time_n_seconds/60):.2f} minutes
    (in future I want to add statistics here related to memory and CPU usage)"""
            if log_outputs or log_runtime_metrics:
                logger.log(loglevel, postrun_log_message)

            return func_output

        return wrapper_log_function_call

    return decorator_log_function_call


class CodeSectionTimer:
    """Logs runtime between 2 checkpoints (i.e. times a code section)

    Example:
        >>> import logging
        >>> logger: logging.Logger = create_default_logger(__name__)
        >>> code_section_timer = CodeSectionTimer()
        >>> code_section_timer.section("load data").start(logging.INFO)
        >>> code_section_timer.section("load_data").end(logging.INFO)
    """

    def __init__(self) -> None:
        self.logger: Optional[logging.Logger] = None
        self.sections: dict[str, dict] = {}
        self.current_section: Optional[str] = None

    def set_logger(self, logger: logging.Logger) -> None:
        self.logger = logger

    def section(self, section_name: str) -> Self:
        """Selects an existing named section (or creates it if it doesn't exist)"""
        if section_name not in self.sections:
            self.sections[section_name] = {"start_time": None, "end_time": None}
        self.current_section = section_name
        return self

    def start(self, loglevel: int = logging.INFO) -> None:
        """Starts the timer for the currently selected section"""
        if self.sections[self.current_section]["start_time"] is not None:
            raise AlreadyExistsError(
                f"section '{self.current_section}' has already started"
            )
        self.sections[self.current_section]["start_time"] = time.perf_counter()
        self.logger.log(loglevel, "Started section '%s'", self.current_section)

    def end(self, loglevel: int = logging.INFO) -> None:
        """Stops the running timer of the currently selected section"""
        if self.sections[self.current_section]["end_time"] is not None:
            raise AlreadyExistsError(
                f"section '{self.current_section}' has already finished"
            )
        self.sections[self.current_section]["end_time"] = time.perf_counter()
        seconds_elapsed = (
            self.sections[self.current_section]["end_time"]
            - self.sections[self.current_section]["start_time"]
        )
        self.logger.log(
            loglevel,
            "Finished section '%s' (total runtime %s seconds = %s minutes)",
            self.current_section,
            f"{seconds_elapsed:,.0f}",
            f"{(seconds_elapsed/60):,.2f}",
        )


code_section_timer = CodeSectionTimer()
