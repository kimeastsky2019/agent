from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from src.database import get_db
from src.services.supply_analysis_service import SupplyAnalysisService

router = APIRouter()

@router.get("/analysis/{asset_id}")
async def get_supply_analysis(
    asset_id: str,
    db: Session = Depends(get_db)
):
    """에너지 공급 분석 결과 조회"""
    try:
        service = SupplyAnalysisService(asset_id=asset_id)
        analysis = await service.analyze_supply()
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/realtime/{asset_id}")
async def get_realtime_power(
    asset_id: str,
    range: str = Query("hour", regex="^(hour|day|month|year)$"),
    db: Session = Depends(get_db)
):
    """실시간 전력 데이터 조회"""
    try:
        service = SupplyAnalysisService(asset_id=asset_id)
        data = await service.get_realtime_power(range_type=range)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast/{asset_id}")
async def get_production_forecast(
    asset_id: str,
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """생산량 예측 조회"""
    try:
        service = SupplyAnalysisService(asset_id=asset_id)
        forecast = await service.forecast_production(days=days)
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/anomalies/{asset_id}")
async def get_anomalies(
    asset_id: str,
    db: Session = Depends(get_db)
):
    """이상 탐지 결과 조회"""
    try:
        service = SupplyAnalysisService(asset_id=asset_id)
        anomalies = await service.detect_anomalies()
        return anomalies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/facility/{asset_id}")
async def get_facility_info(
    asset_id: str,
    db: Session = Depends(get_db)
):
    """시설 정보 조회"""
    try:
        service = SupplyAnalysisService(asset_id=asset_id)
        facility = await service.get_facility_info()
        return facility
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/{asset_id}")
async def get_supply_dashboard(
    asset_id: str,
    db: Session = Depends(get_db)
):
    """공급 분석 대시보드 데이터 조회"""
    try:
        service = SupplyAnalysisService(asset_id=asset_id)
        analysis = await service.analyze_supply()
        
        return {
            'asset_id': asset_id,
            'dashboard_url': f'/supply-analysis/{asset_id}',
            'analysis': analysis,
            'status': 'active'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




