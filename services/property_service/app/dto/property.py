from email import message
from pydantic import BaseModel


class PropertyRequest(BaseModel):
    name: str
    address: str
    created_by: int

class PropertyRoomRequest(BaseModel):
    property_id: int
    room_name: str    

class PropertyAssociationRequest(BaseModel):
    property_id: int
    user_id: int

class PropertyResponse(BaseModel):
    message: str    