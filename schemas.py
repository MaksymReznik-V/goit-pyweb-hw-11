from pydantic import BaseModel, EmailStr
from datetime import date

class Contact(BaseModel):
    name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    additional_info: str | None = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr

    model_config = {'from_attributes': True}

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str