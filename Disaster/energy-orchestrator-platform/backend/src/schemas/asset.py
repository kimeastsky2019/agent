from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class Location(BaseModel):
    lat: float
    lon: float

class AssetBase(BaseModel):
    name: str
    type: str
    capacity_kw: float
    location: Optional[Location] = None

class AssetCreate(AssetBase):
    organization_id: Optional[str] = None

class AssetResponse(AssetBase):
    id: str
    status: str
    service_type: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

