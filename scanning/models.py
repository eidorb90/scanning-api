from pydantic import BaseModel

class ScanParams(BaseModel):
    mesh: bool
    max_distance: int
    frame_interval: int
    depth: int
    pw: float
    trim: float
    out_name: str

    
