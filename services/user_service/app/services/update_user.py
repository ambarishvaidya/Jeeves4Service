from services.user_service.app.models.user import User


class UpdateUserService:
    """Service class for updating users with dependency injection"""
    
    def __init__(self, logger, session):
        self.logger = logger
        self.session = session
    
    def update_user(self, user_id, updates):
        """Update user information"""
        try:
            self.logger.info(f"Starting user update for user ID: {user_id}")
            
            # Get the user
            user = self.session.query(User).filter(User.id == user_id).first()
            if not user:
                self.logger.error(f"User with ID {user_id} not found")
                raise ValueError("User not found")
            
            # Update fields
            for field, value in updates.items():
                if hasattr(user, field):
                    setattr(user, field, value)
                    self.logger.info(f"Updated {field} for user ID: {user_id}")
            
            self.session.commit()
            self.logger.info(f"Successfully updated user ID: {user_id}")
            
            return {"user_id": user_id, "message": "User updated successfully"}
            
        except ValueError as ve:
            # ValueError exceptions are already logged above, just re-raise
            raise ve
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error during user update: {str(e)}")
            raise
        
        finally:
            if self.session:
                self.session.close()


# Legacy function for backward compatibility
def update_user(user_id, updates):
    """Legacy function wrapper - deprecated, use UpdateUserService instead"""
    from services.user_service.app.di.containers import ServiceFactory
    
    service = ServiceFactory.get_update_user_service()
    return service.update_user(user_id, updates)