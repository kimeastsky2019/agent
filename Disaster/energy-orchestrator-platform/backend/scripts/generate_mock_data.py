"""
가상 데이터 생성 스크립트
전체 서비스가 작동하도록 다양한 가상 데이터를 생성합니다.
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

# 가상 데이터 저장소
mock_data = {
    "assets": [],
    "disasters": [],
    "energy_readings": [],
    "demand_data": [],
    "supply_data": []
}

def generate_assets() -> List[Dict[str, Any]]:
    """에너지 자산 생성"""
    asset_types = [
        {"type": "solar", "service_type": "supply", "capacity_range": (500, 5000)},
        {"type": "wind", "service_type": "supply", "capacity_range": (1000, 3000)},
        {"type": "battery", "service_type": "storage", "capacity_range": (200, 1000)},
        {"type": "demand", "service_type": "demand", "capacity_range": (0, 0)},
    ]
    
    locations = [
        {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503},
        {"name": "Osaka", "lat": 34.6937, "lon": 135.5023},
        {"name": "Yokohama", "lat": 35.4437, "lon": 139.6380},
        {"name": "Nagoya", "lat": 35.1815, "lon": 136.9066},
        {"name": "Fukuoka", "lat": 33.5904, "lon": 130.4017},
    ]
    
    assets = []
    
    for i, asset_type_info in enumerate(asset_types):
        for j in range(2):  # 각 타입당 2개씩
            location = random.choice(locations)
            capacity = random.uniform(*asset_type_info["capacity_range"])
            
            asset = {
                "id": str(uuid.uuid4()),
                "name": f"{asset_type_info['type'].capitalize()} Farm {location['name']} {i+1}-{j+1}",
                "type": asset_type_info["type"],
                "capacity_kw": round(capacity, 2),
                "location": {
                    "lat": location["lat"] + random.uniform(-0.1, 0.1),
                    "lon": location["lon"] + random.uniform(-0.1, 0.1)
                },
                "status": random.choice(["online", "online", "online", "maintenance"]),  # 대부분 online
                "service_type": asset_type_info["service_type"],
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                "organization_id": f"org_{random.randint(1, 3)}"
            }
            assets.append(asset)
    
    # 수요 섹터 추가
    for location in locations[:3]:
        asset = {
            "id": str(uuid.uuid4()),
            "name": f"Energy Demand Sector {location['name']}",
            "type": "demand",
            "capacity_kw": 0.0,
            "location": {
                "lat": location["lat"],
                "lon": location["lon"]
            },
            "status": "online",
            "service_type": "demand",
            "created_at": (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat(),
            "organization_id": f"org_{random.randint(1, 3)}"
        }
        assets.append(asset)
    
    return assets

def generate_disasters() -> List[Dict[str, Any]]:
    """재난 데이터 생성"""
    disaster_types = [
        {"event_type": "earthquake", "severity_range": (3, 7), "radius_range": (10, 100)},
        {"event_type": "typhoon", "severity_range": (2, 5), "radius_range": (50, 200)},
        {"event_type": "flood", "severity_range": (1, 4), "radius_range": (5, 50)},
        {"event_type": "wildfire", "severity_range": (2, 5), "radius_range": (20, 150)},
    ]
    
    locations = [
        {"lat": 35.6762, "lon": 139.6503},
        {"lat": 34.6937, "lon": 135.5023},
        {"lat": 35.4437, "lon": 139.6380},
    ]
    
    disasters = []
    
    # 활성 재난 (최근 발생)
    for i in range(3):
        disaster_type = random.choice(disaster_types)
        location = random.choice(locations)
        start_time = datetime.now() - timedelta(hours=random.randint(1, 48))
        
        disaster = {
            "id": str(uuid.uuid4()),
            "event_type": disaster_type["event_type"],
            "severity": random.randint(*disaster_type["severity_range"]),
            "location": {
                "lat": location["lat"] + random.uniform(-0.5, 0.5),
                "lon": location["lon"] + random.uniform(-0.5, 0.5)
            },
            "affected_radius_km": round(random.uniform(*disaster_type["radius_range"]), 2),
            "start_time": start_time.isoformat(),
            "end_time": None,  # 활성 재난
            "status": "active"
        }
        disasters.append(disaster)
    
    # 과거 재난 (최근 30일)
    for i in range(5):
        disaster_type = random.choice(disaster_types)
        location = random.choice(locations)
        start_time = datetime.now() - timedelta(days=random.randint(1, 30))
        end_time = start_time + timedelta(hours=random.randint(12, 72))
        
        disaster = {
            "id": str(uuid.uuid4()),
            "event_type": disaster_type["event_type"],
            "severity": random.randint(*disaster_type["severity_range"]),
            "location": {
                "lat": location["lat"] + random.uniform(-0.5, 0.5),
                "lon": location["lon"] + random.uniform(-0.5, 0.5)
            },
            "affected_radius_km": round(random.uniform(*disaster_type["radius_range"]), 2),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "status": "resolved"
        }
        disasters.append(disaster)
    
    return disasters

def generate_energy_readings(assets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """에너지 측정값 생성"""
    readings = []
    now = datetime.now()
    
    for asset in assets:
        if asset["service_type"] == "supply":
            # 공급 자산: 생산 데이터
            for i in range(24):  # 최근 24시간
                time = now - timedelta(hours=23-i)
                hour = time.hour
                
                # 시간대별 패턴 (태양광: 낮에 높음, 풍력: 변동)
                if asset["type"] == "solar":
                    if 6 <= hour <= 18:
                        base_value = asset["capacity_kw"] * random.uniform(0.3, 0.8)
                    else:
                        base_value = 0
                elif asset["type"] == "wind":
                    base_value = asset["capacity_kw"] * random.uniform(0.2, 0.7)
                else:
                    base_value = asset["capacity_kw"] * random.uniform(0.1, 0.5)
                
                reading = {
                    "time": time.isoformat(),
                    "device_id": asset["id"],
                    "metric_type": "production",
                    "value": round(base_value, 2),
                    "unit": "kW"
                }
                readings.append(reading)
        
        elif asset["service_type"] == "demand":
            # 수요 자산: 소비 데이터
            for i in range(24):  # 최근 24시간
                time = now - timedelta(hours=23-i)
                hour = time.hour
                
                # 시간대별 패턴 (아침/저녁에 높음)
                if 7 <= hour <= 9 or 18 <= hour <= 22:
                    base_value = random.uniform(50, 150)
                elif 10 <= hour <= 17:
                    base_value = random.uniform(30, 80)
                else:
                    base_value = random.uniform(20, 50)
                
                reading = {
                    "time": time.isoformat(),
                    "device_id": asset["id"],
                    "metric_type": "consumption",
                    "value": round(base_value, 2),
                    "unit": "kW"
                }
                readings.append(reading)
    
    return readings

def generate_demand_data(asset_id: str, days: int = 93) -> List[Dict[str, Any]]:
    """수요 분석용 데이터 생성"""
    data = []
    now = datetime.now()
    
    for i in range(days):
        date = now - timedelta(days=days-i)
        
        # 요일 효과
        weekday_factor = 0.8 if date.weekday() >= 5 else 1.0
        
        # 계절 효과
        month = date.month
        if month in [12, 1, 2]:
            season_factor = 1.2  # 겨울
        elif month in [6, 7, 8]:
            season_factor = 1.3  # 여름
        else:
            season_factor = 1.0
        
        # 일일 평균 소비량
        daily_kwh = random.uniform(80, 120) * weekday_factor * season_factor
        peak_kw = daily_kwh / 24 * random.uniform(1.5, 2.5)
        
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "kWh": round(daily_kwh, 2),
            "kW": round(peak_kw, 2),
            "asset_id": asset_id
        })
    
    return data

def generate_supply_data(asset_id: str, capacity_kw: float, days: int = 30) -> List[Dict[str, Any]]:
    """공급 분석용 데이터 생성"""
    data = []
    now = datetime.now()
    
    for i in range(days):
        date = now - timedelta(days=days-i)
        
        # 날씨 효과 (간단한 시뮬레이션)
        weather_factor = random.uniform(0.5, 1.0)
        
        # 요일 효과
        weekday_factor = 0.9 if date.weekday() >= 5 else 1.0
        
        # 일일 생산량
        daily_production = capacity_kw * weather_factor * weekday_factor * random.uniform(0.3, 0.9) * 24
        
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "production_kwh": round(daily_production, 2),
            "peak_power_kw": round(capacity_kw * weather_factor * weekday_factor, 2),
            "efficiency": round(weather_factor * 100, 2),
            "asset_id": asset_id
        })
    
    return data

def save_mock_data():
    """가상 데이터를 JSON 파일로 저장"""
    output_dir = project_root / "data" / "mock"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # JSON 파일로 저장
    with open(output_dir / "mock_data.json", "w", encoding="utf-8") as f:
        json.dump(mock_data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"✅ 가상 데이터가 {output_dir / 'mock_data.json'}에 저장되었습니다.")

def main():
    """메인 함수"""
    print("🚀 가상 데이터 생성 시작...")
    print()
    
    # 1. 자산 생성
    print("📦 에너지 자산 생성 중...")
    assets = generate_assets()
    mock_data["assets"] = assets
    print(f"   ✅ {len(assets)}개의 자산 생성 완료")
    
    # 2. 재난 데이터 생성
    print("⚠️  재난 데이터 생성 중...")
    disasters = generate_disasters()
    mock_data["disasters"] = disasters
    print(f"   ✅ {len(disasters)}개의 재난 이벤트 생성 완료")
    
    # 3. 에너지 측정값 생성
    print("⚡ 에너지 측정값 생성 중...")
    energy_readings = generate_energy_readings(assets)
    mock_data["energy_readings"] = energy_readings
    print(f"   ✅ {len(energy_readings)}개의 측정값 생성 완료")
    
    # 4. 수요 데이터 생성
    print("📊 수요 분석 데이터 생성 중...")
    demand_assets = [a for a in assets if a["service_type"] == "demand"]
    for asset in demand_assets[:3]:  # 처음 3개만
        demand_data = generate_demand_data(asset["id"], days=93)
        mock_data["demand_data"].extend(demand_data)
    print(f"   ✅ {len(mock_data['demand_data'])}개의 수요 데이터 생성 완료")
    
    # 5. 공급 데이터 생성
    print("🔋 공급 분석 데이터 생성 중...")
    supply_assets = [a for a in assets if a["service_type"] == "supply"]
    for asset in supply_assets[:5]:  # 처음 5개만
        supply_data = generate_supply_data(asset["id"], asset["capacity_kw"], days=30)
        mock_data["supply_data"].extend(supply_data)
    print(f"   ✅ {len(mock_data['supply_data'])}개의 공급 데이터 생성 완료")
    
    print()
    print("💾 데이터 저장 중...")
    save_mock_data()
    
    print()
    print("=" * 50)
    print("📊 생성된 데이터 요약:")
    print(f"   • 자산: {len(assets)}개")
    print(f"   • 재난: {len(disasters)}개 (활성: {len([d for d in disasters if d['status'] == 'active'])}개)")
    print(f"   • 에너지 측정값: {len(energy_readings)}개")
    print(f"   • 수요 데이터: {len(mock_data['demand_data'])}개")
    print(f"   • 공급 데이터: {len(mock_data['supply_data'])}개")
    print("=" * 50)
    print()
    print("✅ 가상 데이터 생성 완료!")
    print()
    print("💡 다음 단계:")
    print("   1. API 엔드포인트들이 이 데이터를 사용하도록 업데이트해야 합니다.")
    print("   2. docker-compose up으로 서비스를 시작하세요.")
    print("   3. http://localhost:3000에서 프론트엔드를 확인하세요.")

if __name__ == "__main__":
    main()




