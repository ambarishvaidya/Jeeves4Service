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
    
@router.get("/property/{property_id}", response_model=PropertyResponse)
async def get_property_by_id(property_id: int) -> PropertyResponse:
    """Get a property by its ID"""
    try:
        get_property_service = ServiceFactory.get_get_property_service()
        response = get_property_service.get_property_by_id(property_id)
        if response is None:
            raise HTTPException(status_code=404, detail="Property not found")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/properties/{user_id}", response_model=list[PropertyResponse])
async def get_properties(user_id: int) -> list[PropertyResponse]:
    """Get properties associated with a user"""
    try:
        get_property_service = ServiceFactory.get_get_property_service()
        response = get_property_service.get_properties(user_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rooms/property/{property_id}", response_model=list[RoomResponse])
async def get_rooms_by_property(property_id: int) -> list[RoomResponse]:
    """Get all rooms for a specific property"""
    try:
        get_rooms_service = ServiceFactory.get_get_rooms_service()
        response = get_rooms_service.get_rooms_by_property(property_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rooms/{room_id}", response_model=RoomResponse)
async def get_room_by_id(room_id: int) -> RoomResponse:
    """Get a specific room by its ID"""
    try:
        get_rooms_service = ServiceFactory.get_get_rooms_service()
        response = get_rooms_service.get_room_by_id(room_id)
        if response is None:
            raise HTTPException(status_code=404, detail="Room not found")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))