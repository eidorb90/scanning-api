from sqlalchemy import Table, Column, Integer, ForeignKey, String
from auth.database import Base

client_clinic_association = Table(
    "client_clinic",
    Base.metadata,
    Column("client_id", Integer, ForeignKey("clients.id"), primary_key=True),
    Column("clinic_id", Integer, ForeignKey("clinics.id"), primary_key=True),
    extend_existing=True,
)

clinic_staff_association = Table(
    "clinic_staff",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("clinic_id", Integer, ForeignKey("clinics.id"), primary_key=True),
    Column("role", String(50), default="staff"),   # optional: "admin", "vet", etc.
)
