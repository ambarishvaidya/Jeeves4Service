import re
from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from services.shared.j4s_jwt_lib.jwt_processor import JwtTokenProcessor
from services.property_service.app.di.containers import ServiceFactory
from services.property_service.app.dto.property import (
    NewPropertyRequest,
    PropertyRoomRequest,
    RoomResponse, 
    UpdatePropertyRequest, 
    PropertyResponse
)

router = APIRouter()

jwt_token = JwtTokenProcessor(
    issuer="http://jeeves4service",
    audience="http://jeeves4service",
    secret_key="J33v3s4s3rv1c3jeeves4service",
    expiry_milli_seconds=3600000
)

security = HTTPBearer()

def verify_token(authorization: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = authorization.credentials
    try:
        payload = jwt_token.decode_token(token)
        if "error" in payload:
            raise HTTPException(
                status_code=401,
                detail=payload["error"],
                headers={"WWW-Authenticate": "Bearer"}
            )
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=401, 
            detail="Authorization header is missing",
            headers={"WWW-Authenticate": "Bearer"}
        )  

@router.post("/property/add", response_model=PropertyResponse)
async def add_property(request: NewPropertyRequest, auth_token: dict = Depends(verify_token)) -> PropertyResponse:
    """Add a new property"""
    try:
        add_property_service = ServiceFactory.get_add_property_service()
        request.user_id = auth_token.get("user_id")
        property_response = add_property_service.add_property(request)
        return property_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/property/update", response_model=PropertyResponse)
async def update_property(request: UpdatePropertyRequest, auth_token: dict = Depends(verify_token)) -> PropertyResponse:
    """Update an existing property"""
    try:
        update_property_service = ServiceFactory.get_update_property_service()
        request.user_id = auth_token.get("user_id")
        property_response = update_property_service.update_property(request)
        return property_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("rooms/add", response_model=RoomResponse)
async def add_room(request: PropertyRoomRequest, auth_token: dict = Depends(verify_token)) -> RoomResponse:
    """Add a room to a property"""
    try:
        add_rooms_service = ServiceFactory.get_add_rooms_service()
        request.user_id = auth_token.get("user_id")
        room_response = add_rooms_service.add_room(request)
        return room_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/property/{property_id}", response_model=PropertyResponse)
async def get_property_by_id(property_id: int, auth_token: dict = Depends(verify_token)) -> PropertyResponse:
    """Get a property by its ID"""
    try:
        get_property_service = ServiceFactory.get_get_property_service()
        property_response = get_property_service.get_property_by_id(property_id)
        if property_response is None:
            raise HTTPException(status_code=404, detail="Property not found")
        return property_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/properties/{user_id}", response_model=list[PropertyResponse])
async def get_properties(user_id: int, auth_token: dict = Depends(verify_token)) -> list[PropertyResponse]:
    """Get properties associated with a user"""
    try:
        get_property_service = ServiceFactory.get_get_property_service()
        property_response = get_property_service.get_properties(user_id)
        return property_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rooms/property/{property_id}", response_model=list[RoomResponse])
async def get_rooms_by_property(property_id: int, auth_token: dict = Depends(verify_token)) -> list[RoomResponse]:
    """Get all rooms for a specific property"""
    try:
        get_rooms_service = ServiceFactory.get_get_rooms_service()
        list_room_response = get_rooms_service.get_rooms_by_property(property_id)
        return list_room_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rooms/{room_id}", response_model=RoomResponse)
async def get_room_by_id(room_id: int, auth_token: dict = Depends(verify_token)) -> RoomResponse:
    """Get a specific room by its ID"""
    try:
        get_rooms_service = ServiceFactory.get_get_rooms_service()
        room_response = get_rooms_service.get_room_by_id(room_id)
        if room_response is None:
            raise HTTPException(status_code=404, detail="Room not found")
        return room_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))