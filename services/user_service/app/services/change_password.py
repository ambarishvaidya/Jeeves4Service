from services.user_service.app.dto.user import ChangePasswordRequest, ChangePasswordResponse
from services.user_service.app.models.user import User, UserPassword


class ChangePasswordService:
    """Service class for password changes with dependency injection"""
    
    def __init__(self, logger, session, crypto_hash_service, crypto_verify_service):
        self.logger = logger
        self.session = session
        self.crypto_hash_service = crypto_hash_service
        self.crypto_verify_service = crypto_verify_service
    
    def change_password(self, request: ChangePasswordRequest) -> ChangePasswordResponse:
        """Change user password"""
        try:
            self.logger.info(f"Starting password change for user ID: {request.user_id}")
            
            # Get the user
            user = self.session.query(User).filter(User.id == request.user_id).first()
            if not user:
                self.logger.error(f"User with ID {request.user_id} not found")
                raise ValueError("User not found")
            
            # Verify old password
            if not self.crypto_verify_service(user.password_hash, request.old_password, user.salt):
                self.logger.error(f"Invalid old password for user ID: {request.user_id}")
                raise ValueError("Invalid old password")
            
            # Hash new password
            (new_password_hash, new_salt) = self.crypto_hash_service(request.new_password)
            
            # Update user password
            user.password_hash = new_password_hash
            user.salt = new_salt
            
            # Update UserPassword table (for testing/debugging purposes)
            user_password = self.session.query(UserPassword).filter(UserPassword.user_id == request.user_id).first()
            if user_password:
                user_password.password_str = request.new_password  # Update with new password (only for testing!)
                self.logger.info(f"Updated UserPassword table for user ID: {request.user_id}")
            else:
                # Create new entry if it doesn't exist
                new_user_password = UserPassword(
                    user_id=request.user_id,
                    email=user.email,
                    password_str=request.new_password
                )
                self.session.add(new_user_password)
                self.logger.info(f"Created new UserPassword entry for user ID: {request.user_id}")
            
            self.session.commit()
            self.logger.info(f"Successfully changed password for user ID: {request.user_id}")
            
            return ChangePasswordResponse(
                user_id=request.user_id,
                message="Password changed successfully"
            )
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error during password change: {str(e)}")
            raise
        
        finally:
            if self.session:
                self.session.close()


# Legacy function for backward compatibility
def change_password(request: ChangePasswordRequest, session) -> ChangePasswordResponse:
    """Legacy function wrapper - deprecated, use ChangePasswordService instead"""
    from services.user_service.app.di.containers import ServiceFactory
    
    service = ServiceFactory.get_change_password_service()
    return service.change_password(request)