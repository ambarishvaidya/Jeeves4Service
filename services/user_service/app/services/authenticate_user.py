import secrets
from services.user_service.app.dto.user import AuthenticateUserResponse
from services.user_service.app.models.user import User


class AuthenticateUser:

    def __init__(self, logger, session, crypto_service):
        self.logger = logger
        self.session = session
        self.crypto_service = crypto_service

    def authenticate(self, email: str, password: str):
        """Authenticate a user by email and password"""
        try:
            self.logger.info(f"Starting authentication for email: {email}")
            
            user = self.session.query(User).filter(User.email == email).first()
            if not user:
                self.logger.error(f"User with email {email} not found")
                raise ValueError("User not found")
            
            # Verify password
            if not self.crypto_service.verify_password(user.password_hash, password, user.salt):
                self.logger.error("Invalid password")
                raise ValueError("Invalid password")
            
            self.logger.info(f"User with email {email} authenticated successfully")
            return AuthenticateUserResponse(
                session_id=secrets.token_hex(16),  # Generate a GUID for the session
                user_id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                is_admin=user.is_admin
            )
        
        except ValueError as ve:
            # ValueError exceptions are already logged above, just re-raise
            raise ve
        
        except Exception as e:
            self.logger.error(f"Error during authentication: {str(e)}")
            raise
        