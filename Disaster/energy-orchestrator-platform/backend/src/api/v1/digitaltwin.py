from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import asyncio
import json
import logging

from src.database import get_db
from src.services.digitaltwin_service import DigitalTwinService

router = APIRouter()
logger = logging.getLogger(__name__)

# 디지털 트윈 인스턴스 관리 (asset_id별)
twin_instances: dict = {}

@router.get("/state/{asset_id}")
async def get_digital_twin_state(asset_id: str, db: Session = Depends(get_db)):
    """디지털 트윈 현재 상태 조회"""
    try:
        if asset_id not in twin_instances:
            twin_instances[asset_id] = DigitalTwinService(asset_id)
            await twin_instances[asset_id].initialize()
        
        service = twin_instances[asset_id]
        state = await service.get_current_state()
        return state
    except Exception as e:
        logger.error(f"Error getting digital twin state: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/initialize/{asset_id}")
async def initialize_digital_twin(asset_id: str, db: Session = Depends(get_db)):
    """디지털 트윈 초기화"""
    try:
        service = DigitalTwinService(asset_id)
        initialized = await service.initialize()
        
        if initialized:
            twin_instances[asset_id] = service
        
        return {
            "asset_id": asset_id,
            "initialized": initialized,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error initializing digital twin: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cycle/{asset_id}")
async def run_control_cycle(asset_id: str, db: Session = Depends(get_db)):
    """제어 사이클 실행"""
    try:
        if asset_id not in twin_instances:
            twin_instances[asset_id] = DigitalTwinService(asset_id)
            await twin_instances[asset_id].initialize()
        
        service = twin_instances[asset_id]
        result = await service.run_control_cycle()
        return result
    except Exception as e:
        logger.error(f"Error running control cycle: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/{asset_id}")
async def get_performance_metrics(asset_id: str, db: Session = Depends(get_db)):
    """성능 지표 조회"""
    try:
        if asset_id not in twin_instances:
            twin_instances[asset_id] = DigitalTwinService(asset_id)
            await twin_instances[asset_id].initialize()
        
        service = twin_instances[asset_id]
        metrics = await service.get_performance_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/stream/{asset_id}")
async def websocket_stream(websocket: WebSocket, asset_id: str):
    """WebSocket을 통한 실시간 시뮬레이션 스트림"""
    await websocket.accept()
    
    try:
        if asset_id not in twin_instances:
            twin_instances[asset_id] = DigitalTwinService(asset_id)
            await twin_instances[asset_id].initialize()
        
        service = twin_instances[asset_id]
        
        # 실시간 스트림 시작
        async for data in service.run_simulation_stream(duration_hours=24, time_step_minutes=15):
            await websocket.send_json(data)
            await asyncio.sleep(0.1)  # 100ms 간격
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for asset {asset_id}")
    except Exception as e:
        logger.error(f"Error in WebSocket stream: {e}")
        await websocket.close()

@router.get("/simulation/{asset_id}")
async def start_simulation(
    asset_id: str,
    duration_hours: int = 24,
    time_step_minutes: int = 15,
    db: Session = Depends(get_db)
):
    """시뮬레이션 시작"""
    try:
        if asset_id not in twin_instances:
            twin_instances[asset_id] = DigitalTwinService(asset_id)
            await twin_instances[asset_id].initialize()
        
        service = twin_instances[asset_id]
        
        # 첫 번째 사이클 실행
        result = await service.run_control_cycle()
        
        return {
            "asset_id": asset_id,
            "duration_hours": duration_hours,
            "time_step_minutes": time_step_minutes,
            "result": result,
            "status": "running"
        }
    except Exception as e:
        logger.error(f"Error starting simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))




