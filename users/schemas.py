from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ---------------- User --------------

class UserBase(BaseModel):
    username: str
    phone: Optional[str] = None

class UserCreate(BaseModel):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_client: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# ----------------- Client ------------

class ClinicBase(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    notes: Optional[str] = None

class ClientCreate(ClinicBase):
    clinic_id: int

class Client(ClinicBase):
    id: int
    clinic_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


  