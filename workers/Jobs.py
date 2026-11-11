
from pydantic import BaseModel



class ScanJob(BaseModel):
    user_name: str
    file_name: str
    file_path: str
    frames_path: str
    sparse_path: str
    mesh_path: str
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
    frame_count: int