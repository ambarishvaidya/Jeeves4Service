from services.user_service.app.dto.user import CompleteRegistrationRequest, CompleteRegistrationResponse
from services.shared.j4s_crypto_lib.password_processor import generate_hash, verify_password
from services.user_service.app.core.logger import logger
from services.user_service.app.models import User
from services.user_service.app.db import SessionLocal

def complete_registration(request: CompleteRegistrationRequest, session: SessionLocal) -> CompleteRegistrationResponse:
    logger = logger(__name__)
    
    try:
        logger.info(f"Starting complete registration for user ID: {request.user_id}")
        
        # Get the user
        user = session.query(User).filter(User.id == request.user_id).first()
        if not user:
            logger.error(f"User with ID {request.user_id} not found")
            raise ValueError("User not found")
        
        # Verify old password
        if not verify_password(request.old_password, user.password_hash, user.salt):
            logger.error(f"Invalid old password for user ID: {request.user_id}")
            raise ValueError("Invalid old password")
        
        # Hash new password
        (new_password_hash, new_salt) = generate_hash(request.new_password)
        
        # Update user with all fields
        user.first_name = request.first_name
        user.last_name = request.last_name
        user.email = request.email
        user.dob = request.dob
        user.password_hash = new_password_hash
        user.salt = new_salt
        
        session.commit()
        logger.info(f"Successfully completed registration for user ID: {request.user_id}")
        
        return CompleteRegistrationResponse(
            user_id=request.user_id,
            message="Registration completed successfully"
        )
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error during complete registration: {str(e)}")
        raise