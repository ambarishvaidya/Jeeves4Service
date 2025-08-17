"""Token payload models for JWT authentication."""
from pydantic import BaseModel
from typing import Optional, List
from services.shared.dto.property_shared import PropertyClaimDto


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
    properties: Optional[List[PropertyClaimDto]] = None  # User's property access
    
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
        is_admin: bool = False,
        properties: Optional[List[PropertyClaimDto]] = None
    ) -> 'TokenPayload':
        """
        Factory method for creating authentication payloads.
        Ensures all required fields for authentication are provided.
        """
        return cls(
            user_id=user_id,
            username=username,
            trace_id=trace_id,
            is_admin=is_admin,
            properties=properties or []
        )
    
    def has_property_access(self, property_id: int, required_level: str = "member") -> bool:
        """
        Check if user has access to a specific property.
        
        Args:
            property_id: The property ID to check
            required_level: Required access level ('guest', 'member', 'owner')
        
        Returns:
            bool: True if user has the required access level or higher
        """
        if not self.properties:
            return False
            
        access_hierarchy = {"guest": 1, "member": 2, "owner": 3}
        required_rank = access_hierarchy.get(required_level, 1)
        
        for prop in self.properties:
            if prop.property_id == property_id:
                user_rank = access_hierarchy.get(prop.access_level, 1)
                return user_rank >= required_rank
                
        return False
    
    def get_property_ids(self) -> List[int]:
        """Get list of property IDs the user has access to."""
        return [prop.property_id for prop in (self.properties or [])]

    def get_owned_property_ids(self) -> List[int]:
        """Get list of property IDs the user owns."""
        if not self.properties:
            return []
        return [prop.property_id for prop in self.properties if prop.access_level == "owner"]
