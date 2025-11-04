from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.database import get_db
from src.schemas.disaster import DisasterResponse
from src.data.mock_data import get_disasters, get_active_disasters, get_disaster as get_mock_disaster

router = APIRouter()

@router.get("/", response_model=List[DisasterResponse])
async def get_disasters_endpoint(db: Session = Depends(get_db)):
    """재난 목록"""
    return get_disasters()

@router.get("/active", response_model=List[DisasterResponse])
async def get_active_disasters_endpoint(db: Session = Depends(get_db)):
    """활성 재난 목록"""
    return get_active_disasters()

@router.get("/{disaster_id}", response_model=DisasterResponse)
async def get_disaster_endpoint(disaster_id: str, db: Session = Depends(get_db)):
    """재난 조회"""
    disaster = get_mock_disaster(disaster_id)
    if not disaster:
        raise HTTPException(status_code=404, detail="Disaster not found")
    return disaster

