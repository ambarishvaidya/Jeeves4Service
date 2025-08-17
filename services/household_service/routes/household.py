from fastapi import APIRouter, Depends, HTTPException
from h11 import Request

from services.shared.request_context import RequestContext
from services.shared.j4s_utilities.jwt_helper import jwt_helper
from services.household_service.app.di.containers import ServiceFactory
from services.household_service.app.dto.household import AddHouseholdItemDTO, DeleteHouseholdItemDTO, HouseholdItemResponseDTO, SearchHouseholdItemResponseDTO, SearchHouseholdItemResponseDTO


router = APIRouter()

@router.post("/household/add", response_model=HouseholdItemResponseDTO)
async def add_household_item(request: AddHouseholdItemDTO, auth_token: dict = Depends(jwt_helper.verify_token)):
    try:
        add_item_service = ServiceFactory.get_add_item_service()
        response = add_item_service.add_household_item(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/household/find/{item}", response_model=SearchHouseholdItemResponseDTO)
async def find_household_item(item: str, auth_token: dict = Depends(jwt_helper.verify_token)):
    try:
        RequestContext.set_token(auth_token)
        find_item_service = ServiceFactory.get_find_item_service()
        response = find_item_service.find_household_item(item)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/household/remove/", response_model=HouseholdItemResponseDTO)
async def remove_household_item(request: DeleteHouseholdItemDTO, auth_token: dict = Depends(jwt_helper.verify_token)):
    try:
        remove_item_service = ServiceFactory.get_remove_item_service()
        response = remove_item_service.remove_item(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))