from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from workers.Jobs import ScanJob
from basics.Queue import ScanQueue
from pathlib import Path

from fastapi.responses import FileResponse, HTMLResponse
from auth.dependencies import get_current_user
import shutil
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from users.models import User
from .models import ScanParams, MeshParams
from .utils import get_video_frames
from scanning.DogColmap import DogColmap
import os


UPLOAD_DIR = "uploaded_videos"

SCANJOB_QUEUE = ScanQueue()

router = APIRouter()

@router.post("/upload-video/", status_code=status.HTTP_201_CREATED)
async def upload_video(current_user: User = Depends(get_current_user), file: UploadFile = File(...)):
    username = current_user.username
    print(f"Uploading video for {username}")
    if file.content_type is None:
        return
    if not file.content_type.startswith("video/"):
        print("ERROR UPLOADING FILE: File provided is not a valid video format.")
        return

    file_path = os.path.join(f"{UPLOAD_DIR}/{username}/{file.filename}", file.filename)

    os.makedirs(f"{UPLOAD_DIR}/{username}/{file.filename}")
    html_string = f"""
    <p>Successfully added uploaded Video for {current_user.username} <p/>
    """
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        html_string = f"""
                <p>An Error occured while uploading video {e}<p/>
                """
 
    finally:
        await file.close()

    return HTMLResponse(html_string)



@router.post("/start-scan/")
async def start_scan(scan_params: ScanParams = Form(), current_user: User = Depends(get_current_user), file_name: str = Form(...)):
    try:
        user_name = current_user.username

        frames_path = f"{UPLOAD_DIR}/{user_name}/{file_name}/out/frames"
        sparse_path = f"{UPLOAD_DIR}/{user_name}/{file_name}/out"
        mesh_path = f"{UPLOAD_DIR}/{user_name}/mesh/"
        file_path = f"{UPLOAD_DIR}/{user_name}/{file_name}/{file_name}"

        frame_count = get_video_frames(file_path, scan_params.frame_interval)
        new_scan_job = ScanJob(
            out_name = scan_params.out_name,
            mesh = scan_params.mesh,
            max_distance = scan_params.max_distance,
            frame_interval = scan_params.frame_interval,
            max_num_feats = scan_params.max_num_feats,
            peak_thresh = scan_params.peak_thresh,
            estimate_shape = scan_params.estimate_shape,
            domain_pooling = scan_params.domain_pooling,
            depth = scan_params.depth,
            pw = scan_params.pw,
            trim = scan_params.trim,
            user_name=str(user_name),
            file_name=file_name,
            file_path=file_path,
            frames_path=frames_path,
            sparse_path=sparse_path,
            mesh_path=mesh_path,
            frame_count=int(frame_count),
        )



        SCANJOB_QUEUE.enqueue(new_scan_job)
        return HTMLResponse(f"""
            <p>You are a position {SCANJOB_QUEUE.length()} in the Queue </p>
            <p>Please refresh Estimated time to finish is {SCANJOB_QUEUE.estimated_wait(SCANJOB_QUEUE.length())} minutes </p>
            """)
    except Exception as e:
        return HTMLResponse(f"""
        <p> An error occured {e} </p>
        """)

@router.get("/download-scan/")
async def download_scan(file_name: str, current_user: User = Depends(get_current_user)):
    user_name = current_user.username
    ply_dir = (Path(UPLOAD_DIR) / user_name / "ply").resolve()
    path = (ply_dir / f"{file_name}.ply").resolve()
    if ply_dir not in path.parents or not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    return FileResponse(path, media_type="application/octet-stream", filename=path.name)


@router.get("/get-scans/", response_class=HTMLResponse)
async def get_scans(current_user: User = Depends(get_current_user)):
    user_name = current_user.username
    user_scan_path = Path(f"{UPLOAD_DIR}/{user_name}/ply")
    files = [f for f in user_scan_path.iterdir() if f.is_file()]
    if files is None:
        return HTMLResponse("You dont have any scans yet")

    items = "".join(f"<li> {f.name} <a href='/view-scan/?scan_name={f.name}' >View</a> </li>" for f in files)
    return HTMLResponse("<ul>" + items + "</ul>")

