# Import all models so SQLAlchemy can configure the mappers
from users.models import User, Client
from clinics.models import Clinic
from scanning.models import Scan, ScanParam, UserScan, ClinicScan, Mesh, MeshParam
from association import client_clinic_association, clinic_staff_association


# Optional: re-export them
__all__ = [
    "User",
    "Clinic",
    "Client",
    "Scan",
    "ScanParam",
    "UserScan",
    "ClinicScan",
    "Mesh",
    "MeshParam",
    "client_clinic_association",
    "clinic_staff_association",
]