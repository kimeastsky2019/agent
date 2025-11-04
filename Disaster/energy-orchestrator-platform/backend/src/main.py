from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from src.config import settings
from src.database import engine, Base
from src.api.v1 import (
    auth, users, assets, devices, 
    energy, disasters, orchestrator, weather, demand, supply, digitaltwin
)

# Logging 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
# 프로덕션 환경에서는 API 문서 비활성화
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 초기화
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up application...")
    # 테이블 생성 (개발용, 프로덕션에서는 Alembic 사용)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application...")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}

@app.get("/ready")
async def readiness_check():
    """Readiness check - 데이터베이스 연결 상태 확인"""
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "not ready", "error": str(e)}
        )

@app.get('/api/energy/demand', tags=['Energy'])
async def get_energy_demand():
    """Get energy demand analysis data"""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            # Get summary from demand_analysis service
            try:
                response = await client.get('http://localhost:5002/api/summary', timeout=10.0)
                if response.status_code == 200:
                    return response.json()
                else:
                    return {'status': 'error', 'message': f'Demand analysis service returned {response.status_code}'}
            except httpx.ConnectError:
                # Try alternative addresses
                try:
                    response = await client.get('http://127.0.0.1:5002/api/summary', timeout=10.0)
                    if response.status_code == 200:
                        return response.json()
                except:
                    pass
                return {'status': 'error', 'message': 'Demand analysis service unavailable. Please check if the service is running on port 5002.'}
            except Exception as e:
                return {'status': 'error', 'message': f'Connection error: {str(e)}'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@app.get('/api/energy/demand/patterns', tags=['Energy'])
async def get_energy_demand_patterns():
    """Get energy demand time patterns"""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get('http://localhost:5002/api/patterns', timeout=10.0)
                if response.status_code == 200:
                    return response.json()
                else:
                    return {'status': 'error', 'message': f'Patterns service returned {response.status_code}'}
            except httpx.ConnectError:
                return {'status': 'error', 'message': 'Patterns service unavailable'}
            except Exception as e:
                return {'status': 'error', 'message': f'Error: {str(e)}'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@app.get('/api/energy/demand/heatmap', tags=['Energy'])
async def get_energy_demand_heatmap():
    """Get energy demand heatmap data"""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get('http://localhost:5002/api/heatmap', timeout=10.0)
                if response.status_code == 200:
                    return response.json()
                else:
                    return {'status': 'error', 'message': f'Heatmap service returned {response.status_code}'}
            except httpx.ConnectError:
                return {'status': 'error', 'message': 'Heatmap service unavailable'}
            except Exception as e:
                return {'status': 'error', 'message': f'Error: {str(e)}'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# API 라우터 등록
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(assets.router, prefix="/api/v1/assets", tags=["Assets"])
app.include_router(devices.router, prefix="/api/v1/devices", tags=["Devices"])
app.include_router(energy.router, prefix="/api/v1/energy", tags=["Energy"])
app.include_router(disasters.router, prefix="/api/v1/disasters", tags=["Disasters"])
app.include_router(weather.router, prefix="/api/v1/weather", tags=["Weather"])
app.include_router(demand.router, prefix="/api/v1/demand", tags=["Demand Analysis"])
app.include_router(supply.router, prefix="/api/v1/supply", tags=["Supply Analysis"])
app.include_router(digitaltwin.router, prefix="/api/v1/digitaltwin", tags=["Digital Twin"])
app.include_router(orchestrator.router, prefix="/api/v1/orchestrator", tags=["Orchestrator"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

