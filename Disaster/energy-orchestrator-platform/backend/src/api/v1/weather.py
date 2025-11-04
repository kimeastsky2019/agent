from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from src.database import get_db
from src.services.weather_service import WeatherService
from src.schemas.weather import WeatherResponse, WeatherForecastResponse

router = APIRouter()

@router.get("/current", response_model=WeatherResponse)
async def get_current_weather(
    lat: float,
    lon: float,
    db: Session = Depends(get_db)
):
    """현재 날씨 정보"""
    weather_service = WeatherService()
    try:
        weather = await weather_service.get_current_weather(lat, lon)
        return weather
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast", response_model=WeatherForecastResponse)
async def get_weather_forecast(
    lat: float,
    lon: float,
    days: int = 5,
    db: Session = Depends(get_db)
):
    """날씨 예보"""
    weather_service = WeatherService()
    try:
        forecast = await weather_service.get_forecast(lat, lon, days)
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/locations")
async def get_weather_locations(db: Session = Depends(get_db)):
    """날씨 정보가 있는 위치 목록"""
    return []






