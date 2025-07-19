import logging
import sys
from logging.handlers import RotatingFileHandler
import os

# Define a consistent log format
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'

def configure_logging(logger_name: str, log_level=logging.INFO, logs_base_dir=None):
    """
    Configures and returns a logger instance for a specific service or component.
    Log files will be created in <logs_base_dir>/<service_name>.log
    """
    if logs_base_dir is None:
        raise ValueError("logs_base_dir must be provided to determine the logs directory.")

    # Ensure the base directory for logs exists (e.g., home_inventory/logs)
    os.makedirs(logs_base_dir, exist_ok=True)

    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    logger.propagate = False # Prevent logs from being duplicated by the root logger

    formatter = logging.Formatter(LOG_FORMAT)

    # Add Console Handler if not already present
    if not any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Add File Handler if not already present for this path
    log_file_path = os.path.join(logs_base_dir, f"{logger_name}.log")
    if not any(isinstance(handler, RotatingFileHandler) and handler.baseFilename == os.path.abspath(log_file_path) for handler in logger.handlers):
        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=10 * 1024 * 1024, # 10 MB per file
            backupCount=5              # Keep 5 historical log files
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger