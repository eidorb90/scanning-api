import asyncio
import os
import shutil
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi import (FastAPI, File, Form, HTTPException, Request, UploadFile,
                     status, Depends)
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.responses import RedirectResponse, HTMLResponse

from scanning.DogColmap import DogColmap
from basics.Queue import ScanQueue
from workers.Workers import ScanJob, ScanWorker
from auth.routes import router as auth_router
from users.routes import router as users_router
from scanning.routes import router as scanning_router
from ui.routes import router as ui_router
from users.models import User

from auth.dependencies import get_current_user
from scanning.routes import UPLOAD_DIR, SCANJOB_QUEUE

# ========== Globals =============


# ========== Work Manager =========
@asynccontextmanager
async def lifespan(app: FastAPI):
    scan_worker_instance = ScanWorker(SCANJOB_QUEUE)
    scan_worker = asyncio.create_task(scan_worker_instance.work())
    print("Scan Worker created:", scan_worker)

    yield

    scan_worker.cancel()
    await asyncio.gather(scan_worker, return_exceptions=True)


# =========== Setup ==============

app = FastAPI(lifespan=lifespan)
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(scanning_router, prefix="/scanning", tags=["scanning"])
app.include_router(ui_router, prefix="", tags=["ui"])

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount(
    "/view-scan/uploaded_videos",
    StaticFiles(directory="uploaded_videos"),
    name="uploaded_videos"
)
app.mount(
    "/view-mesh/uploaded_videos",
    StaticFiles(directory="uploaded_videos"),
    name="uploaded_videos"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://bigman.tailc9dd83.ts.net:8000/"], 
    allow_credentials=True,                 
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(UPLOAD_DIR, exist_ok=True)


class UserRegistration(BaseModel):
    username: str

@app.exception_handler(HTTPException)
async def redirect_unauthorized_to_login(request: Request, exc: HTTPException):
    # If a 401 occurs on a browser page route, redirect to login
    if exc.status_code == 401:
        return RedirectResponse(url="/login", status_code=303)
    return HTMLResponse(content=exc.detail, status_code=exc.status_code)


