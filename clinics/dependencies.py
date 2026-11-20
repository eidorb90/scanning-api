from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from .models import Clinic
from users.models import User, Client
from auth.database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_clinic(db: Session, clinic_name: str):
    return db.query(Clinic).filter(Clinic.Clinicname == clinic_name).first()

def get_user_clinics(db: Session, user: User):
    return db.query(Clinic).filter(Clinic.owner_id == user.id).all()

def get_clinics_where_user_is_client(db: Session, user: User):
    client = db.query(Client).filter(Client.id == user.id).first()
    if not client:
        return []
       
    return client.clinics