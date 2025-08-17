import logging
import sys
from logging.handlers import RotatingFileHandler
from services.shared.request_context import RequestContext
from services.shared.j4s_utilities.token_models import TokenPayload
import os

# Define a consistent log format
LOG_FORMAT = '%(asctime)s - %(traceid)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'


class ContextAwareFormatter(logging.Formatter):
    """Custom formatter that dynamically injects trace_id from RequestContext into log records."""
    
    def format(self, record):
        # Get trace_id DYNAMICALLY on each log call
        payload_token = RequestContext.get_token()
        trace_id = payload_token.trace_id if payload_token and hasattr(payload_token, 'trace_id') and payload_token.trace_id else 'NO-TRACE'
        
        # Add trace_id to the log record
        record.traceid = trace_id
        
        # Call the parent formatter - this uses the stored format string
        # The format string is accessible via: self._style._fmt
        return super().format(record)


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

    # Use the custom formatter that dynamically gets trace_id on each log call
    formatter = ContextAwareFormatter(LOG_FORMAT)

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