import os
import sys
import logging
from pathlib import Path
from platformdirs import user_log_dir

from app.core.constants import APP_NAME, APP_ORGANIZATION

def setup_logging(log_level: int = logging.INFO) -> logging.Logger:
    """Configures structured Python logging with console and file appenders."""
    log_dir = Path(user_log_dir(APP_NAME, APP_ORGANIZATION))
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "lyricforge.log"

    logger = logging.getLogger("LyricForge")
    logger.setLevel(log_level)
    
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(filename)s:%(lineno)d]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)

    # File Handler
    try:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Failed to initialize log file handler: {e}")

    logger.info(f"Initialized {APP_NAME} logging framework. Log file: {log_file}")
    return logger

logger = setup_logging()
