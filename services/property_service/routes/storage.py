from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from services.shared.j4s_jwt_lib.jwt_processor import JwtTokenProcessor
from services.property_service.app.di.containers import ServiceFactory
from services.property_service.app.dto.storage import (
    PropertyStorageRequest,
    PropertyStorageResponse
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


router = APIRouter()

@router.post("/storage/add-main-storage", response_model=PropertyStorageResponse)
async def add_main_storage(request: PropertyStorageRequest, auth_token: dict = Depends(verify_token)) -> PropertyStorageResponse:
    """Add main storage (container_id is None)"""
    try:
        # Ensure container_id is None for main storage
        if request.container_id is not None:
            raise HTTPException(
                status_code=400, 
                detail="Main storage cannot have a container_id. Use /storage/add-storage for sub-storage."
            )
        
        add_main_storage_service = ServiceFactory.get_add_main_storage_service()
        request.user_id = auth_token.get("user_id")
        response = add_main_storage_service.add_main_storage(request)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/storage/add-storage", response_model=PropertyStorageResponse)
async def add_storage(request: PropertyStorageRequest, auth_token: dict = Depends(verify_token)) -> PropertyStorageResponse:
    """Add storage (container_id is required)"""
    try:
        # Ensure container_id is provided for regular storage
        if request.container_id is None:
            raise HTTPException(
                status_code=400, 
                detail="Storage requires a container_id. Use /storage/add-main-storage for main storage."
            )
        
        add_storage_service = ServiceFactory.get_add_storage_service()
        request.user_id = auth_token.get("user_id")
        response = add_storage_service.add_storage(request)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/storage/property/{property_id}", response_model=list[PropertyStorageResponse])
async def get_storage_by_property(property_id: int, auth_token: dict = Depends(verify_token)) -> list[PropertyStorageResponse]:
    """Get all storage for a specific property"""
    try:
        get_storage_service = ServiceFactory.get_get_storage_service()
        response = get_storage_service.get_storage_by_property(property_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/storage/room/{room_id}", response_model=list[PropertyStorageResponse])
async def get_storage_by_room(room_id: int, auth_token: dict = Depends(verify_token)) -> list[PropertyStorageResponse]:
    """Get all storage for a specific room"""
    try:
        get_storage_service = ServiceFactory.get_get_storage_service()
        response = get_storage_service.get_storage_by_room(room_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/storage/{storage_id}", response_model=PropertyStorageResponse)
async def get_storage_by_id(storage_id: int, auth_token: dict = Depends(verify_token)) -> PropertyStorageResponse:
    """Get a specific storage by its ID"""
    try:
        get_storage_service = ServiceFactory.get_get_storage_service()
        response = get_storage_service.get_storage_by_id(storage_id)
        if response is None:
            raise HTTPException(status_code=404, detail="Storage not found")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
