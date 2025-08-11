from datetime import date
from typing import Optional
from pydantic import BaseModel

from services.property_service.routes import storage


class AddHouseholdItemDTO(BaseModel):
    product_name: Optional[str] = None
    general_name: str
    quantity: Optional[int] = 1
    storage_id: int
    property_id: int

class UpdateHouseholdItemDTO(BaseModel):
    id: int
    product_name: Optional[str] = None
    general_name: str
    quantity: Optional[int] = 1
    storage_id: int
    property_id: int

class HouseholdItemResponseDTO(BaseModel):
    msg: Optional[str] = None
    err: Optional[str] = None
    is_success: bool

class DeleteHouseholdItemDTO(BaseModel):
    id: int

class DeleteHouseholdItemResponseDTO(BaseModel):
    success: bool
    message: Optional[str] = None

class SearchHouseholdItemDTO(BaseModel):
    property_id: int
    search_product: str

class HouseholdItemDTO(BaseModel):
    product_name: Optional[str] = None
    general_name: str
    quantity: Optional[int] = 1
    storage_id: int
    property_id: int
    location: str

class SearchHouseholdItemResponseDTO(BaseModel):
    items: list[HouseholdItemDTO] = []