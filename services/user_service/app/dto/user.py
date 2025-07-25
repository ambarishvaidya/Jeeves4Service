from pydantic import BaseModel, EmailStr
from datetime import date

class InviteUser(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr    

class AddUserRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    dob: date
    is_admin: bool = False

class ChangePasswordRequest(BaseModel):
    user_id: int
    old_password: str
    new_password: str

class ChangePasswordResponse(BaseModel):
    user_id: int
    message: str

class CompleteRegistrationRequest(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: EmailStr
    dob: date
    old_password: str
    new_password: str

class CompleteRegistrationResponse(BaseModel):
    user_id: int
    message: str

class ActivateDeactivateUserRequest(BaseModel):
    user_id: int
    admin_id: int
    is_active: bool

class ActivateDeactivateUserResponse(BaseModel):
    user_id: int
    is_active: bool
    message: str

class AuthenticateUserResponse(BaseModel):
    session_id: str
    user_id: int
    email: EmailStr
    first_name: str
    last_name: str
    is_admin: bool    