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

@app.get("/")
async def root():
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content="""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Energy Orchestrator Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Malgun Gothic", sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 0; }
        .top-header { background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); box-shadow: 0 2px 10px rgba(0,0,0,0.1); position: sticky; top: 0; z-index: 1000; padding: 15px 30px; }
        .top-header-content { max-width: 1400px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
        .logo { display: flex; align-items: center; gap: 12px; text-decoration: none; color: #667eea; font-weight: 700; font-size: 1.3rem; }
        .logo-icon { font-size: 1.8rem; }
        .nav-menu { display: flex; gap: 20px; align-items: center; }
        .nav-link { color: #333; text-decoration: none; font-weight: 500; padding: 8px 16px; border-radius: 8px; transition: all 0.3s ease; }
        .nav-link:hover { background: #667eea; color: white; }
        .home-link { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .home-link:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4); }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; color: white; margin-bottom: 40px; padding: 40px 0; }
        .header h1 { font-size: 3rem; margin-bottom: 15px; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); font-weight: 700; }
        .header p { font-size: 1.3rem; opacity: 0.95; }
        .status-badge { display: inline-block; background: rgba(76, 175, 80, 0.9); color: white; padding: 10px 20px; border-radius: 25px; font-size: 1rem; margin-top: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
        .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 25px; margin-top: 40px; }
        .card { background: white; border-radius: 16px; padding: 30px; box-shadow: 0 8px 24px rgba(0,0,0,0.15); transition: transform 0.3s ease, box-shadow 0.3s ease; text-decoration: none; color: inherit; display: block; position: relative; overflow: hidden; }
        .card::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #667eea, #764ba2); }
        .card:hover { transform: translateY(-5px); box-shadow: 0 12px 32px rgba(0,0,0,0.2); }
        .card-icon { font-size: 3.5rem; margin-bottom: 20px; display: block; }
        .card-title { font-size: 1.6rem; font-weight: 600; color: #333; margin-bottom: 12px; }
        .card-description { color: #666; font-size: 1rem; line-height: 1.6; }
        .info-section { background: rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 30px; margin-top: 40px; color: white; }
        .info-section h2 { font-size: 1.8rem; margin-bottom: 20px; }
        .info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; }
        .info-item { background: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 12px; }
        .info-item strong { display: block; margin-bottom: 8px; font-size: 1.1rem; }
    </style>
</head>
<body>
    <nav class="top-header">
        <div class="top-header-content">
            <a href="/eop" class="logo">
                <span class="logo-icon">⚡</span>
                <span>Energy Orchestrator Platform</span>
            </a>
            <div class="nav-menu">
                <a href="/eop" class="nav-link home-link">홈</a>
                <a href="/da" class="nav-link">Energy Demand</a>
                <a href="/sa" class="nav-link">Energy Supply</a>
                <a href="/assets" class="nav-link">Asset Management</a>
                <a href="/dashboard" class="nav-link">Disaster</a>
            </div>
        </div>
    </nav>
    <div class="container">
        <div class="header">
            <h1>⚡ Energy Orchestrator Platform</h1>
            <p>재난 대응 에너지 공유 네트워크</p>
            <div class="status-badge">✅ 서비스 운영 중</div>
        </div>
        <div class="dashboard-grid">
            <a href="/da" class="card"><span class="card-icon">📊</span><div class="card-title">Energy Demand</div><div class="card-description">에너지 수요 분석 및 예측</div></a>
            <a href="/sa" class="card"><span class="card-icon">⚡</span><div class="card-title">Energy Supply</div><div class="card-description">에너지 공급 분석 및 관리</div></a>
            <a href="/dtwin" class="card"><span class="card-icon">🌐</span><div class="card-title">Digital Twin</div><div class="card-description">디지털 트윈 시뮬레이션</div></a>
            <a href="/weather" class="card"><span class="card-icon">🌤️</span><div class="card-title">Weather</div><div class="card-description">날씨 분석 및 예측</div></a>
            <a href="/ontology" class="card"><span class="card-icon">🔗</span><div class="card-title">Ontology Service</div><div class="card-description">지식 그래프 서비스</div></a>
            <a href="http://localhost:3010" class="card" target="_blank"><span class="card-icon">🤝</span><div class="card-title">Collaborative Ontology</div><div class="card-description">협업형 온톨로지 플랫폼</div></a>
            <a href="/ibs" class="card"><span class="card-icon">📡</span><div class="card-title">Image Broadcasting</div><div class="card-description">영상 모니터링 서비스</div></a>
            <a href="/assets" class="card"><span class="card-icon">📦</span><div class="card-title">Asset Management</div><div class="card-description">자산 관리 시스템</div></a>
            <a href="/dashboard" class="card"><span class="card-icon">🎛️</span><div class="card-title">Disaster</div><div class="card-description">재난 대비</div></a>
        </div>
        <div class="info-section">
            <h2>📋 시스템 정보</h2>
            <div class="info-grid">
                <div class="info-item"><strong>서비스</strong><span>Energy Orchestrator Platform</span></div>
                <div class="info-item"><strong>버전</strong><span>1.0.0</span></div>
                <div class="info-item"><strong>상태</strong><span>Operational</span></div>
                <div class="info-item"><strong>API</strong><span>/api/v1</span></div>
            </div>
        </div>
    </div>
    <script>async function loadSystemStatus(){try{const response=await fetch("/eop/health");const data=await response.json();console.log("System status:",data);}catch(err){console.error("Failed to load system status:",err);}}document.addEventListener("DOMContentLoaded",function(){loadSystemStatus();});</script>
</body>
</html>""")

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

@app.get('/api/collaborative-ontology/health', tags=['Collaborative Ontology'])
async def get_collaborative_ontology_health():
    """Get collaborative ontology service health status"""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f'{settings.COLLABORATIVE_ONTOLOGY_URL}/health', timeout=10.0)
                if response.status_code == 200:
                    return response.json()
                else:
                    return {'status': 'error', 'message': f'Collaborative ontology service returned {response.status_code}'}
            except httpx.ConnectError:
                return {'status': 'error', 'message': 'Collaborative ontology service unavailable'}
            except Exception as e:
                return {'status': 'error', 'message': f'Error: {str(e)}'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@app.get('/api/collaborative-ontology', tags=['Collaborative Ontology'])
async def get_collaborative_ontology_info():
    """Get collaborative ontology service information"""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f'{settings.COLLABORATIVE_ONTOLOGY_URL}/', timeout=10.0)
                if response.status_code == 200:
                    return response.json()
                else:
                    return {'status': 'error', 'message': f'Collaborative ontology service returned {response.status_code}'}
            except httpx.ConnectError:
                return {'status': 'error', 'message': 'Collaborative ontology service unavailable'}
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

