
import logging
from venv import logger
from j4s_logger import configure_logging
from dependency_injector import containers, providers

from services.inventory_service.app.db.session import SessionLocal


class LoggerFactory:

    @staticmethod
    def create_logger_for(logger_name: str):
        return configure_logging(logger_name, log_level=logging.INFO, logs_base_dir=".")
    

class Container(containers.DeclarativeContainer):

    config = providers.Configuration()

    logger_factory = providers.Factory(LoggerFactory.create_logger_for)
    db_session = providers.Factory(SessionLocal)

class ServiceFactory:
    pass    