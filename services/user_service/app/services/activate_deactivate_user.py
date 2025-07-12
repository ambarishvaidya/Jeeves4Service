from services.user_service.app.db import SessionLocal
from services.user_service.app.dto.user import ActivateDeactivateUserRequest, ActivateDeactivateUserResponse
from services.user_service.app.core.logger import logger
from services.user_service.app.models import User

def activate_deactivate_user(request: ActivateDeactivateUserRequest, session: SessionLocal) -> ActivateDeactivateUserResponse:
    logger = logger(__name__)
    
    try:
        logger.info(f"Starting user activation/deactivation for user ID: {request.user_id} by admin ID: {request.admin_id}")
        
        # Verify admin exists and is admin
        admin = session.query(User).filter(User.id == request.admin_id).first()
        if not admin:
            logger.error(f"Admin with ID {request.admin_id} not found")
            raise ValueError("Admin not found")
        
        if not admin.admin:
            logger.error(f"User with ID {request.admin_id} is not an admin")
            raise ValueError("User is not authorized to perform this action")
        
        # Get the user to be activated/deactivated
        user = session.query(User).filter(User.id == request.user_id).first()
        if not user:
            logger.error(f"User with ID {request.user_id} not found")
            raise ValueError("User not found")
        
        # Update user active status
        user.is_active = request.is_active
        
        session.commit()
        
        status = "activated" if request.is_active else "deactivated"
        logger.info(f"Successfully {status} user ID: {request.user_id} by admin ID: {request.admin_id}")
        
        return ActivateDeactivateUserResponse(
            user_id=request.user_id,
            is_active=request.is_active,
            message=f"User {status} successfully"
        )
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error during user activation/deactivation: {str(e)}")
        raise