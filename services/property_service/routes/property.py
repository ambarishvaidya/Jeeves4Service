from fastapi import APIRouter, HTTPException

from app.di.containers import ServiceFactory
from app.dto.property import (
    NewPropertyRequest, 
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
