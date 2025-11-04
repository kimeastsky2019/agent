"""
Energy Supply Analysis Service
통합된 에너지 공급 분석 서비스
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import random
import math
import logging

logger = logging.getLogger(__name__)

try:
    from sklearn.ensemble import IsolationForest
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available. Using mock implementation.")


class SupplyAnalysisService:
    """에너지 공급 분석 서비스"""
    
    def __init__(self, asset_id: str):
        self.asset_id = asset_id
        # 가상 데이터에서 자산 정보 로드
        try:
            from src.data.mock_data import get_asset
            asset = get_asset(asset_id)
            if asset:
                self.capacity_kw = asset.get("capacity_kw", 100.0)
            else:
                self.capacity_kw = 100.0
        except Exception:
            self.capacity_kw = 100.0
        
    async def analyze_supply(self) -> Dict[str, Any]:
        """에너지 공급 분석 실행"""
        try:
            # 실시간 전력 데이터
            realtime_data = await self.get_realtime_power()
            
            # 생산량 예측
            forecast = await self.forecast_production()
            
            # 이상 탐지
            anomalies = await self.detect_anomalies()
            
            # 시설 정보
            facility = await self.get_facility_info()
            
            # 통계 계산
            statistics = self.calculate_statistics(realtime_data)
            
            return {
                'asset_id': self.asset_id,
                'realtime_data': realtime_data,
                'forecast': forecast,
                'anomalies': anomalies,
                'facility': facility,
                'statistics': statistics,
                'status': 'success'
            }
        except Exception as e:
            logger.error(f"Error in supply analysis: {e}")
            return self._get_mock_analysis()
    
    async def get_realtime_power(self, range_type: str = "hour") -> Dict[str, Any]:
        """실시간 전력 데이터 조회"""
        now = datetime.now()
        labels = []
        values = []
        
        capacity = self.capacity_kw
        
        if range_type == "hour":
            # 최근 24시간
            for i in range(24, 0, -1):
                time = now - timedelta(hours=i)
                labels.append(time.strftime("%H:%M"))
                
                # 시간대별 패턴 (태양광: 낮에 높음)
                hour = time.hour
                if 6 <= hour <= 18:
                    base_value = capacity * (0.3 + math.sin((hour - 6) / 12 * math.pi) * 0.5)
                else:
                    base_value = capacity * random.uniform(0, 0.1)
                
                values.append(round(base_value + random.uniform(-5, 5), 2))
        elif range_type == "day":
            # 최근 7일
            for i in range(7, 0, -1):
                date = now - timedelta(days=i)
                labels.append(date.strftime("%m/%d"))
                values.append(round(capacity * random.uniform(0.3, 0.7), 2))
        
        return {
            "labels": labels,
            "values": values,
            "range_type": range_type,
            "timestamp": now.isoformat()
        }
    
    async def forecast_production(self, days: int = 7) -> Dict[str, Any]:
        """생산량 예측"""
        forecast_data = []
        base_production = 100  # 기본 생산량 (kWh)
        
        for i in range(days):
            date = datetime.now() + timedelta(days=i+1)
            
            # 요일 효과 (주말에 약간 낮음)
            weekday_factor = 0.9 if date.weekday() >= 5 else 1.0
            
            # 계절 효과 (간단한 사인 함수)
            season_factor = 1 + 0.3 * np.sin((date.month - 3) / 12 * 2 * np.pi)
            
            # 랜덤 변동
            random_factor = random.uniform(0.85, 1.15)
            
            # 예측 생산량
            predicted = base_production * weekday_factor * season_factor * random_factor
            
            # 신뢰 구간
            confidence_interval = predicted * 0.15
            
            forecast_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "day_of_week": ["월", "화", "수", "목", "금", "토", "일"][date.weekday()],
                "predicted_production": round(predicted, 2),
                "confidence_lower": round(predicted - confidence_interval, 2),
                "confidence_upper": round(predicted + confidence_interval, 2),
                "confidence_level": round(random.uniform(80, 95), 2),
                "weather_factor": round(season_factor, 2)
            })
        
        return {
            "forecast_days": days,
            "predictions": forecast_data
        }
    
    async def detect_anomalies(self) -> Dict[str, Any]:
        """이상 탐지"""
        if not SKLEARN_AVAILABLE:
            return {
                "count": 3,
                "anomalies": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                        "value": 150.5,
                        "severity": "high",
                        "description": "이상 높은 생산량"
                    }
                ]
            }
        
        try:
            # 샘플 데이터 생성
            data = []
            for i in range(100):
                value = 50 + np.random.normal(0, 10)
                data.append(value)
            
            # 이상치 추가
            data.extend([10, 150, 5, 160])
            data_array = np.array(data).reshape(-1, 1)
            
            # Isolation Forest 모델
            model = IsolationForest(
                contamination=0.05,
                random_state=42
            )
            
            # 학습 및 예측
            predictions = model.fit_predict(data_array)
            scores = model.score_samples(data_array)
            
            # 이상치 탐지
            anomaly_indices = np.where(predictions == -1)[0]
            
            anomalies = []
            for idx in anomaly_indices[:10]:  # 최대 10개만
                anomalies.append({
                    "timestamp": (datetime.now() - timedelta(hours=idx)).isoformat(),
                    "value": float(data_array[idx][0]),
                    "score": float(scores[idx]),
                    "severity": "high" if abs(scores[idx]) > 0.5 else "medium"
                })
            
            return {
                "count": len(anomalies),
                "anomalies": anomalies
            }
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            return {"count": 0, "anomalies": []}
    
    async def get_facility_info(self) -> Dict[str, Any]:
        """시설 정보 조회"""
        # 자산 정보 가져오기
        try:
            from src.data.mock_data import get_asset
            asset = get_asset(self.asset_id)
            if asset:
                asset_name = asset.get("name", f"Facility {self.asset_id}")
                asset_type = asset.get("type", "solar")
                capacity = asset.get("capacity_kw", 100.0) * 1000  # kW to W
                status = asset.get("status", "online")
            else:
                asset_name = f"Solar Facility {self.asset_id}"
                asset_type = "solar"
                capacity = self.capacity_kw * 1000
                status = "online"
        except Exception:
            asset_name = f"Solar Facility {self.asset_id}"
            asset_type = "solar"
            capacity = self.capacity_kw * 1000
            status = "online"
        
        return {
            "id": self.asset_id,
            "name": asset_name,
            "type": asset_type,
            "capacity": capacity,
            "current_power": random.uniform(0, capacity * 0.8),
            "efficiency": random.uniform(80, 95),
            "status": status,
            "last_updated": datetime.now().isoformat()
        }
    
    def calculate_statistics(self, realtime_data: Dict[str, Any]) -> Dict[str, Any]:
        """통계 계산"""
        values = realtime_data.get("values", [])
        
        if not values:
            return {
                "total_production": 0.0,
                "average_power": 0.0,
                "peak_power": 0.0,
                "efficiency": 0.0
            }
        
        total_production = sum(values)
        average_power = total_production / len(values) if values else 0
        peak_power = max(values) if values else 0
        
        return {
            "total_production": round(total_production, 2),
            "average_power": round(average_power, 2),
            "peak_power": round(peak_power, 2),
            "efficiency": round(random.uniform(80, 95), 2)
        }
    
    def _get_mock_analysis(self) -> Dict[str, Any]:
        """Mock 분석 결과"""
        return {
            'asset_id': self.asset_id,
            'realtime_data': {
                "labels": [],
                "values": [],
                "range_type": "hour"
            },
            'forecast': {
                "forecast_days": 7,
                "predictions": []
            },
            'anomalies': {
                "count": 0,
                "anomalies": []
            },
            'facility': {
                "id": self.asset_id,
                "name": f"Solar Facility {self.asset_id}",
                "type": "solar",
                "capacity": 100000,
                "current_power": 0,
                "efficiency": 0,
                "status": "online"
            },
            'statistics': {
                "total_production": 0.0,
                "average_power": 0.0,
                "peak_power": 0.0,
                "efficiency": 0.0
            },
            'status': 'success'
        }

