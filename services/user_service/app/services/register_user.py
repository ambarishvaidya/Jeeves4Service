from ast import In
from psycopg2 import IntegrityError
from pydantic import BaseModel, EmailStr
from datetime import date
from services.user_service.app.dto.registration import RegisterUserRequest, RegisterUserResponse
from services.user_service.app.models.user import User, UserPassword
import secrets
import string


class RegisterUserService:
    """Service class for user registration with dependency injection"""
    
    def __init__(self, logger, session, crypto_hash_service):
        self.logger = logger
        self.session = session
        self.crypto_hash_service = crypto_hash_service
    
    def register_user(self, request: RegisterUserRequest) -> RegisterUserResponse:
        """Register a new user with family management"""
        try:
            self.logger.info(f"Starting user registration for email: {request.email}")
            
            self._validate_user_inputs(request)

            # Hash password for main user
            (password_hash, salt) = self.crypto_hash_service(request.password)
            
            # Create main user (admin)
            main_user = User(
                first_name=request.first_name,
                last_name=request.last_name,
                email=request.email,
                password_hash=password_hash,
                salt=salt,
                dob=request.dob,
                is_admin=True
            )
            
            self.session.add(main_user)
            self.session.flush()  # To get the user ID
            
            # Create UserPassword entry for main user (for testing/debugging purposes)
            main_user_password = UserPassword(
                user_id=main_user.id,
                email=main_user.email,
                password_str=request.password  # Store original password (only for testing!)
            )
            self.session.add(main_user_password)
            
            self.logger.info(f"Created main user with ID: {main_user.id}")
                                    
            self.session.commit()            
            
            return RegisterUserResponse(
                user_id=main_user.id,
                message="User registration completed successfully"
            )
            
        except IntegrityError as e:
            self.session.rollback()
            self.logger.error(f"Integrity error during user registration: {str(e)}")
            raise IntegrityError("User already exists")   
        
        except ValueError as ve:
            self.session.rollback()
            self.logger.error(f"Value error during user registration: {str(ve)}")
            raise ve

        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error during user registration: {str(e)}")
            raise
            
        finally:
            if self.session:
                self.session.close()

    def _validate_user_inputs(self, request: RegisterUserRequest):
        """Validate user input data"""
        import re
        
        # Enhanced email validation
        if not request.email:
            raise ValueError("Email is required")
        
        # Basic email regex pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, request.email):
            raise ValueError("Invalid email format")
        
        # Check for common invalid patterns
        if request.email.startswith('.') or request.email.endswith('.'):
            raise ValueError("Invalid email format")
        
        if '..' in request.email:
            raise ValueError("Invalid email format")
        
        if len(request.password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if request.dob > date.today():
            raise ValueError("Date of birth cannot be in the future")
        
        if request.first_name.strip() == "":
            raise ValueError("First name cannot be empty")
        
        if request.last_name.strip() == "":
            raise ValueError("Last name cannot be empty")
        
        # Additional validation logic can be added here


# Legacy function for backward compatibility
def register_user(request: RegisterUserRequest, session, logger=None) -> RegisterUserResponse:
    """Legacy function wrapper - deprecated, use RegisterUserService instead"""
    from services.user_service.app.di.containers import ServiceFactory
    
    service = ServiceFactory.get_register_user_service()
    return service.register_user(request)


def validate_user_inputs(request: RegisterUserRequest):
    """Legacy function wrapper - deprecated, use RegisterUserService._validate_user_inputs instead"""
    from services.user_service.app.di.containers import ServiceFactory
    
    service = ServiceFactory.get_register_user_service()
    return service._validate_user_inputs(request)    