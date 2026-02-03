import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(log_dir: str = "logs", log_filename: str = "trading_bot.log") -> None:
    """
    Configure application-wide logging.

    Creates a rotating file handler and a simple console handler.
    """
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_filename)

    logger = logging.getLogger()
    if logger.handlers:
        # Already configured
        return

    logger.setLevel(logging.INFO)

    file_handler = RotatingFileHandler(
        log_path, maxBytes=5 * 1024 * 1024, backupCount=2, encoding="utf-8"
    )
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter("%(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


