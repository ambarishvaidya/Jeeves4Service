import re
import os
import logging
from fastapi import APIRouter, HTTPException, Depends, Response, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List

from services.shared.j4s_utilities.jwt_helper import jwt_helper
from services.shared.j4s_utilities.token_models import TokenPayload
from services.shared.j4s_jwt_lib.jwt_processor import JwtTokenProcessor
from services.shared.dto.property_shared import PropertyClaimDto, UserPropertiesResponseDto
from services.property_service.app.di.containers import ServiceFactory
from services.property_service.app.dto.property import (
    NewPropertyRequest,
    PropertyRoomRequest,
    RoomResponse, 
    UpdatePropertyRequest, 
    PropertyResponse
)

logger = logging.getLogger(__name__)

# Internal service authentication
INTERNAL_SERVICE_TOKEN = os.getenv("INTERNAL_SERVICE_TOKEN", "your-secure-internal-token-here")

def _validate_internal_token(token: str) -> bool:
    """Validate internal service authentication token."""
    return token == INTERNAL_SERVICE_TOKEN

def _log_internal_access(user_id: int, requester_ip: str):
    """Log internal service access for audit trail."""
    logger.info(f"Internal service access - User ID: {user_id}, IP: {requester_ip}")

router = APIRouter()

@router.post("/property/add", response_model=PropertyResponse)
async def add_property(request: NewPropertyRequest, auth_token: dict = Depends(jwt_helper.verify_token)) -> PropertyResponse:
    """Add a new property"""
    try:
        add_property_service = ServiceFactory.get_add_property_service()
        request.created_by = auth_token.user_id
        property_response = add_property_service.add_property(request)
        return property_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/property/update", response_model=PropertyResponse)
async def update_property(request: UpdatePropertyRequest, auth_token: dict = Depends(jwt_helper.verify_token)) -> PropertyResponse:
    """Update an existing property"""
    try:
        update_property_service = ServiceFactory.get_update_property_service()
        property_response = update_property_service.update_property(request)
        return property_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rooms/add", response_model=RoomResponse)
async def add_room(request: PropertyRoomRequest, auth_token: dict = Depends(jwt_helper.verify_token)) -> RoomResponse:
    """Add a room to a property"""
    try:
        add_rooms_service = ServiceFactory.get_add_rooms_service()
        room_response = add_rooms_service.add_room(request)
        return room_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/property/{property_id}", response_model=PropertyResponse)
async def get_property_by_id(property_id: int, auth_token: dict = Depends(jwt_helper.verify_token)) -> PropertyResponse:
    """Get a property by its ID"""
    try:
        get_property_service = ServiceFactory.get_get_property_service()
        property_response = get_property_service.get_property_by_id(property_id)
        if property_response is None:
            raise HTTPException(status_code=404, detail="Property not found")
        return property_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/internal/properties/users/{user_id}", response_model=UserPropertiesResponseDto)
async def get_user_properties_for_claims(
    user_id: int,
    request: Request,
    x_internal_token: str = Header(..., alias="X-Internal-Token")
) -> UserPropertiesResponseDto:
    """
    INTERNAL ENDPOINT - NOT FOR PUBLIC ACCESS
    Get properties associated with a user for JWT claims.
    This endpoint is used by other services to fetch property data.
    Requires internal service authentication token.
    """
    # Validate internal service token
    if not _validate_internal_token(x_internal_token):
        logger.warning(f"Invalid internal token access attempt from {request.client.host}")
        raise HTTPException(
            status_code=401, 
            detail="Invalid internal service token"
        )
    
    # Log internal access for audit trail
    _log_internal_access(user_id, request.client.host)
    try:
        get_property_service = ServiceFactory.get_get_property_service()
        properties = get_property_service.get_properties(user_id)
        
        # Convert to PropertyClaimDto format
        property_claims = []
        for prop in properties:
            # You'll need to determine access level logic based on your business rules
            # For now, assuming all associated properties give 'member' access
            property_claims.append(PropertyClaimDto(
                property_id=prop.id,
                property_name=prop.name,
                access_level="member"  # This should be determined by your business logic
            ))
        
        return UserPropertiesResponseDto(
            user_id=user_id,
            properties=property_claims,
            total_count=len(property_claims)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/properties/", response_model=list[PropertyResponse])
async def get_properties(auth_token: dict = Depends(jwt_helper.verify_token)) -> list[PropertyResponse]:
    """Get properties associated with a user"""
    try:
        get_property_service = ServiceFactory.get_get_property_service()
        property_response = get_property_service.get_properties(auth_token.user_id)
        return property_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rooms/property/{property_id}", response_model=list[RoomResponse])
async def get_rooms_by_property(property_id: int, auth_token: dict = Depends(jwt_helper.verify_token)) -> list[RoomResponse]:
    """Get all rooms for a specific property"""
    try:
        get_rooms_service = ServiceFactory.get_get_rooms_service()
        list_room_response = get_rooms_service.get_rooms_by_property(property_id)
        return list_room_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rooms/{room_id}", response_model=RoomResponse)
async def get_room_by_id(room_id: int, auth_token: dict = Depends(jwt_helper.verify_token)) -> RoomResponse:
    """Get a specific room by its ID"""
    try:
        get_rooms_service = ServiceFactory.get_get_rooms_service()
        room_response = get_rooms_service.get_room_by_id(room_id)
        if room_response is None:
            raise HTTPException(status_code=404, detail="Room not found")
        return room_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))