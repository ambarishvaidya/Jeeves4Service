from pydantic import BaseModel


class PropertyStorageRequest(BaseModel):
    property_id: int
    room_id: int
    storage_id: int | None = None
    storage_name: str
   

class PropertyStorageResponse(BaseModel):
    message: str