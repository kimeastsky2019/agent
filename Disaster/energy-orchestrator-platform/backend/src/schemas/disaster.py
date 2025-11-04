from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from src.schemas.asset import Location

class DisasterResponse(BaseModel):
    id: str
    event_type: str
    severity: int
    location: Location
    affected_radius_km: Optional[float] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str
    
    class Config:
        from_attributes = True




