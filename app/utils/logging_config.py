import logging
from logging.handlers import RotatingFileHandler
from app.config import settings

def setup_logging():
    log_file = settings.LOG_DIR / "app.log"
    handler = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=5)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    # Optional: still log to console for docker logs
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
