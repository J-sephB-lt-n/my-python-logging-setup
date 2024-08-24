"""The entrypoint script for the project"""

# import src.a_useful_module
import src.log

logger = src.log.create_default_stream_logger(__name__)

logger.info("Here is a log message from main.py")
