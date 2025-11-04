from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class WeatherMain(BaseModel):
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: int
    humidity: int

class WeatherCondition(BaseModel):
    id: int
    main: str
    description: str
    icon: str

class Wind(BaseModel):
    speed: float
    deg: int

class WeatherResponse(BaseModel):
    location: dict
    weather: WeatherCondition
    main: WeatherMain
    wind: Optional[Wind] = None
    visibility: Optional[int] = None
    clouds: Optional[dict] = None
    dt: datetime
    timezone: Optional[int] = None

class WeatherForecastItem(BaseModel):
    dt: datetime
    temp: float
    temp_min: float
    temp_max: float
    weather: WeatherCondition
    wind: Optional[Wind] = None
    humidity: int
    pressure: int

class WeatherForecastResponse(BaseModel):
    location: dict
    forecast: List[WeatherForecastItem]






