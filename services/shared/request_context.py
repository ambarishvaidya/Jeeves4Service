"""
Request Context Module

This module provides request-scoped context management using Python's ContextVar.
It allows storing and retrieving TokenPayload objects across the entire request 
lifecycle without passing parameters through method signatures.

The context is automatically isolated per request in async environments like FastAPI.
"""

from contextvars import ContextVar
from typing import Optional, TYPE_CHECKING
import logging

# Import TokenPayload for type hints only to avoid circular imports
if TYPE_CHECKING:
    from services.shared.j4s_utilities.token_models import TokenPayload

# Create context variable for request-scoped token data
auth_context: ContextVar[Optional['TokenPayload']] = ContextVar('auth_context', default=None)

# Logger for context operations
logger = logging.getLogger(__name__)


class RequestContext:
    """
    Request Context Manager
    
    Provides a simple API for managing request-scoped TokenPayload objects using ContextVar.
    Each request gets its own isolated context that travels through the entire call stack.
    """
    
    @staticmethod
    def set_token(payload: 'TokenPayload') -> None:
        """
        Set the token payload for the current request context.
        
        Args:
            payload (TokenPayload): The validated token payload object
        """
        auth_context.set(payload)
        if payload:
            logger.debug(f"Token set for user: {payload.username} (ID: {payload.user_id})")
    
    @staticmethod
    def get_token() -> Optional['TokenPayload']:
        """
        Get the token payload for the current request context.
        
        Returns:
            TokenPayload or None: Token payload object if available, None otherwise
        """
        return auth_context.get()


# Example usage:
"""
from services.shared.request_context import RequestContext
from services.shared.j4s_utilities.token_models import TokenPayload

# In your route handlers:
@router.get("/some-endpoint")
async def some_endpoint(current_user: TokenPayload = Depends(jwt_helper.verify_token)):
    RequestContext.set_token(current_user)
    # ... rest of your route logic

# In your service methods:
def some_service_method(self):
    current_user = RequestContext.get_token()
    if current_user:
        # Use TokenPayload methods for all operations
        user_id = current_user.user_id
        username = current_user.username
        is_admin = current_user.is_admin
        # ... etc
"""
