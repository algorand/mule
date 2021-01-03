import logging
import tempfile


from colorlog import ColoredFormatter


colors = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "red",
}
log_format = "[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s"
stream_format = "%(log_color)s%(levelname)-4s%(reset)s %(message)s"


def setup_file_logger(logger):
    fileHandler = logging.FileHandler("/tmp/foo.log")
    fileHandler.setLevel(logging.DEBUG)
    file_formatter = ColoredFormatter(
        log_format,
        datefmt=None,
        reset=True,
        log_colors=colors
    )
    logger.addHandler(fileHandler)


def setup_logger():
    logger = logging.getLogger(__name__)
    setup_file_logger(logger)
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


logger = setup_logger()
