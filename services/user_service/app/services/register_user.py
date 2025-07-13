from ast import In
from psycopg2 import IntegrityError
from pydantic import BaseModel, EmailStr
from datetime import date
from services.user_service.app.dto.registration import RegisterUserRequest, RegisterUserResponse
from services.user_service.app.dto.user import AddUserRequest
from services.shared.j4s_crypto_lib.password_processor import generate_hash
from services.user_service.app.core.logger import logger
from services.user_service.app.models.user import User
from services.user_service.app.models.family import Family
from services.user_service.app.db.session import SessionLocal
import uuid
import secrets
import string

# ...existing code...

def register_user(request: RegisterUserRequest, session: SessionLocal, logger) -> RegisterUserResponse:
    #logger = logger(__name__)
        
    try:
        logger.info(f"Starting user registration for email: {request.email}")
        
        validate_user_inputs(request)

        # Hash password for main user
        (password_hash, salt) = generate_hash(request.password)
        
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
        
        session.add(main_user)
        session.flush()  # To get the user ID
        
        logger.info(f"Created main user with ID: {main_user.id}")
        
        # Generate unique family UUID
        family_uuid = str(uuid.uuid4())
        logger.info(f"Generated family UUID: {family_uuid}")

        # Create family entry for main user
        main_family = Family(
            user_id=main_user.id,
            family_uuid=family_uuid,
            is_admin=True
        )
        session.add(main_family)
        
        # Process additional users if any
        if request.additional_users:
            logger.info(f"Processing {len(request.additional_users)} additional users")
            
            for additional_user in request.additional_users:
                try:
                    # Generate 8-character dynamic password
                    dynamic_password = ''.join(secrets.choice(
                        string.ascii_letters + string.digits
                    ) for _ in range(8))
                    
                    # Hash the dynamic password
                    (user_password_hash, user_salt) = generate_hash(dynamic_password)
                    
                    # Create additional user
                    user = User(
                        first_name=additional_user.first_name,
                        last_name=additional_user.last_name,
                        email=additional_user.email,
                        password_hash=user_password_hash,
                        salt=user_salt,
                        dob=additional_user.dob,
                        is_admin=False
                    )
                    
                    session.add(user)
                    session.flush()
                    
                    logger.info(f"Created additional user with ID: {user.id}, dynamic password: {dynamic_password}")
                    
                    # Create family entry for additional user
                    user_family = Family(
                        user_id=user.id,
                        family_uuid=family_uuid,
                        is_admin=additional_user.is_admin if hasattr(additional_user, 'is_admin') else False
                    )
                    session.add(user_family)
                
                except IntegrityError as e:
                    logger.error(f"Integrity error for additional user {additional_user.email}: {str(e)}")
                
        
        session.commit()
        logger.info(f"Successfully registered user and family with UUID: {family_uuid}")
        
        return RegisterUserResponse(
            user_id=main_user.id,
            message="User registration completed successfully"
        )
        
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Integrity error during user registration: {str(e)}")
        raise IntegrityError("User already exists")   
    
    except ValueError as ve:
        session.rollback()
        logger.error(f"Value error during user registration: {str(ve)}")
        raise ve

    except Exception as e:
        session.rollback()
        logger.error(f"Error during user registration: {str(e)}")
        raise
        
    finally:
        pass

def validate_user_inputs(request: RegisterUserRequest):
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