from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import APIRouter, HTTPException, Response, Depends, Header
from typing import Optional

from h11 import Request
from yaml import Token

from services.shared.request_context import RequestContext
from services.shared.j4s_utilities.jwt_helper import jwt_helper
from services.shared.j4s_utilities.token_models import TokenPayload
from services.shared.j4s_jwt_lib.jwt_processor import JwtTokenProcessor
from services.shared.clients.property_service_client import property_client
from services.user_service.app.di.containers import ServiceFactory
from services.user_service.app.dto.registration import RegisterUserResponse, RegisterUserRequest
from services.user_service.app.dto.user import AuthenticateUserResponse, ChangePasswordRequest, ChangePasswordResponse, InviteUser


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
async def authenticate_user(email: str, password: str, response: Response) -> AuthenticateUserResponse:
    try:
        auth_service = ServiceFactory.get_authenticate_user_service()
        auth_response = auth_service.authenticate(email, password)
        
        # Fetch user's properties for JWT claims
        user_properties = property_client.get_user_properties_sync(auth_response.user_id)
        
        payload = TokenPayload(
            user_id=auth_response.user_id,
            username=auth_response.email,
            trace_id=auth_response.session_id,
            is_admin=auth_response.is_admin,
            properties=user_properties
        )
        token = jwt_helper.generate_token(payload)
        RequestContext.set_token(payload)
        response.headers["Authorization"] = f"Bearer {token}"
        return auth_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/users/change-password", response_model=ChangePasswordResponse)
async def change_password( request: ChangePasswordRequest, auth_token: dict = Depends(jwt_helper.verify_token) ) -> ChangePasswordResponse:
    try:
        
        change_password_service = ServiceFactory.get_change_password_service()
        request.user_id = auth_token.user_id
        response = change_password_service.change_password(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))