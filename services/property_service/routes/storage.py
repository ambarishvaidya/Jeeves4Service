from fastapi import APIRouter, HTTPException

from services.property_service.app.di.containers import ServiceFactory
from services.property_service.app.dto.storage import (
    PropertyStorageRequest,
    PropertyStorageResponse
)

router = APIRouter()

@router.post("/storage/add-main-storage", response_model=PropertyStorageResponse)
async def add_main_storage(request: PropertyStorageRequest) -> PropertyStorageResponse:
    """Add main storage (container_id is None)"""
    try:
        # Ensure container_id is None for main storage
        if request.container_id is not None:
            raise HTTPException(
                status_code=400, 
                detail="Main storage cannot have a container_id. Use /storage/add-storage for sub-storage."
            )
        
        add_main_storage_service = ServiceFactory.get_add_main_storage_service()
        response = add_main_storage_service.add_main_storage(request)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/storage/add-storage", response_model=PropertyStorageResponse)
async def add_storage(request: PropertyStorageRequest) -> PropertyStorageResponse:
    """Add storage (container_id is required)"""
    try:
        # Ensure container_id is provided for regular storage
        if request.container_id is None:
            raise HTTPException(
                status_code=400, 
                detail="Storage requires a container_id. Use /storage/add-main-storage for main storage."
            )
        
        add_storage_service = ServiceFactory.get_add_storage_service()
        response = add_storage_service.add_storage(request)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
