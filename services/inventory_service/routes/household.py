from fastapi import APIRouter, Depends, HTTPException

from services.shared.j4s_utilities.jwt_helper import jwt_helper
from services.inventory_service.app.di.containers import ServiceFactory
from services.inventory_service.app.dto.household import AddHouseholdItemDTO, HouseholdItemResponseDTO


router = APIRouter()

@router.post("/household/add", response_model=HouseholdItemResponseDTO)
async def add_household_item(request: AddHouseholdItemDTO, auth_token: dict = Depends(jwt_helper.verify_token)):
    try:
        add_item_service = ServiceFactory.get_add_item_service()
        response = add_item_service.add_household_item(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

