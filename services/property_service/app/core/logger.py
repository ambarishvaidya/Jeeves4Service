import logging
import os
from services.shared.j4s_logging_lib.j4s_logger import configure_logging

# # Determine the absolute path to the project root's 'logs' directory.
# # This assumes the script is run from the project root or the path is relative to it.
# # os.path.dirname(__file__) is 'services/user_service/app/core'
# # os.path.abspath(...) makes it absolute
# # os.path.join(..., '..', '..', '..', 'logs') navigates up to the project root and then into 'logs'
# # A more robust way might be to define a PROJECT_ROOT constant if available globally.
# # For now, let's assume a relative path from the project root is needed.
# # If running `python services/user_service/app/services/add_user.py` from project root:
# # The logs directory is at the same level as 'services'
# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
# logs_directory = os.path.join(project_root, 'logs')

# Configure the logger using the shared library, providing the required logs_base_dir
logger = configure_logging(logger_name="property_service", log_level=logging.INFO, logs_base_dir=f".")

if __name__ == "__main__":
    logger.info("This is a test message from core/logger.py, confirming log setup.")
    logger.warning("This message should go to console and file.")

