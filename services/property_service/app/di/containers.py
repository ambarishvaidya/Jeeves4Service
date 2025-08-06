import logging
from services.property_service.app.services import get_property
from services.shared.j4s_logging_lib.j4s_logger import configure_logging
from dependency_injector import containers, providers
from services.property_service.app.db.session import SessionLocal


class LoggerFactory:
    """Smart logger factory that automatically detects service names"""
    
    @staticmethod
    def create_for_service(service_class_path: str):
        """Create logger automatically based on service class name"""
        class_name = service_class_path.split('.')[-1]  # Get class name from full path
        service_name = class_name.lower().replace('service', '')  # RegisterUserService -> registeruser
        return configure_logging(logger_name=service_name, log_level=logging.INFO, logs_base_dir=".")
    
    @staticmethod
    def create_logger_for(logger_name: str):
        """Create logger automatically based on passed name"""
        return configure_logging(logger_name=logger_name, log_level=logging.INFO, logs_base_dir=".")


class Container(containers.DeclarativeContainer):

    config = providers.Configuration()

    # Core dependencies
    logger_factory = providers.Factory(LoggerFactory.create_for_service)
    db_session = providers.Factory(SessionLocal)

    # Service providers with automatic dependency injection
    add_main_storage_service = providers.Factory(
        "services.property_service.app.services.add_main_storage.AddMainStorage",
        logger=providers.Factory(
            LoggerFactory.create_logger_for,
            logger_name="AddMainStorageService"
        ),
        session=db_session
    )

    add_property_service = providers.Factory(
        "services.property_service.app.services.add_property.AddProperty",
        logger=providers.Factory(
            LoggerFactory.create_logger_for,
            logger_name="AddPropertyService"
        ),
        session=db_session
    )

    get_property_service = providers.Factory(
        "services.property_service.app.services.get_property.GetProperty",
        logger=providers.Factory(
            LoggerFactory.create_logger_for,
            logger_name="GetPropertyService"
        ),
        session=db_session
    )    

    add_rooms_service = providers.Factory(
        "services.property_service.app.services.add_rooms.AddRooms",
        logger=providers.Factory(
            LoggerFactory.create_logger_for,
            logger_name="AddRoomsService"
        ),
        session=db_session
    )

    add_storage_service = providers.Factory(
        "services.property_service.app.services.add_storage.AddStorage",
        logger=providers.Factory(
            LoggerFactory.create_logger_for,
            logger_name="AddStorageService"
        ),
        session=db_session
    )

    add_users_to_property_service = providers.Factory(
        "services.property_service.app.services.add_users_property.AddUsersProperty",
        logger=providers.Factory(
            LoggerFactory.create_logger_for,
            logger_name="AddUsersToPropertyService"
        ),
        session=db_session
    )

    update_property_service = providers.Factory(
        "services.property_service.app.services.update_property.UpdateProperty",
        logger=providers.Factory(
            LoggerFactory.create_logger_for,
            logger_name="UpdatePropertyService"
        ),
        session=db_session
    )

    update_room_service = providers.Factory(
        "services.property_service.app.services.update_room.UpdateRoom",
        logger=providers.Factory(
            LoggerFactory.create_logger_for,
            logger_name="UpdateRoomService"
        ),
        session=db_session
    )

    get_rooms_service = providers.Factory(
        "services.property_service.app.services.get_rooms.GetRooms",
        logger=providers.Factory(
            LoggerFactory.create_logger_for,
            logger_name="GetRoomsService"
        ),
        session=db_session
    )

    get_storage_service = providers.Factory(
        "services.property_service.app.services.get_storage.GetStorage",
        logger=providers.Factory(
            LoggerFactory.create_logger_for,
            logger_name="GetStorageService"
        ),
        session=db_session
    )


class ServiceFactory:
    """Factory to create service instances with injected dependencies"""
    @staticmethod
    def get_add_property_service():
        return Container.add_property_service()

    @staticmethod
    def get_get_property_service():
        return Container.get_property_service()

    @staticmethod
    def get_update_property_service():
        return Container.update_property_service()

    @staticmethod
    def get_update_room_service():
        return Container.update_room_service()

    @staticmethod
    def get_add_rooms_service():
        return Container.add_rooms_service()
    
    @staticmethod
    def get_add_main_storage_service():
        return Container.add_main_storage_service() 
    
    @staticmethod
    def get_add_storage_service():
        return Container.add_storage_service()
    
    @staticmethod
    def get_add_users_to_property_service():
        return Container.add_users_to_property_service()
    
    @staticmethod
    def get_update_property_service():
        return Container.update_property_service()
    
    @staticmethod
    def get_update_room_service():
        return Container.update_room_service()
    
    @staticmethod
    def get_get_rooms_service():
        return Container.get_rooms_service()
    
    @staticmethod
    def get_get_storage_service():
        return Container.get_storage_service()