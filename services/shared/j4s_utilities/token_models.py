"""Token payload models for JWT authentication."""
from pydantic import BaseModel
from typing import Optional


class TokenPayload(BaseModel):
    """
    JWT Token Payload model for dual purpose:
    1. Creating tokens (during authentication)
    2. Consuming tokens (during route authorization)
    
    All fields except user_id are optional to allow flexible token creation
    while maintaining backward compatibility.
    """
    user_id: int                              # Required - core user identifier
    username: Optional[str] = None            # User's email/username
    trace_id: Optional[str] = None            # Session/trace identifier
    is_admin: Optional[bool] = False          # Admin privileges flag
    
    # Future extensibility - add new fields here as optional
    # organization_id: Optional[int] = None   # Multi-tenant support
    # permissions: Optional[List[str]] = None # Role-based permissions
    # session_id: Optional[str] = None        # Separate session tracking
    
    def to_dict(self) -> dict:
        """
        Convert to dictionary for JWT payload creation.
        Excludes None values to keep JWT payload clean.
        """
        return {k: v for k, v in self.dict().items() if v is not None}
    
    @classmethod
    def create_auth_payload(
        cls, 
        user_id: int, 
        username: str, 
        trace_id: str, 
        is_admin: bool = False
    ) -> 'TokenPayload':
        """
        Factory method for creating authentication payloads.
        Ensures all required fields for authentication are provided.
        """
        return cls(
            user_id=user_id,
            username=username,
            trace_id=trace_id,
            is_admin=is_admin
        )
