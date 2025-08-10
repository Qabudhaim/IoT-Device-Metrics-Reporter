import logging
from logging.handlers import RotatingFileHandler
import os
from typing import Optional

def setup_logger(log_file: Optional[str] = "metrics.log") -> None:
    """
    Sets up a rotating file logger for the application.

    This function configures the root logger to write log messages to a file
    located in a hidden ".log" directory within the project's directory. The log
    file uses rotation to limit its size and maintain backup files.

    Args:
        log_file (str, optional): The name of the log file. Defaults to "metrics.log".

    Side Effects:
        - Creates a ".log" directory in the project's directory if it does not exist.
        - Configures the root logger to use a RotatingFileHandler with a maximum file size of 1,000,000 bytes and up to 3 backup files.
        - Sets the logging level to INFO.
        - Clears any existing handlers from the root logger before adding the new handler.

    Example:
        setup_logger("my_app.log")
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(script_dir, ".log")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)

    logger: logging.Logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if logger.hasHandlers():
        logger.handlers.clear()

    handler: RotatingFileHandler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=3)
    formatter: logging.Formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
