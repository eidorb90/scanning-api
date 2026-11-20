from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ---------------- User ----------------
class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    username: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 


# ---------------- Client ----------------
class ClientBase(BaseModel):
    email: Optional[EmailStr] = None
    notes: Optional[str] = None


class ClientCreate(UserCreate, ClientBase):
    """Creating a client requires both User fields + Client fields."""
    clinic_id: int


class ClientUpdate(UserUpdate, ClientBase):
    clinic_id: Optional[int] = None


class Client(User, ClientBase):
    """Response model: a Client is a User + extra fields."""
    clinic_id: int
