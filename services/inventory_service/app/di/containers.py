
import logging
from services.shared.j4s_logging_lib.j4s_logger import configure_logging
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

    create_add_item_service = providers.Factory(
        "services.inventory_service.app.services.add_item.AddItem",
        logger=providers.Factory(
            LoggerFactory.create_logger_for,
            logger_name="InventoryService"
        ),
        session=db_session
    )

class ServiceFactory:

    """Factory class for accessing services from the container"""
    
    _container = None
    
    @classmethod
    def get_container(cls):
        """Get or create the container instance"""
        if cls._container is None:
            cls._container = Container()
        return cls._container

    @classmethod
    def get_add_item_service(cls):
       """Get the add item service instance"""
       return cls.get_container().create_add_item_service()