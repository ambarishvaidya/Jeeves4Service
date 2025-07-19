class AddUserService:
    """Service class for adding users with dependency injection"""
    
    def __init__(self, logger, session, crypto_hash_service):
        self.logger = logger
        self.session = session
        self.crypto_hash_service = crypto_hash_service
    
    def add_user(self, request=None):
        """Add a new user"""
        self.logger.info("Starting user addition process")
        
        # Implementation of user addition logic goes here
        # ...
        
        self.logger.info("User added successfully")
        return {"message": "User added successfully"}


# Legacy function for backward compatibility
def add_user():
    """Legacy function wrapper - deprecated, use AddUserService instead"""
    from services.user_service.app.di.containers import ServiceFactory
    
    service = ServiceFactory.get_add_user_service()
    return service.add_user()


if __name__ == "__main__":
    add_user()
    print("add_user.py executed directly, user addition process completed.")