@router.get("/get-uploaded-videos/", response_class=HTMLResponse)
async def get_uploaded_videos(current_user: User = Depends(get_current_user)):
    user_name = current_user.username
    user_video_path = Path(f"{UPLOAD_DIR}/{user_name}")

    video_dirs = [d for d in user_video_path.iterdir() if d.is_dir()]

    if video_dirs is None:
        return HTMLResponse("You dont have any uploaded vidoes yet")
    
  
    itmes = "".join(f"<li> {d.name} </li>" for d in video_dirs if d.name != "ply" and d.name != "mesh")
    return HTMLResponse("<ul>" + itmes + "</ul>")


@router.get("/get-meshes/", response_class=HTMLResponse)
async def get_meshes(current_user: User = Depends(get_current_user)):
    user_name = current_user.username
    user_scan_path = Path(f"{UPLOAD_DIR}/{user_name}/mesh")
    files = [f for f in user_scan_path.iterdir() if f.is_file()]
    if files is None:
        return HTMLResponse("You dont have any meshes yet")

    items = "".join(f"<li> {f.name} <a href='/view-mesh/?mesh_name={f.name}' >View</a> </li>" for f in files)
    return HTMLResponse("<ul>" + items + "</ul>")

@router.post("/mesh-scan/", response_class=HTMLResponse)
async def mesh_scan(mesh_params: MeshParams = Form(), current_user: User = Depends(get_current_user)):
    try:
        dc = DogColmap("", current_user.username, "", "", "", "", "", "", "")
        trim = mesh_params.trim
        pw = mesh_params.pw
        depth = mesh_params.depth
        dc.set_trim(trim)
        dc.set_pw(pw)
        dc.set_depth(depth)
        ply_path = f"{UPLOAD_DIR}/{current_user.username}/ply/{mesh_params.scan_name}"
        mesh_path = f"{UPLOAD_DIR}/{current_user.username}/mesh/{mesh_params.scan_name}"
        dc.mesh_poisson(ply_path, mesh_path)
        return HTMLResponse(f"""
            <p>Mesh Saved to {mesh_path}</p>
            """) 
    except Exception as e:
        return HTMLResponse(f"""
                    <p>Error Occured {e}</p>
                    """)
    
@router.post("/remesh-scan/", response_class=HTMLResponse)
async def remesh_scan(mesh_params: MeshParams = Form(), current_user: User = Depends(get_current_user)):
    try:
        dc = DogColmap("", current_user.username, "", "", "", "", "", "", "")
        trim = mesh_params.trim
        pw = mesh_params.pw
        depth = mesh_params.depth
        dc.set_trim(trim)
        dc.set_pw(pw)
        dc.set_depth(depth)
        ply_path = f"{UPLOAD_DIR}/{current_user.username}/ply/{mesh_params.scan_name}"
        mesh_path = f"{UPLOAD_DIR}/{current_user.username}/mesh/{mesh_params.scan_name}"
        dc.mesh_poisson(ply_path, mesh_path)
        return HTMLResponse(f"""
            <p>Mesh Updated to {mesh_path}</p>
            """) 
    except Exception as e:
        return HTMLResponse(f"""
                    <p>Error Occured {e}</p>
                    """)

@router.delete("/delete-scan/", response_class=HTMLResponse)
async def delete_scan(scan_name: str, current_user: User = Depends(get_current_user)):
    try:
        scan_to_remove =  f"{UPLOAD_DIR}/{current_user.username}/ply/{scan_name}"
        os.remove(scan_to_remove)

        return HTMLResponse(f"""
            <p>Sucessfully deleted {scan_name} </p>
            """)
    except Exception as e:
        return HTMLResponse(f"""
            <p> Error Occured {e} </p>
            """)

    
@router.delete("/delete-mesh/", response_class=HTMLResponse)
async def delete_mesh(mesh_name: str, current_user: User = Depends(get_current_user)):
    try:
        mesh_to_remove = f"{UPLOAD_DIR}/{current_user.username}/mesh/{mesh_name}"
        os.remove(mesh_to_remove)

        return HTMLResponse(f"""
            <p>Sucessfully deleted {mesh_name} </p>
            """)
    except Exception as e:
        return HTMLResponse(f"""
            <p> Error Occured {e} </p>
            """)

    




