import httpx
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from src.config import settings
from src.schemas.weather import WeatherResponse, WeatherForecastResponse, WeatherCondition, WeatherMain, Wind

logger = logging.getLogger(__name__)

class WeatherService:
    """날씨 정보 서비스 (OpenWeatherMap API 사용)"""
    
    def __init__(self):
        self.api_key = settings.WEATHER_API_KEY
        self.base_url = settings.WEATHER_API_URL
        
    async def get_current_weather(self, lat: float, lon: float) -> WeatherResponse:
        """현재 날씨 정보 조회"""
        if not self.api_key:
            # Mock 데이터 반환 (API 키가 없는 경우)
            return self._get_mock_weather(lat, lon)
        
        async with httpx.AsyncClient() as client:
            try:
                url = f"{self.base_url}/weather"
                params = {
                    "lat": lat,
                    "lon": lon,
                    "appid": self.api_key,
                    "units": "metric"
                }
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                return self._parse_weather_response(data, lat, lon)
            except httpx.HTTPError as e:
                logger.error(f"Weather API error: {e}")
                return self._get_mock_weather(lat, lon)
    
    async def get_forecast(self, lat: float, lon: float, days: int = 5) -> WeatherForecastResponse:
        """날씨 예보 조회"""
        if not self.api_key:
            return self._get_mock_forecast(lat, lon, days)
        
        async with httpx.AsyncClient() as client:
            try:
                url = f"{self.base_url}/forecast"
                params = {
                    "lat": lat,
                    "lon": lon,
                    "appid": self.api_key,
                    "units": "metric",
                    "cnt": days * 8  # 3시간 간격 데이터
                }
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                return self._parse_forecast_response(data, lat, lon, days)
            except httpx.HTTPError as e:
                logger.error(f"Weather forecast API error: {e}")
                return self._get_mock_forecast(lat, lon, days)
    
    def _parse_weather_response(self, data: Dict[str, Any], lat: float, lon: float) -> WeatherResponse:
        """날씨 응답 파싱"""
        weather_data = data.get("weather", [{}])[0]
        main_data = data.get("main", {})
        wind_data = data.get("wind", {})
        
        return WeatherResponse(
            location={"lat": lat, "lon": lon, "name": data.get("name", "")},
            weather=WeatherCondition(
                id=weather_data.get("id", 0),
                main=weather_data.get("main", ""),
                description=weather_data.get("description", ""),
                icon=weather_data.get("icon", "")
            ),
            main=WeatherMain(
                temp=main_data.get("temp", 0),
                feels_like=main_data.get("feels_like", 0),
                temp_min=main_data.get("temp_min", 0),
                temp_max=main_data.get("temp_max", 0),
                pressure=main_data.get("pressure", 0),
                humidity=main_data.get("humidity", 0)
            ),
            wind=Wind(
                speed=wind_data.get("speed", 0),
                deg=wind_data.get("deg", 0)
            ) if wind_data else None,
            visibility=data.get("visibility"),
            clouds=data.get("clouds"),
            dt=datetime.fromtimestamp(data.get("dt", 0)),
            timezone=data.get("timezone")
        )
    
    def _parse_forecast_response(self, data: Dict[str, Any], lat: float, lon: float, days: int) -> WeatherForecastResponse:
        """예보 응답 파싱"""
        forecast_items = []
        
        for item in data.get("list", [])[:days * 8]:
            main_data = item.get("main", {})
            weather_data = item.get("weather", [{}])[0]
            wind_data = item.get("wind", {})
            
            forecast_items.append({
                "dt": datetime.fromtimestamp(item.get("dt", 0)),
                "temp": main_data.get("temp", 0),
                "temp_min": main_data.get("temp_min", 0),
                "temp_max": main_data.get("temp_max", 0),
                "weather": WeatherCondition(
                    id=weather_data.get("id", 0),
                    main=weather_data.get("main", ""),
                    description=weather_data.get("description", ""),
                    icon=weather_data.get("icon", "")
                ),
                "wind": Wind(
                    speed=wind_data.get("speed", 0),
                    deg=wind_data.get("deg", 0)
                ) if wind_data else None,
                "humidity": main_data.get("humidity", 0),
                "pressure": main_data.get("pressure", 0)
            })
        
        return WeatherForecastResponse(
            location={"lat": lat, "lon": lon, "name": data.get("city", {}).get("name", "")},
            forecast=forecast_items
        )
    
    def _get_mock_weather(self, lat: float, lon: float) -> WeatherResponse:
        """Mock 날씨 데이터 (API 키가 없을 때)"""
        return WeatherResponse(
            location={"lat": lat, "lon": lon, "name": "Test Location"},
            weather=WeatherCondition(
                id=800,
                main="Clear",
                description="clear sky",
                icon="01d"
            ),
            main=WeatherMain(
                temp=20.0,
                feels_like=19.5,
                temp_min=18.0,
                temp_max=22.0,
                pressure=1013,
                humidity=65
            ),
            wind=Wind(speed=3.5, deg=180),
            dt=datetime.now()
        )
    
    def _get_mock_forecast(self, lat: float, lon: float, days: int) -> WeatherForecastResponse:
        """Mock 예보 데이터"""
        forecast_items = []
        for i in range(days):
            forecast_items.append({
                "dt": datetime.now() + timedelta(hours=i*3),
                "temp": 20.0 + i,
                "temp_min": 18.0 + i,
                "temp_max": 22.0 + i,
                "weather": WeatherCondition(
                    id=800,
                    main="Clear",
                    description="clear sky",
                    icon="01d"
                ),
                "wind": Wind(speed=3.5, deg=180),
                "humidity": 65,
                "pressure": 1013
            })
        
        return WeatherForecastResponse(
            location={"lat": lat, "lon": lon, "name": "Test Location"},
            forecast=forecast_items
        )




