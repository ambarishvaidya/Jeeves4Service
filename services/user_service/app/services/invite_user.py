import secrets
import string
from typing import List

from psycopg2 import IntegrityError
from services.user_service.app.dto.user import InviteUser
from services.user_service.app.models.user import User, UserPassword
from datetime import date


class InviteUserService:

    def __init__(self, logger, session, crypto_hash_service):
        self.logger = logger
        self.session = session
        self.crypto_hash_service = crypto_hash_service

    def send_invite(self, request: List[InviteUser]) -> str:
        """Send invites to users"""
        self.logger.info("Starting invite user process")
        
        successful_invites = 0
        failed_invites = 0
        failed_users = []
        
        for user in request:
            try:
                # Create dynamic password
                dynamic_password = ''.join(secrets.choice(
                      string.ascii_letters + string.digits
                      ) for _ in range(8))
                            
                # Hash the dynamic password
                (user_password_hash, user_salt) = self.crypto_hash_service(dynamic_password)

                # Create user object
                new_user = User(
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=user.email,
                    password_hash=user_password_hash,
                    dob=date.min,
                    salt=user_salt,
                    is_admin=False  # Assuming invited users are not admins
                )

                self.session.add(new_user)
                self.session.flush()  # Ensure the user ID is generated
                
                user_password = UserPassword(
                    user_id=new_user.id,
                    email=user.email,
                    password_str=dynamic_password
                )
                self.session.add(user_password)
                
                # Commit each user individually
                self.session.commit()
                successful_invites += 1
                self.logger.info(f"Successfully invited user: {user.email}")

            except IntegrityError as e:
                # Extract just the message from IntegrityError
                error_msg = e.args[0] if e.args else str(e)
                self.logger.error(f"Error inviting user {user.email}: {error_msg}")
                self.session.rollback()
                failed_invites += 1
                failed_users.append(user.email)
                continue  # Continue with the next user
            
            except Exception as e:
                self.logger.error(f"Unexpected error inviting user {user.email}: {e}")
                self.session.rollback()
                failed_invites += 1
                failed_users.append(user.email)
                continue
        
        # Return summary message
        try:
            if failed_invites == 0:
                return f"All {successful_invites} users invited successfully"
            elif successful_invites == 0:
                return f"Failed to invite all {failed_invites} users"
            else:
                return f"Invited {successful_invites} users successfully, {failed_invites} failed. Failed users: {', '.join(failed_users)}"
        
        finally:
            if self.session:
                self.session.close()