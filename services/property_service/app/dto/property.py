from email import message
from token import OP
from pydantic import BaseModel
from typing import Optional, List


class NewPropertyRequest(BaseModel):
    name: str
    address: Optional[str] = None
    created_by: int

class UpdatePropertyRequest(BaseModel):
    property_id: int
    name: Optional[str] = None
    address: Optional[str] = None

class AddUsersPropertyRequest(BaseModel):
    property_id: int
    user_ids: List[int]

class PropertyRoomRequest(BaseModel):
    property_id: int
    room_name: str    

class UpdateRoomRequest(BaseModel):
    room_id: int
    room_name: str

class PropertyAssociationRequest(BaseModel):
    property_id: int
    user_id: int

class PropertyResponse(BaseModel):
    id: Optional[int] = None    
    name: Optional[str] = None
    address: Optional[str] = None
    message: Optional[str] = None

class RoomResponse(BaseModel):
    message: str
    room_id: Optional[int] = None    