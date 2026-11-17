from pydantic import BaseModel
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, ForeignKey, func
from sqlalchemy.orm import relationship, declarative_base
from auth.database import Base
from users.models import TimestampMixin

class ScanParams(BaseModel):
    mesh: bool
    max_distance: int
    frame_interval: int
    max_num_feats: int
    peak_thresh: float
    estimate_shape: bool
    domain_pooling: bool
    depth: int
    pw: float
    trim: float
    out_name: str


class MeshParams(BaseModel):
    scan_name: str
    trim: float
    pw: float
    depth: int



class Scan(Base, TimestampMixin):
    """Base scan table (shared data)."""
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)

    # One-to-one with params
    params = relationship(
        "ScanParams",
        back_populates="scan",
        uselist=False,
        cascade="all, delete-orphan",
    )


class ScanParam(Base, TimestampMixin):
    __tablename__ = "scanparams"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), unique=True, nullable=False)

    user_name = Column(String(50), index=True)
    file_name = Column(String(255), index=True)
    file_path = Column(String(1000), unique=True)
    mesh_path = Column(String(1000), unique=True)
    max_distance = Column(Integer)
    frame_interval = Column(Integer)
    max_num_feats = Column(Integer)
    peak_thresh = Column(Float)
    estimate_shape = Column(Boolean, default=False)
    domain_pooling = Column(Boolean, default=False)
    depth = Column(Integer)
    pw = Column(Float)
    trim = Column(Float)
    out_name = Column(String(100))
    frame_count = Column(Integer)
    use_gpu = Column(Boolean, default=False)

    scan = relationship("Scan", back_populates="params")


class UserScan(Base, TimestampMixin):
    """Scans created by regular app users (not clinic-related)."""
    __tablename__ = "userscans"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    scan = relationship("Scan")
    user = relationship("User", back_populates="user_scans")


class ClinicScan(Base, TimestampMixin):
    """Scans that belong to a clinic and can be viewed by a client."""
    __tablename__ = "clinicscans"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), unique=True, nullable=False)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True, index=True)

    scan = relationship("Scan")
    clinic = relationship("Clinic", back_populates="clinic_scans")
    client = relationship("Client", back_populates="clinic_scans")