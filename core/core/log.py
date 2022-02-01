import os
from logging import Formatter, StreamHandler, getLogger


def setup_logger(name: str) -> None:
    """
    Sets up a common logging format.

    Args:
        name (str): `name` of the logger to setup
    """
    level = os.getenv("LOG_LEVEL", "INFO")
    logger = getLogger(name)
    logger.setLevel(level)
    handler = StreamHandler()
    formatter = Formatter("%(asctime)s - %(levelname)s - %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
