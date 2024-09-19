# My Python Logging Setup

A toy codebase illustrating native python logging functionality.

To see it in action run

```bash
python main.py
```

Goals:

| Completed | Goal                                                                          | Notes                                                    |
| --------- | ----------------------------------------------------------------------------- | -------------------------------------------------------- |
| ✅        | unified logger formatting                                                     |                                                          |
| ✅        | dynamic logger formatting (easy to set and reset format, and done safely)     |
| ✅        | function decorator (logs function calls, inputs and outputs, runtime metrics) | Might not be aesthetic for all complex python data types |
| ❌        | class decorator (logs instantiations and method calls)                        | Haven't started this yet                                 |
| ✅        | section timer                                                                 |
| ❌        | flask/fastAPI route call logging                                              | Haven't started this yet                                 |
| ✅        | integration with Google Cloud logging                                         |                                                          |

Here are examples of the basic functionality available so far:

```python
import sys
from src.log import (
  BASE_LOGGER_FORMAT,
  create_default_logger,
  log_handlers,
  code_section_timer,
  log_function_or_method_call,
  change_logger_format,
)

logger = create_default_logger(__name__)

# automatically log all errors raised outside of a try/except except block
sys.excepthook = lambda err_type, err_value, err_traceback: logger.error(
    "Uncaught exception", exc_info=(err_type, err_value, err_traceback)
)

# basic log messages #
logger.info("an example log message")
# 2024-09-01 20:33:56,769 : __main__ : INFO : [daily ELT] an example log message

verbose_logger = create_default_logger(
  logger_name=f"verbose-{__name__}",
  handlers=[
    log_handlers.file,
    log_handlers.gcp,
    log_handlers.stream,
  ],
)
verbose_logger.info("this log message writes to local file `main.log`, to standard out, and to GCP cloud logging")

# code section timer #
import time
code_section_timer.set_logger(logger)
code_section_timer.section("outer section").start()
# 2024-09-01 20:34:11,504 : __main__ : INFO : [daily ELT] Started section 'outer section'
time.sleep(1)
code_section_timer.section("inner section").start()
# 2024-09-01 20:34:12,511 : __main__ : INFO : [daily ELT] Started section 'inner section'
time.sleep(2)
code_section_timer.section("inner section").end()
# 2024-09-01 20:34:14,518 : __main__ : INFO : [daily ELT] Finished section 'inner section' (total runtime 2 seconds = 0.03 minutes)
time.sleep(1)
code_section_timer.section("outer section").end()
# 2024-09-01 20:34:15,526 : __main__ : INFO : [daily ELT] Finished section 'outer section' (total runtime 4 seconds = 0.07 minutes)

# automatic function call logging #
@log_function_or_method_call(logger, log_inputs=True, log_outputs=True, log_runtime_metrics=True)
def do_nothing(task: str) -> None:
  ignore = task
  time.sleep(0.69)

do_nothing(task="delete the database")
# 2024-09-01 20:36:22,197 : __main__ : INFO : [daily ELT] Called do_nothing('task'='delete the database')
# 2024-09-01 20:36:22,892 : __main__ : INFO : [daily ELT] Finished function/method do_nothing()
#     --Function/method Output--
# 'None'
#     --Runtime metrics--
#     Total execution time: 0.69 seconds = 0.01 minutes
#     (in future I want to add statistics here related to memory and CPU usage)

# dynamic change of logger format #
for user in ("johann", "peter", "joe"):
    change_logger_format(
        logger,
        new_format=BASE_LOGGER_FORMAT.replace(
            "%(message)s",
            f"user='{user}' %(message)s"
        )
    )
    logger.info("loading user data")
    logger.info("processing user data")
# 2024-09-01 20:36:53,872 : __main__ : INFO : [daily ELT] user='johann' loading user data
# 2024-09-01 20:36:53,873 : __main__ : INFO : [daily ELT] user='johann' processing user data
# 2024-09-01 20:36:53,873 : __main__ : INFO : [daily ELT] user='peter' loading user data
# 2024-09-01 20:36:53,873 : __main__ : INFO : [daily ELT] user='peter' processing user data
# 2024-09-01 20:36:53,873 : __main__ : INFO : [daily ELT] user='joe' loading user data
# 2024-09-01 20:36:53,873 : __main__ : INFO : [daily ELT] user='joe' processing user data
change_logger_format(
    logger,
    new_format=BASE_LOGGER_FORMAT,
)
logger.info("logger format back to default")
# 2024-09-01 20:37:18,467 : __main__ : INFO : [daily ELT] logger format back to default
```
