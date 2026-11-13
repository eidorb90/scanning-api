from fastapi import APIRouter, Depends, HTTPException, status, Request
from pathlib import Path
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from users.models import User
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from auth.dependencies import get_current_user
from scanning.routes import UPLOAD_DIR
from fastapi.templating import Jinja2Templates
import os


router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, current_user: User = Depends(get_current_user)):
    username = current_user.username

    (Path(UPLOAD_DIR) / username / "ply").mkdir(parents=True, exist_ok=True)
    return templates.TemplateResponse(
        request,
        name="home.html",
        context={"request": request, "title": "Home Page", "username": username},
    )

@router.get("/scans/", response_class=HTMLResponse)
async def scans(request: Request, current_user: User = Depends(get_current_user)):
    username = current_user.username

    return templates.TemplateResponse(
        request,
        name="scans.html",
        context={"request": request, "title": "Scans", "username": username},
    )

@router.get("/meshes/", response_class=HTMLResponse)
async def meshes(request: Request, current_user: User = Depends(get_current_user)):
    username = current_user.username

    return templates.TemplateResponse(
        request,
        name="meshes.html",
        context={"request": request, "title": "Meshes", "username": username},
    )

@router.get("/videos/", response_class=HTMLResponse)
async def videos(request: Request, current_user: User = Depends(get_current_user)):
    username = current_user.username

    return templates.TemplateResponse(
        request,
        name="videos.html",
        context={"request": request, "title": "Videos", "username": username},
    )
    
@router.get("/new-scan/", response_class=HTMLResponse)
async def new_scan(request: Request, current_user: User = Depends(get_current_user)):
    username = current_user.username

    return templates.TemplateResponse(
        request,
        name="new-scan.html",
        context={"request": request, "title": "New Scan", "username": username},
    )

@router.get("/login/", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse(
        request, 
        name="login.html",
        context={"request": request, "title": "Login"}
    )

@router.get("/signup/", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse(
        request,
        name="signup.html",
        context={"request": request, "title": "Signup"}

    )

@router.get("/view-scan/", response_class=HTMLResponse)
async def view_scan(request: Request, scan_name: str, current_user: User = Depends(get_current_user)):
    scan_path = f"{UPLOAD_DIR}/{current_user.username}/ply/{scan_name}"
    return templates.TemplateResponse(
        request, 
        name="view-scan.html",
        context={"request": request, "title": f"View - {scan_name}", "scan_name": scan_name, "scan_path": scan_path}
    )

@router.get("/view-mesh/", response_class=HTMLResponse)
async def view_mesh(request: Request, mesh_name: str, current_user: User = Depends(get_current_user)):
    scan_path = f"{UPLOAD_DIR}/{current_user.username}/mesh/{mesh_name}"
    return templates.TemplateResponse(
        request, 
        name="view-mesh.html",
        context={"request": request, "title": f"View - {mesh_name}", "scan_name": mesh_name, "scan_path": scan_path}
    )

