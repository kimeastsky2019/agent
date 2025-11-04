from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from src.database import get_db
from src.schemas.device import DeviceResponse

router = APIRouter()

@router.get("/", response_model=List[DeviceResponse])
async def get_devices(db: Session = Depends(get_db)):
    """IoT 디바이스 목록"""
    return []

@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: str, db: Session = Depends(get_db)):
    """IoT 디바이스 조회"""
    return {"id": device_id, "device_id": device_id, "device_type": "sensor", "status": "online"}




