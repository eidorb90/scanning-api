from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, ForeignKey, func
from sqlalchemy.orm import relationship, declarative_base
from auth.database import Base
from users.models import TimestampMixin

class Clinic(Base, TimestampMixin):
    __tablename__ = "clinics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    country = Column(String(50), nullable=False, index=True)
    city = Column(String(50), nullable=False, index=True)
    address = Column(String(255), nullable=False)
    zip = Column(String(20), nullable=False, index=True)
    phone = Column(String(20), unique=True)
    contact_email = Column(String(100), unique=True, index=True, nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    owner = relationship("User", back_populates="clinics")

    # Clients of this clinic
    clients = relationship("Client", back_populates="clinic")
    # Scans belonging to this clinic
    clinic_scans = relationship("ClinicScan", back_populates="clinic")
