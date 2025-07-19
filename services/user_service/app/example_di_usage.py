"""Example usage of the dependency injection system"""

from services.user_service.app.di.containers import Container, ServiceFactory
from services.user_service.app.dto.registration import RegisterUserRequest
from services.user_service.app.dto.user import ChangePasswordRequest
from datetime import date


def main():
    """Example of how to use the dependency injection system"""
    
    # Method 1: Using ServiceFactory (Recommended for most cases)
    print("=== Method 1: Using ServiceFactory ===")
    
    # Get service instance
    register_service = ServiceFactory.get_register_user_service()
    
    # Create a sample request
    request = RegisterUserRequest(
        first_name="John",
        last_name="Doe", 
        email="john.doe@example.com",
        password="SecurePassword123!",
        dob=date(1990, 1, 1)
    )
    
    try:
        # Use the service - all dependencies are automatically injected
        response = register_service.register_user(request)
        print(f"Registration successful: {response.message}")
        print(f"User ID: {response.user_id}")
    except Exception as e:
        print(f"Registration failed: {e}")
    
    # Method 2: Using Container directly (For advanced scenarios)
    print("\n=== Method 2: Using Container directly ===")
    
    # Initialize container
    container = Container()
    
    # Get multiple services
    change_password_service = container.change_password_service()
    activate_service = container.activate_deactivate_user_service()
    
    print("Services obtained from container:")
    print(f"- Change Password Service: {type(change_password_service).__name__}")
    print(f"- Activate/Deactivate Service: {type(activate_service).__name__}")
    
    # Method 3: Testing with mocked dependencies
    print("\n=== Method 3: For Testing (Mocked dependencies) ===")
    
    # Override dependencies for testing
    from unittest.mock import Mock
    
    test_container = Container()
    test_container.db_session.override(Mock())
    test_container.crypto_hash_service.override(Mock(return_value=("hash", "salt")))
    
    # Get service with mocked dependencies
    test_service = test_container.register_user_service()
    print(f"Test service with mocked dependencies: {type(test_service).__name__}")
    
    print("\n=== All Services Available ===")
    print("- RegisterUserService")
    print("- ActivateDeactivateUserService") 
    print("- ChangePasswordService")
    print("- CompleteRegistrationService")
    print("- AddUserService")
    print("- UpdateUserService")


if __name__ == "__main__":
    main()
