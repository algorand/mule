from datetime import datetime
import logging


log_format = "%(asctime)s - %(levelname)s - %(message)s"


def setup_file_logger(logger, tempfile):
    file_handler = logging.FileHandler(tempfile)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)


def setup_logger():
    logger = logging.getLogger(__name__)
    setup_stream_logger(logger)
    return logger


def setup_stream_logger(logger):
    # Default is to write to stderr.
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)


def start_debug(args):
    tempfile = f"/tmp/mule.{datetime.utcnow().isoformat()}.log"
    setup_file_logger(logger, tempfile)
    logger.setLevel(logging.DEBUG)
    logger.info(f"Logs for this session are available in {tempfile}")
    logger.debug("--------------------------")
    logger.debug(args)
    logger.debug("--------------------------")


logger = setup_logger()
