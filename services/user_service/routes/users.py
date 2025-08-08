from fastapi import APIRouter, HTTPException, Response

from services.shared.j4s_jwt_lib.jwt_processor import JwtTokenProcessor
from services.user_service.app.di.containers import ServiceFactory
from services.user_service.app.dto.registration import RegisterUserResponse, RegisterUserRequest
from services.user_service.app.dto.user import AuthenticateUserResponse, ChangePasswordRequest, ChangePasswordResponse, InviteUser


router = APIRouter()

jwt_token = JwtTokenProcessor(
    issuer="http://jeeves4service",
    audience="http://jeeves4service",
    secret_key="J33v3s4s3rv1c3jeeves4service",
    expiry_milli_seconds=3600000
)


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
        payload = {
            "user_id": auth_response.user_id,
            "username": auth_response.email,
            "trace_id": auth_response.session_id
        }
        token = jwt_token.generate_token(payload)
        response.headers["Authorization"] = f"Bearer {token}"
        return auth_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/users/change-password", response_model=ChangePasswordResponse)
async def change_password(request: ChangePasswordRequest) -> ChangePasswordResponse:
    try:
        change_password_service = ServiceFactory.get_change_password_service()
        response = change_password_service.change_password(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))