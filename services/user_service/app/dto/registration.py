from pydantic import BaseModel, EmailStr
from datetime import date
from services.user_service.app.dto.user import AddUserRequest

class RegisterUserRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    dob: date
    additional_users: list[AddUserRequest] = [] 

class RegisterUserResponse(BaseModel):
    user_id: int
    message: str
