from pydantic import BaseModel
from typing import Optional


class PropertyStorageRequest(BaseModel):
    property_id: int
    room_id: int
    container_id: int | None = None
    storage_name: str
   

class PropertyStorageResponse(BaseModel):
    message: Optional[str] = None
    id: Optional[int] = None
    property_id: Optional[int] = None
    room_id: Optional[int] = None
    container_id: Optional[int] = None
    storage_name: Optional[str] = None