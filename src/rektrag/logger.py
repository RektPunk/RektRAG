import logging
import sys


def init_logger() -> logging.Logger:
    LOGGER_NAME = "RektRAG"
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.hasHandlers():
        logger.handlers.clear()

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(levelname)s] %(asctime)s [%(name)s] %(filename)s:%(lineno)d: %(message)s"
    )
    ch.setFormatter(formatter)

    logger.addHandler(ch)
    return logger


logger = init_logger()
