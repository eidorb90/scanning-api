from fastapi import APIRouter, Depends, HTTPException, status, Response, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .dependencies import get_db, authenticate_user, get_user
from .utils import create_access_token 
from .schemas import UserCreate, UserResponse
from users.models import User
from .utils import get_password_hash
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Annotated
import os


router = APIRouter()


@router.post("/token/")
def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return HTMLResponse("""
            <div class="alert alert-bad" role="alert">
            <p>Invalid username or password. Try again.</p>
            </div>
        """)


    
    access_token = create_access_token(data={"sub":user.username})

    html = HTMLResponse("""
        <div class="alert alert-ok" role="status">
            <p>Login successful. Taking you home.</p>
            <meta http-equiv="refresh" content="3;url=/" />
        </div>
        """)
    html.set_cookie(
        key="authToken",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7200
    )
    return html
    
    
@router.post("/signup/")
def signup(user: Annotated[UserCreate, Form()], db: Session = Depends(get_db)):
    db_user = get_user(db, username = user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registerd")

    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    user_dir = os.path.join("uploaded_videos", user.username)
    os.makedirs(user_dir, exist_ok=True)
    os.makedirs(f"{user_dir}/ply", exist_ok=True)

    return HTMLResponse("""
        <div class="alert alert-ok" role="status">
            <p>Signup successful. Taking you to log in.</p>
            <meta http-equiv="refresh" content="3;url=/login/" />
        </div>
        """)

@router.post("/logout/")
async def logout(response: Response):
    response.delete_cookie(key="authToken")
    return RedirectResponse(url="/login/", status_code=303) 