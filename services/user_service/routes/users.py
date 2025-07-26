from ast import List
from urllib import request
from fastapi import APIRouter, HTTPException

from app.di.containers import ServiceFactory
from app.dto.registration import RegisterUserResponse, RegisterUserRequest
from app.dto.user import AuthenticateUserResponse, ChangePasswordRequest, ChangePasswordResponse, InviteUser


router = APIRouter()

@router.post("/users/register", response_model=RegisterUserResponse)
async def register_user(request: RegisterUserRequest) -> RegisterUserResponse:
    try:
        register_service = ServiceFactory.get_register_user_service()
        response = register_service.register_user(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/authenticate", response_model=AuthenticateUserResponse)
async def authenticate_user(email: str, password: str) -> AuthenticateUserResponse:
    try:
        auth_service = ServiceFactory.get_authenticate_user_service()
        response = auth_service.authenticate(email, password)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/users/change-password", response_model=ChangePasswordResponse)
async def change_password(request: ChangePasswordRequest) -> ChangePasswordResponse:
    try:
        change_password_service = ServiceFactory.get_change_password_service()
        change_password_service.change_password(request)
        return {"message": "Password changed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))