from pydantic import BaseModel

class ScanParams(BaseModel):
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


class MeshParams(BaseModel):
    scan_name: str
    trim: float
    pw: float
    depth: int