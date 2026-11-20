from sqlalchemy.orm import Session
from .models import User, Client
from clinics.models import Clinic

def make_user_into_client(db: Session, user_id: int, email: str, clinic_id: int = None): # type: ignore
    """Adds the user as a cleint for a specificed clinic"""
    user = db.query(User).filter(User.id == user_id, User.email == email).first()
    if not user:
        raise ValueError("User not Found")
    
    existing_client = db.query(Client).filter(Client.id == user.id).first()

    if existing_client: 
        return existing_client
    
    client = Client(
        id=user.id,
        nodes="",
    )

    if clinic_id:
        clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()
        if clinic:
            client.clinics.append(clinic)

    db.add(client)
    db.commit()
    db.refresh(client)
    return client


