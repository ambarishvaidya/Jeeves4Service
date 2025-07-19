"""Main entry point for the user service application"""

from services.user_service.app.di.containers import Container, ServiceFactory
from services.user_service.app.dto.registration import RegisterUserRequest
from datetime import date
import logging


def setup_application():
    """Initialize the application with dependency injection"""
    print("Initializing User Service Application...")
    
    # Initialize the container
    container = Container()
    
    # Optional: Configure any settings
    # container.config.from_dict({
    #     "database_url": "postgresql://...",
    #     "log_level": "INFO"
    # })
    
    print("Dependency injection container initialized successfully!")
    return container


def example_service_usage():
    """Example of how to use services in the application"""
    try:
        # Get a service using ServiceFactory
        register_service = ServiceFactory.get_register_user_service()
        
        # Example usage (would normally come from API endpoints or other sources)
        sample_request = RegisterUserRequest(
            first_name="Demo",
            last_name="User",
            email="demo@example.com",
            password="SecurePassword123!",
            dob=date(1990, 1, 1)
        )
        
        print(f"Using RegisterUserService: {type(register_service).__name__}")
        print("Service has properly injected dependencies:")
        print(f"- Logger: {type(register_service.logger)}")
        print(f"- Session: {type(register_service.session)}")
        print(f"- Crypto Service: {register_service.crypto_hash_service}")
        
        # Note: Uncomment below to actually register a user
        # response = register_service.register_user(sample_request)
        # print(f"Registration response: {response}")
        
    except Exception as e:
        print(f"Error during service usage: {e}")


def main():
    """Main application entry point"""
    print("=" * 50)
    print("USER SERVICE APPLICATION")
    print("=" * 50)
    
    # Setup dependency injection
    container = setup_application()
    
    # Example service usage
    print("\n--- Service Usage Example ---")
    example_service_usage()
    
    # Show available services
    print("\n--- Available Services ---")
    services = [
        "RegisterUserService",
        "ActivateDeactivateUserService", 
        "ChangePasswordService",
        "CompleteRegistrationService",
        "AddUserService",
        "UpdateUserService"
    ]
    
    for service in services:
        print(f"✓ {service}")
    
    print("\n--- Application Ready ---")
    print("All services are configured with dependency injection!")
    print("Use ServiceFactory.get_*_service() to access services throughout your application.")
    
    # In a real application, you would start your web server here
    # e.g., uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
