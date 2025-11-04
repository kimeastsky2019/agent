from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = os.getenv("APP_NAME", "Energy Orchestrator Platform")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/energy_db"
    )
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "20"))
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Security
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "your-secret-key-here-change-in-production"
    )
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # CORS
    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173"
    )
    
    # MQTT
    MQTT_BROKER_HOST: str = os.getenv("MQTT_BROKER_HOST", "localhost")
    MQTT_BROKER_PORT: int = int(os.getenv("MQTT_BROKER_PORT", "1883"))
    MQTT_USERNAME: str = os.getenv("MQTT_USERNAME", "")
    MQTT_PASSWORD: str = os.getenv("MQTT_PASSWORD", "")
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_TOPIC_IOT_DATA: str = os.getenv("KAFKA_TOPIC_IOT_DATA", "iot-data")
    KAFKA_TOPIC_DISASTERS: str = os.getenv("KAFKA_TOPIC_DISASTERS", "disasters")
    
    # External APIs
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    WEATHER_API_URL: str = os.getenv("WEATHER_API_URL", "https://api.openweathermap.org/data/2.5")
    NIED_API_URL: str = os.getenv("NIED_API_URL", "https://api.nied.go.jp")
    
    # Ontology
    JENA_FUSEKI_URL: str = os.getenv("JENA_FUSEKI_URL", "http://localhost:3030")
    RDF_DATABASE: str = os.getenv("RDF_DATABASE", "energy_ontology")
    ONTOLOGY_SERVICE_URL: str = os.getenv("ONTOLOGY_SERVICE_URL", "http://localhost:5000")
    
    # Image Broadcasting
    IMAGE_BROADCASTING_URL: str = os.getenv("IMAGE_BROADCASTING_URL", "http://localhost:5001")
    
    # Monitoring
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    GRAFANA_URL: str = os.getenv("GRAFANA_URL", "http://localhost:3001")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 프로덕션 환경에서 SECRET_KEY 검증
        if self.ENVIRONMENT == "production":
            if self.SECRET_KEY == "your-secret-key-here-change-in-production":
                raise ValueError(
                    "SECRET_KEY must be changed in production environment. "
                    "Please set a strong SECRET_KEY in your .env file."
                )
            if len(self.SECRET_KEY) < 32:
                raise ValueError(
                    "SECRET_KEY must be at least 32 characters long in production."
                )

settings = Settings()






