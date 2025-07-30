from email import message
from pydantic import BaseModel
from typing import Optional


class NewPropertyRequest(BaseModel):
    name: str
    address: Optional[str] = None
    created_by: int

class PropertyRoomRequest(BaseModel):
    property_id: int
    room_name: str    

class PropertyAssociationRequest(BaseModel):
    property_id: int
    user_id: int

class PropertyResponse(BaseModel):
    message: str    