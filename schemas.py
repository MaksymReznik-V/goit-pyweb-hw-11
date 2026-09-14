from pydantic import BaseModel, EmailStr, ConfigDict
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
    is_verified: bool

    model_config = ConfigDict(
        from_attributes=True
    )

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str