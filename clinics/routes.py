from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse
from auth.dependencies import get_current_user, get_db
from sqlalchemy.orm import Session
from users.models import User, Client
from .models import Clinic, ClinicInvitation, ClinicStaffInvitation
from .dependencies import get_clinic as db_get_clinic
from .dependencies import get_user_clinics
from .schemas import ClinicCreate
from typing import Annotated
from users.utils import make_user_into_client
import os
import secrets
from datetime import datetime, timedelta, timezone

router = APIRouter()
@router.post("/create/")
def create_clinic(clinic: Annotated[ClinicCreate, Form()], user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a clinic"""
    clinic.name = clinic.name.lower()

    # TODO make sure to finish more validation checks on phone and email
    db_clinc = db_get_clinic(db, clinic_name=clinic.name)
    if db_clinc:
        raise HTTPException(status_code=400, detail="Clinc with that name already registerd")

    db_clinc = Clinic(name=clinic.name, country=clinic.country, city=clinic.city, address=clinic.address, zip=clinic.zip, phone=clinic.phone, contact_email=clinic.contact_email, owner_id=user.id, owner=user)

    clinic_dir = os.path.join("uploaded_videos", "clinics", clinic.name)
    os.makedirs(clinic_dir, exist_ok=True)

    return HTMLResponse(f"""
        <div class="alert alert-ok", role="status">
            <p>Clinic Creation Successful.</p>
        </div>
        """)



@router.get("/my-clinics/")
def get_my_clinics(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get the Clinics where the user is an owner"""
    user_clinics = get_user_clinics(db, user)

    if not user_clinics:
        raise HTTPException(status_code=200, detail="You dont own any clinics")

    clinics_html_string = "".join(f"<li>{clinic.name}</li>" for clinic in user_clinics)

    return HTMLResponse(f"""
        {clinics_html_string}
        """)

    
@router.get("/client-clinics/")
def get_clinics_where_im_client(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get the Clinics where the current user is a client"""
    client = db.query(Client).filter(Client.id == user.id).first()
    
    if not client:
        raise HTTPException(status_code=404, detail="There is not client with this user id")
    
    clinics = db.query(Clinic).filter(Clinic.clients.any(Client.id == client.id)).all()

    clinics_html_string = "".join(f"<li>{clinic.name}</li>" for clinic in clinics)

    return HTMLResponse(f"""
        {clinics_html_string}                
        """)

@router.get("/accept-staff-invite/")
def join_clinic_as_staff(token: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Allows for users to accept staff inviations"""
    invite = db.query(ClinicStaffInvitation).filter(ClinicStaffInvitation.token == token, ClinicStaffInvitation.accepted==False).first()
    if not invite or (invite.expires_at and invite.expires_at < datetime.now(timezone.utc)): # type: ignore
        raise HTTPException(status_code=400, detail="Invalid or expired invite")

    if user.email and user.email.lower() != invite.email: # type: ignore
        raise HTTPException(status_code=403, detail="Invite is for a differnt email") 

    clinic = db.query(Clinic).filter(Clinic.id == invite.clinic_id).first()
    if clinic:
        clinic.staff.append(user)
   

    invite.accepted = True # type: ignore
    db.commit()
    return HTMLResponse(f"""
        <p>Invite Successfully Accepted</p>
        """)


@router.post("/invite-staff/")
def invite_as_staff(clinic_id: int, email: str,  user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Allows a clinic to invite users to be clients of their clinic"""
    if clinic_id not in user.clinics:
        raise HTTPException(status_code=401, detail="Current user does not own the clinic")

    token = secrets.token_urlsafe(32)

    invitation = ClinicStaffInvitation(
        clinic_id=clinic_id,
        email=email.lower(),
        token=token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db.add(invitation)
    db.commit()

    return HTMLResponse(f"""
        <p>User with email : {email} was invited to be a staff memeber</p>        
        """)


@router.post("/remove-staff/")
def remove_staff_memeber(clinic_id: int, email: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    clinic = db.query(Clinic).filter(Clinic.id==clinic_id).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Cannot find clinic")


    user_to_remove = db.query(User).filter(User.email==email.lower).first() 
    if not user_to_remove:
        raise HTTPException(status_code=404, detail="Cannot find user")

    if clinic_id not in user.clinics:
        raise HTTPException(status_code=401, detail="You cannot remove staff members of a clinic you dont own")

    
    if user_to_remove not in clinic.staff:
        raise HTTPException(status_code=404, detail="User with this email is not a staff memeber of this clinic")
    
    clinic.staff.remove(user_to_remove)
    db.commit()
    return HTMLResponse(f"""
        <p>Staff Member removed successfully</p>             
        """)
    
@router.post("/remove-client/")
def remove_client(clinic_id: int, email: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    clinic = db.query(Clinic).filter(Clinic.id==clinic_id).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Cannot find clinic")

    client_to_remove = db.query(Client).filter(Client.email==email.lower).first()
    if not client_to_remove:
        HTTPException(status_code=404, detail="Cannot find user")

    if client_to_remove not in clinic.clients:
        raise HTTPException(status_code=404, detail="User with this email is not a client of this clinic")
 
    if clinic_id not in user.clinics:
        raise HTTPException(status_code=401, detail="You cannot remove clients of a clinic you dont own")
    
   
    clinic.staff.remove(client_to_remove)
    db.commit()
    return HTMLResponse(f"""
        <p>Client removed successfully</p>             
        """)

@router.get("/accept-client-invite/")
def join_clinic(token: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Allows the user to accept invites from clinics"""
    invite = db.query(ClinicInvitaion).filter(ClinicInvitaion.token == token, ClinicInvitaion.accepted==False).first()
    if not invite or (invite.expires_at and invite.expires_at < datetime.now(timezone.utc)): # type: ignore
        raise HTTPException(status_code=400, detail="Invalid or expired invite")

    if user.email and user.email.lower() != invite.email: # type: ignore
        raise HTTPException(status_code=403, detail="Invite is for a differnt email") 
    
    client = make_user_into_client(db, user.id, email=invite.email, clinic_id=invite.clinic_id) # type: ignore

    invite.accepted = True # type: ignore
    db.commit()
    return HTMLResponse(f"""
        <p>Invite Successfully Accepted</p>
        """)


router.post("/invite-client/")
def invite_to_clinic(clinic_id: int, email: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Allows a clinic to invite users to be clients of their clinic"""
    if clinic_id not in user.clinics or clinic_id not in user.staff_clinics:
        raise HTTPException(status_code=401, detail="Current user does not own the clinic")

    token = secrets.token_urlsafe(32)

    invitation = ClinicInvitaion(
        clinic_id=clinic_id,
        email=email.lower(),
        token=token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db.add(invitation)
    db.commit()

    return HTMLResponse(f"""
        <p>User with email : {email} was invited </p>        
        """)


router.get("/client-scans/")
def get_client_scans(clinic_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Gets the cleints scans for a clinic"""
    if clinic_id not in user.clinics or clinic_id not in user.staff_clinics:
        raise HTTPException(status_code=401, detail="Current user is not a staff memeber or owner of the clinic")
    
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()

    client_scans_html = ""
    if clinic:
        client_scans_html = "".join(f"<li>{scan.params.file_name}</li>" for scan in clinic.clinic_scans)


    return HTMLResponse(f"""
        {client_scans_html}    
        """)

