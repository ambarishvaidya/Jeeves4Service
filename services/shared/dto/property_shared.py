"""Shared Property DTOs for cross-service communication."""
from pydantic import BaseModel
from typing import List, Optional


class PropertyClaimDto(BaseModel):
    """
    Lightweight property information for JWT claims.
    Contains only essential data needed for authorization decisions.
    """
    property_id: int
    property_name: str
    access_level: str  # 'owner', 'member', 'guest', etc.
    
    
class PropertyMetadataDto(BaseModel):
    """
    Extended property metadata for cross-service requests.
    Used when services need more property details.
    """
    id: int
    name: str
    address: Optional[str] = None
    created_by: Optional[int] = None
    
    
class PropertyAssociationDto(BaseModel):
    """
    User-property relationship information.
    """
    property_id: int
    user_id: int
    property_name: str
    access_level: str = "member"  # Can be extended with roles
    

class UserPropertiesResponseDto(BaseModel):
    """
    Response containing all properties associated with a user.
    """
    user_id: int
    properties: List[PropertyClaimDto]
    total_count: int
