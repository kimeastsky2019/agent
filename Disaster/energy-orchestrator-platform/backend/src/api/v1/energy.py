from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from src.database import get_db
from src.schemas.energy import EnergyReadingResponse, EnergyBalanceResponse
from src.data.mock_data import get_energy_readings, get_energy_balance

router = APIRouter()

@router.get("/production", response_model=List[EnergyReadingResponse])
async def get_production(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """에너지 생산량 조회"""
    readings = get_energy_readings(start_time=start_time, end_time=end_time)
    return [r for r in readings if r.get("metric_type") == "production"]

@router.get("/consumption", response_model=List[EnergyReadingResponse])
async def get_consumption(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """에너지 소비량 조회"""
    readings = get_energy_readings(start_time=start_time, end_time=end_time)
    return [r for r in readings if r.get("metric_type") == "consumption"]

@router.get("/balance", response_model=EnergyBalanceResponse)
async def get_balance(db: Session = Depends(get_db)):
    """에너지 밸런스"""
    balance = get_energy_balance()
    return balance

@router.get("/forecast")
async def get_forecast(db: Session = Depends(get_db)):
    """에너지 예측"""
    return {"forecast": []}

