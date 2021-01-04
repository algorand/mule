from datetime import datetime
import logging


from colorlog import ColoredFormatter


colors = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "red",
}

log_date_format = "%Y-%m-%d %H:%M:%S"
log_format = "[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s"
stream_format = "%(log_color)s%(levelname)-4s%(reset)s %(message)s"


def setup_file_logger(logger, tempfile):
    fileHandler = logging.FileHandler(tempfile)
    fileHandler.setLevel(logging.DEBUG)
    file_formatter = ColoredFormatter(
        log_format,
        datefmt=log_date_format,
        reset=True,
        log_colors=colors
    )
    logger.addHandler(fileHandler)


def setup_logger():
    logger = logging.getLogger(__name__)
    setup_stream_logger(logger)
    return logger


def setup_stream_logger(logger):
    # Default is to write to stderr.
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        ColoredFormatter(
            stream_format,
            datefmt=None,
            reset=True,
            log_colors=colors
        )
    )
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)


def start_debug(args):
    utc_time = datetime.utcnow().isoformat()
    tempfile = f"/tmp/mule.{utc_time}.log"
    setup_file_logger(logger, tempfile)
    logger.setLevel(logging.DEBUG)
    logger.info(f"Logs for this session are available in {tempfile}")
    logger.debug("--------------------------")
    logger.debug(utc_time)
    logger.debug(args)
    logger.debug("--------------------------")


logger = setup_logger()
