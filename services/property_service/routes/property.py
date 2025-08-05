from fastapi import APIRouter, HTTPException

from services.property_service.app.di.containers import ServiceFactory
from services.property_service.app.dto.property import (
    NewPropertyRequest,
    PropertyRoomRequest,
    RoomResponse, 
    UpdatePropertyRequest, 
    PropertyResponse
)

router = APIRouter()

@router.post("/property/add", response_model=PropertyResponse)
async def add_property(request: NewPropertyRequest) -> PropertyResponse:
    """Add a new property"""
    try:
        add_property_service = ServiceFactory.get_add_property_service()
        response = add_property_service.add_property(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/property/update", response_model=PropertyResponse)
async def update_property(request: UpdatePropertyRequest) -> PropertyResponse:
    """Update an existing property"""
    try:
        update_property_service = ServiceFactory.get_update_property_service()
        response = update_property_service.update_property(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("rooms/add", response_model=RoomResponse)
async def add_room(request: PropertyRoomRequest) -> RoomResponse:
    """Add a room to a property"""
    try:
        add_rooms_service = ServiceFactory.get_add_rooms_service()
        response = add_rooms_service.add_room(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))