from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.database import get_db
from src.schemas.user import UserResponse

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    """사용자 목록"""
    return []

@router.get("/me", response_model=UserResponse)
async def get_current_user():
    """현재 사용자 정보"""
    return {"id": "1", "email": "test@example.com", "full_name": "Test User"}










