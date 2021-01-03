import logging
import sys


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

#fileHandler = logging.FileHandler("foo.log")
#fileHandler.setLevel(logging.INFO)
#logger.addHandler(fileHandler)

#consoleHandler = logging.StreamHandler(sys.stdout)
#consoleHandler.setLevel(logging.INFO)
#logger.addHandler(consoleHandler)

def DEBUG():
    return logger.isEnabledFor(logging.DEBUG)
