from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class ClinicBase(BaseModel):
    name: str
    country: str
    city: str
    address: str
    zip: str
    phone: Optional[str] = None
    contact_email: EmailStr

class ClinicCreate(ClinicBase):
    pass 

class Clinic(ClinicBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 

