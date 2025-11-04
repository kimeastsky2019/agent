"""
가상 데이터 모듈
API 엔드포인트에서 사용할 가상 데이터를 제공합니다.
"""

import json
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import uuid

# 프로젝트 루트
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
MOCK_DATA_FILE = PROJECT_ROOT / "backend" / "data" / "mock" / "mock_data.json"

# 메모리 캐시
_mock_data_cache: Optional[Dict[str, Any]] = None

def load_mock_data() -> Dict[str, Any]:
    """가상 데이터 로드"""
    global _mock_data_cache
    
    if _mock_data_cache is not None:
        return _mock_data_cache
    
    # JSON 파일에서 로드
    if MOCK_DATA_FILE.exists():
        try:
            with open(MOCK_DATA_FILE, "r", encoding="utf-8") as f:
                _mock_data_cache = json.load(f)
                return _mock_data_cache
        except Exception as e:
            print(f"Warning: Could not load mock data from file: {e}")
    
    # 파일이 없으면 기본 데이터 생성
    _mock_data_cache = generate_default_mock_data()
    return _mock_data_cache

def generate_default_mock_data() -> Dict[str, Any]:
    """기본 가상 데이터 생성 (파일이 없을 때)"""
    assets = [
        {
            "id": "1",
            "name": "Solar Farm Tokyo",
            "type": "solar",
            "capacity_kw": 1000.0,
            "location": {"lat": 35.6762, "lon": 139.6503},
            "status": "online",
            "service_type": "supply",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": "2",
            "name": "Energy Demand Sector Tokyo",
            "type": "demand",
            "capacity_kw": 0.0,
            "location": {"lat": 35.6762, "lon": 139.6503},
            "status": "online",
            "service_type": "demand",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": "3",
            "name": "Wind Farm Osaka",
            "type": "wind",
            "capacity_kw": 2000.0,
            "location": {"lat": 34.6937, "lon": 135.5023},
            "status": "online",
            "service_type": "supply",
            "created_at": datetime.now().isoformat()
        }
    ]
    
    disasters = [
        {
            "id": "1",
            "event_type": "earthquake",
            "severity": 4,
            "location": {"lat": 35.6762, "lon": 139.6503},
            "affected_radius_km": 50.0,
            "start_time": (datetime.now() - timedelta(hours=12)).isoformat(),
            "end_time": None,
            "status": "active"
        }
    ]
    
    return {
        "assets": assets,
        "disasters": disasters,
        "energy_readings": [],
        "demand_data": [],
        "supply_data": []
    }

def get_assets() -> List[Dict[str, Any]]:
    """자산 목록 반환"""
    data = load_mock_data()
    return data.get("assets", [])

def get_asset(asset_id: str) -> Optional[Dict[str, Any]]:
    """특정 자산 반환"""
    assets = get_assets()
    return next((a for a in assets if a["id"] == asset_id), None)

def add_asset(asset: Dict[str, Any]) -> Dict[str, Any]:
    """자산 추가"""
    data = load_mock_data()
    if "assets" not in data:
        data["assets"] = []
    
    new_asset = {
        "id": str(uuid.uuid4()),
        **asset,
        "created_at": datetime.now().isoformat()
    }
    data["assets"].append(new_asset)
    save_mock_data(data)
    return new_asset

def delete_asset(asset_id: str) -> bool:
    """자산 삭제"""
    data = load_mock_data()
    if "assets" not in data:
        return False
    
    original_count = len(data["assets"])
    data["assets"] = [a for a in data["assets"] if a["id"] != asset_id]
    
    if len(data["assets"]) < original_count:
        save_mock_data(data)
        return True
    return False

def get_disasters() -> List[Dict[str, Any]]:
    """재난 목록 반환"""
    data = load_mock_data()
    return data.get("disasters", [])

def get_active_disasters() -> List[Dict[str, Any]]:
    """활성 재난 목록 반환"""
    disasters = get_disasters()
    return [d for d in disasters if d.get("status") == "active"]

def get_disaster(disaster_id: str) -> Optional[Dict[str, Any]]:
    """특정 재난 반환"""
    disasters = get_disasters()
    return next((d for d in disasters if d["id"] == disaster_id), None)

def get_energy_readings(
    device_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """에너지 측정값 반환"""
    data = load_mock_data()
    readings = data.get("energy_readings", [])
    
    # 필터링
    if device_id:
        readings = [r for r in readings if r.get("device_id") == device_id]
    
    if start_time:
        readings = [r for r in readings if datetime.fromisoformat(r["time"]) >= start_time]
    
    if end_time:
        readings = [r for r in readings if datetime.fromisoformat(r["time"]) <= end_time]
    
    return readings

def get_energy_balance() -> Dict[str, Any]:
    """에너지 밸런스 계산"""
    readings = get_energy_readings()
    now = datetime.now()
    recent_readings = [
        r for r in readings
        if (now - datetime.fromisoformat(r["time"])).total_seconds() < 3600  # 최근 1시간
    ]
    
    total_production = sum(
        r["value"] for r in recent_readings
        if r.get("metric_type") == "production"
    )
    
    total_consumption = sum(
        r["value"] for r in recent_readings
        if r.get("metric_type") == "consumption"
    )
    
    return {
        "total_production": round(total_production, 2),
        "total_consumption": round(total_consumption, 2),
        "balance": round(total_production - total_consumption, 2),
        "timestamp": now.isoformat()
    }

def get_demand_data(asset_id: str) -> List[Dict[str, Any]]:
    """수요 데이터 반환"""
    data = load_mock_data()
    demand_data = data.get("demand_data", [])
    return [d for d in demand_data if d.get("asset_id") == asset_id]

def get_supply_data(asset_id: str) -> List[Dict[str, Any]]:
    """공급 데이터 반환"""
    data = load_mock_data()
    supply_data = data.get("supply_data", [])
    return [d for d in supply_data if d.get("asset_id") == asset_id]

def save_mock_data(data: Dict[str, Any]):
    """가상 데이터 저장"""
    global _mock_data_cache
    
    # 디렉토리 생성
    MOCK_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # 파일 저장
    try:
        with open(MOCK_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        _mock_data_cache = data
    except Exception as e:
        print(f"Warning: Could not save mock data: {e}")




