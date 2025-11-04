from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DeviceResponse(BaseModel):
    id: str
    device_id: str
    device_type: str
    status: str
    last_seen: Optional[datetime] = None
    
    class Config:
        from_attributes = True




