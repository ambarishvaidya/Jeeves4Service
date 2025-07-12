from pydantic import BaseModel, EmailStr

class AddUserRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    is_admin: bool = False



