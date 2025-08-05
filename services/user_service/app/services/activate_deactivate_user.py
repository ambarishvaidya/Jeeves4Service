from services.user_service.app.dto.user import ActivateDeactivateUserRequest, ActivateDeactivateUserResponse
from services.user_service.app.models.user import User


class ActivateDeactivateUserService:
    """Service class for user activation/deactivation with dependency injection"""
    
    def __init__(self, logger, session):
        self.logger = logger
        self.session = session
    
    def activate_deactivate_user(self, request: ActivateDeactivateUserRequest) -> ActivateDeactivateUserResponse:
        """Activate or deactivate a user"""
        try:
            self.logger.info(f"Starting user activation/deactivation for user ID: {request.user_id} by admin ID: {request.admin_id}")
            
            # Verify admin exists and is admin
            admin = self.session.query(User).filter(User.id == request.admin_id).first()
            if not admin:
                self.logger.error(f"Admin with ID {request.admin_id} not found")
                raise ValueError("Admin not found")
            
            if not admin.is_admin:
                self.logger.error(f"User with ID {request.admin_id} is not an admin")
                raise ValueError("User is not authorized to perform this action")
            
            # Get the user to be activated/deactivated
            user = self.session.query(User).filter(User.id == request.user_id).first()
            if not user:
                self.logger.error(f"User with ID {request.user_id} not found")
                raise ValueError("User not found")
            
            # Update user active status
            user.is_active = request.is_active
            
            self.session.commit()
            
            status = "activated" if request.is_active else "deactivated"
            self.logger.info(f"Successfully {status} user ID: {request.user_id} by admin ID: {request.admin_id}")
            
            return ActivateDeactivateUserResponse(
                user_id=request.user_id,
                is_active=request.is_active,
                message=f"User {status} successfully"
            )
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error during user activation/deactivation: {str(e)}")
            raise
        
        finally:
            if self.session:
                self.session.close()


# Legacy function for backward compatibility
def activate_deactivate_user(request: ActivateDeactivateUserRequest, session) -> ActivateDeactivateUserResponse:
    """Legacy function wrapper - deprecated, use ActivateDeactivateUserService instead"""
    from services.user_service.app.di.containers import ServiceFactory
    
    service = ServiceFactory.get_activate_deactivate_user_service()
    return service.activate_deactivate_user(request)