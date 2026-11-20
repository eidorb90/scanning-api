from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, ForeignKey, func, Table
from sqlalchemy.orm import relationship, declarative_base
from auth.database import Base
from association import client_clinic_association, clinic_staff_association

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class User(Base, TimestampMixin):
    """Regular app users (can download the app and make scans for fun)."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    first_name = Column(String(50), nullable=False, index=True)
    last_name = Column(String(50), nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=True)
    email = Column(String(100), index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_client = Column(Boolean, default=False, nullable=False)
    
    # type
    type = Column(String(50), nullable=False, default="user")

    # Clinics this user owns
    clinics = relationship("Clinic", back_populates="owner")
    # Clinics this user is staff of
    staff_clinics = relationship("Clinic", secondary=clinic_staff_association, back_populates="staff")
    # Scans this user created (personal scans)
    user_scans = relationship("UserScan", back_populates="user")




class Client(Base, TimestampMixin):
    """Clinic clients (patients). They don't create scans, but can view them."""
    __tablename__ = "clients"

    id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    notes = Column(String(500), nullable=True)

    clinics = relationship("Clinic", secondary=client_clinic_association, back_populates="clients")

    # Scans this client can view
    clinic_scans = relationship("ClinicScan", back_populates="client")
    __mapper_args__ = {
        "polymorphic_identity": "client",
    }


