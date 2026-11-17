from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, ForeignKey, func
from sqlalchemy.orm import relationship, declarative_base
from auth.database import Base


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
    phone = Column(String(20), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_client = Column(Boolean, default=False, nullable=False)

    # Clinics this user owns
    clinics = relationship("Clinic", back_populates="owner")
    # Scans this user created (personal scans)
    user_scans = relationship("UserScan", back_populates="user")




class Client(Base, TimestampMixin):
    """Clinic clients (patients). They don't create scans, but can view them."""
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False, index=True)
    last_name = Column(String(50), nullable=False, index=True)
    phone = Column(String(20), index=True)
    email = Column(String(100), index=True)
    notes = Column(String(1000), nullable=True)

    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=False, index=True)
    clinic = relationship("Clinic", back_populates="clients")

    # Scans this client can view
    clinic_scans = relationship("ClinicScan", back_populates="client")


