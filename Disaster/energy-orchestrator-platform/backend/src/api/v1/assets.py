from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.database import get_db
from src.schemas.asset import AssetResponse, AssetCreate
from src.data.mock_data import get_assets, get_asset, add_asset, delete_asset as delete_mock_asset

router = APIRouter()

@router.get("/", response_model=List[AssetResponse])
async def get_assets_endpoint(db: Session = Depends(get_db)):
    """에너지 자산 목록"""
    return get_assets()

@router.post("/", response_model=AssetResponse)
async def create_asset(asset: AssetCreate, db: Session = Depends(get_db)):
    """에너지 자산 생성"""
    asset_dict = {
        "name": asset.name,
        "type": asset.type,
        "capacity_kw": asset.capacity_kw or 0.0,
        "location": asset.location.model_dump() if asset.location else {"lat": 0.0, "lon": 0.0},
        "status": "online",
        "service_type": "demand" if asset.type == "demand" else "supply",
        "organization_id": asset.organization_id
    }
    return add_asset(asset_dict)

@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset_endpoint(asset_id: str, db: Session = Depends(get_db)):
    """에너지 자산 조회"""
    asset = get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@router.delete("/{asset_id}")
async def delete_asset_endpoint(asset_id: str, db: Session = Depends(get_db)):
    """에너지 자산 삭제"""
    if not delete_mock_asset(asset_id):
        raise HTTPException(status_code=404, detail="Asset not found")
    return {"message": "Asset deleted successfully"}

