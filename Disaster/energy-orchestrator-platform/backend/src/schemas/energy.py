from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EnergyReadingResponse(BaseModel):
    time: datetime
    device_id: str
    metric_type: str
    value: float
    unit: str

class EnergyBalanceResponse(BaseModel):
    total_production: float
    total_consumption: float
    balance: float
    timestamp: datetime






