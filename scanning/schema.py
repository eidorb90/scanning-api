
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional



class ScanParamBase(BaseModel):
    user_name: Optional[str] = None
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    mesh_path: Optional[str] = None
    max_distance: Optional[int] = None
    frame_interval: Optional[int] = None
    max_num_feats: Optional[int] = None
    peak_thresh: Optional[float] = None
    estimate_shape: bool = False
    domain_pooling: bool = False
    depth: Optional[int] = None
    pw: Optional[float] = None
    trim: Optional[float] = None
    out_name: Optional[str] = None
    frame_count: Optional[int] = None
    use_gpu: bool = False


class ScanParamCreate(ScanParamBase):
    pass


class ScanParamUpdate(ScanParamBase):
    pass


class ScanParam(ScanParamBase):
    id: int
    scan_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScanBase(BaseModel):
    name: str = Field(..., max_length=100)


class ScanCreate(ScanBase):
    params: Optional[ScanParamCreate] = None


class ScanUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    params: Optional[ScanParamUpdate] = None


class Scan(ScanBase):
    id: int
    params: Optional[ScanParam] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserScanBase(BaseModel):
    pass


class UserScanCreate(UserScanBase):
    user_id: int
    scan: ScanCreate


class UserScan(UserScanBase):
    id: int
    scan_id: int
    user_id: int
    scan: Scan
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ClinicScanBase(BaseModel):
    pass


class ClinicScanCreate(ClinicScanBase):
    clinic_id: int
    client_id: Optional[int] = None
    scan: ScanCreate


class ClinicScan(ClinicScanBase):
    id: int
    scan_id: int
    clinic_id: int
    client_id: Optional[int] = None
    scan: Scan
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScanWithParams(Scan):
    """Alias / clearer name for responses that include params"""
    pass


class UserScanOut(UserScan):
    pass


class ClinicScanOut(ClinicScan):
    pass