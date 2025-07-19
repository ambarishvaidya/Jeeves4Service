"""Dependency injection container for user service"""

from dependency_injector import containers, providers
from services.user_service.app.db.session import SessionLocal
from services.shared.j4s_crypto_lib.password_processor import generate_hash, verify_password
from services.shared.j4s_logging_lib.j4s_logger import configure_logging
import logging


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
    """Application container for dependency injection"""
    
    # Configuration
    config = providers.Configuration()
    
    # Core dependencies
    logger_factory = providers.Factory(LoggerFactory.create_for_service)
    db_session = providers.Factory(SessionLocal)
    
    # Shared dependencies (j4s libraries)
    crypto_hash_service = providers.Object(generate_hash)
    crypto_verify_service = providers.Object(verify_password)
    
    # Service providers with automatic dependency injection
    register_user_service = providers.Factory(
        "services.user_service.app.services.register_user.RegisterUserService",
        logger=providers.Factory(
            LoggerFactory.create_logger_for,
            logger_name="RegisterUserService"
        ),
        session=db_session,
        crypto_hash_service=crypto_hash_service
    )
    
    activate_deactivate_user_service = providers.Factory(
        "services.user_service.app.services.activate_deactivate_user.ActivateDeactivateUserService",
        logger=providers.Factory(
            LoggerFactory.create_logger_for,
            logger_name="ActivateDeactivateUserService"
        ),
        session=db_session
    )
    
    change_password_service = providers.Factory(
        "services.user_service.app.services.change_password.ChangePasswordService",
        logger=providers.Factory(
            LoggerFactory.create_logger_for,
            logger_name="ChangePasswordService"
        ),
        session=db_session,
        crypto_hash_service=crypto_hash_service,
        crypto_verify_service=crypto_verify_service
    )
    
    complete_registration_service = providers.Factory(
        "services.user_service.app.services.complete_registration.CompleteRegistrationService",
        logger=providers.Factory(
            LoggerFactory.create_logger_for,
            logger_name="CompleteRegistrationService"
        ),
        session=db_session,
        crypto_hash_service=crypto_hash_service,
        crypto_verify_service=crypto_verify_service
    )
    
    add_user_service = providers.Factory(
        "services.user_service.app.services.add_user.AddUserService",
        logger=providers.Factory(
            LoggerFactory.create_logger_for,
            logger_name="AddUserService"
        ),
        session=db_session,
        crypto_hash_service=crypto_hash_service
    )
    
    update_user_service = providers.Factory(
        "services.user_service.app.services.update_user.UpdateUserService",
        logger=providers.Factory(
            LoggerFactory.create_logger_for,
            logger_name="UpdateUserService"
        ),
        session=db_session
    )


# Service factory for easy access
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
    def get_register_user_service(cls):
        """Get RegisterUserService instance"""
        return cls.get_container().register_user_service()
    
    @classmethod
    def get_activate_deactivate_user_service(cls):
        """Get ActivateDeactivateUserService instance"""
        return cls.get_container().activate_deactivate_user_service()
    
    @classmethod
    def get_change_password_service(cls):
        """Get ChangePasswordService instance"""
        return cls.get_container().change_password_service()
    
    @classmethod
    def get_complete_registration_service(cls):
        """Get CompleteRegistrationService instance"""
        return cls.get_container().complete_registration_service()
    
    @classmethod
    def get_add_user_service(cls):
        """Get AddUserService instance"""
        return cls.get_container().add_user_service()
    
    @classmethod
    def get_update_user_service(cls):
        """Get UpdateUserService instance"""
        return cls.get_container().update_user_service()
