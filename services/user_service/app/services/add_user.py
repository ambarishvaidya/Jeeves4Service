from services.user_service.app.core.logger import logger

def add_user():
    logger.info("Adding User")
    # Implementation of user addition logic goes here
    # ...
    logger.info("User added successfully")

if __name__ == "__main__":
    add_user()
    logger.info("add_user.py executed directly, user addition process completed.")