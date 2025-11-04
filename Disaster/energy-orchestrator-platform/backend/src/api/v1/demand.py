from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
from src.database import get_db
from src.services.demand_analysis_service import DemandAnalysisService
import pandas as pd
import io

router = APIRouter()

@router.get("/analysis/{asset_id}")
async def get_demand_analysis(asset_id: str, db: Session = Depends(get_db)):
    """에너지 수요 분석 결과 조회"""
    try:
        service = DemandAnalysisService(asset_id=asset_id)
        analysis = await service.analyze_demand()
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analysis/{asset_id}/analyze")
async def analyze_demand(
    asset_id: str,
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """에너지 수요 분석 실행"""
    try:
        service = DemandAnalysisService(asset_id=asset_id)
        
        if file:
            # CSV 파일 업로드 시
            contents = await file.read()
            df = pd.read_csv(io.BytesIO(contents))
            analysis = await service.analyze_demand(data=df)
        else:
            # 기존 데이터 사용
            analysis = await service.analyze_demand()
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/{asset_id}")
async def get_demand_dashboard(asset_id: str, db: Session = Depends(get_db)):
    """수요 분석 대시보드 데이터 조회"""
    try:
        service = DemandAnalysisService(asset_id=asset_id)
        analysis = await service.analyze_demand()
        
        return {
            'asset_id': asset_id,
            'dashboard_url': f'/demand-analysis/{asset_id}',
            'analysis': analysis,
            'status': 'active'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/api/energy/demand', tags=['Energy'])
async def get_energy_demand():
    """Get energy demand analysis data"""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            # Get summary from demand_analysis service
            response = await client.get('http://localhost:5002/api/summary', timeout=10.0)
            if response.status_code == 200:
                return response.json()
            else:
                return {'status': 'error', 'message': 'Demand analysis service unavailable'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@router.get('/api/energy/demand/patterns', tags=['Energy'])
async def get_energy_demand_patterns():
    """Get energy demand time patterns"""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get('http://localhost:5002/api/patterns', timeout=10.0)
            if response.status_code == 200:
                return response.json()
            else:
                return {'status': 'error', 'message': 'Patterns not available'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@router.get('/api/energy/demand/heatmap', tags=['Energy'])
async def get_energy_demand_heatmap():
    """Get energy demand heatmap data"""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get('http://localhost:5002/api/heatmap', timeout=10.0)
            if response.status_code == 200:
                return response.json()
            else:
                return {'status': 'error', 'message': 'Heatmap not available'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}





