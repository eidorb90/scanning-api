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


class ScanParams(Base, TimestampMixin):
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