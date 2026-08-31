from pydantic import BaseModel, EmailStr
from datetime import date

class Contact(BaseModel):
    name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    additional_info: str | None = None