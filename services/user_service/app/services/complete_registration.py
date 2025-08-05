from services.user_service.app.dto.user import CompleteRegistrationRequest, CompleteRegistrationResponse
from services.user_service.app.models.user import User


class CompleteRegistrationService:
    """Service class for completing registration with dependency injection"""
    
    def __init__(self, logger, session, crypto_hash_service, crypto_verify_service):
        self.logger = logger
        self.session = session
        self.crypto_hash_service = crypto_hash_service
        self.crypto_verify_service = crypto_verify_service
    
    def complete_registration(self, request: CompleteRegistrationRequest) -> CompleteRegistrationResponse:
        """Complete user registration"""
        try:
            self.logger.info(f"Starting complete registration for user ID: {request.user_id}")
            
            # Get the user
            user = self.session.query(User).filter(User.id == request.user_id).first()
            if not user:
                self.logger.error(f"User with ID {request.user_id} not found")
                raise ValueError("User not found")
            
            # Verify old password
            if not self.crypto_verify_service(request.old_password, user.password_hash, user.salt):
                self.logger.error(f"Invalid old password for user ID: {request.user_id}")
                raise ValueError("Invalid old password")
            
            # Hash new password
            (new_password_hash, new_salt) = self.crypto_hash_service(request.new_password)
            
            # Update user with all fields
            user.first_name = request.first_name
            user.last_name = request.last_name
            user.email = request.email
            user.dob = request.dob
            user.password_hash = new_password_hash
            user.salt = new_salt
            
            self.session.commit()
            self.logger.info(f"Successfully completed registration for user ID: {request.user_id}")
            
            return CompleteRegistrationResponse(
                user_id=request.user_id,
                message="Registration completed successfully"
            )
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error during complete registration: {str(e)}")
            raise
        
        finally:
            if self.session:
                self.session.close()


# Legacy function for backward compatibility
def complete_registration(request: CompleteRegistrationRequest, session) -> CompleteRegistrationResponse:
    """Legacy function wrapper - deprecated, use CompleteRegistrationService instead"""
    from services.user_service.app.di.containers import ServiceFactory
    
    service = ServiceFactory.get_complete_registration_service()
    return service.complete_registration(request)