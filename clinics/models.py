from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, ForeignKey, func, Table
from sqlalchemy.orm import relationship
from auth.database import Base
from users.models import TimestampMixin, Client
from association import client_clinic_association, clinic_staff_association

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
    clients = relationship("Client", secondary=client_clinic_association, back_populates="clinics")
    # Scans belonging to this clinic
    clinic_scans = relationship("ClinicScan", back_populates="clinic")

    invitations = relationship("ClinicInvitation", back_populates="clinic")
    staff_invitations = relationship("ClinicStaffInvitation", back_populates="clinic")

    # clinic staff members
    staff = relationship("User", secondary=clinic_staff_association, back_populates="staff_clinics")

class ClinicInvitation(Base, TimestampMixin):
    __tablename__ = "clinicinvitations"

    id = Column(Integer, primary_key=True, index=True)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=False)

    email = Column(String(100), nullable=False, index=True)

    token = Column(String(64), unique=True, nullable=False)

    accepted = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    clinic = relationship("Clinic", back_populates="invitations")


class ClinicStaffInvitation(Base, TimestampMixin):
    __tablename__ = "staffinvitations"

    id = Column(Integer, primary_key=True, index=True)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=False)

    email = Column(String(100), nullable=False, index=True)

    token = Column(String(64), unique=True, nullable=False)

    accepted = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    clinic = relationship("Clinic", back_populates="staff_invitations")
 