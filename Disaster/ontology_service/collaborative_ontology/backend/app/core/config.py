from pydantic_settings import BaseSettings
from typing import Optional, List
import secrets


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 기본 설정
    APP_NAME: str = "Collaborative Energy Ontology Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API 설정
    API_V1_PREFIX: str = "/api/v1"
    
    # 보안
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # 데이터베이스
    DATABASE_URL: str = "postgresql://ontology_user:ontology_pass@localhost:5432/collaborative_ontology"
    
    # Redis (캐싱 및 WebSocket)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # 파일 업로드
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # 이메일 (알림용)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # 첫 번째 슈퍼유저
    FIRST_SUPERUSER_EMAIL: str = "admin@gnginternational.com"
    FIRST_SUPERUSER_USERNAME: str = "admin"
    FIRST_SUPERUSER_PASSWORD: str = "changeme123"
    
    # Ontology 설정
    DEFAULT_NAMESPACE: str = "energy"
    MAX_PROPOSAL_APPROVALS_REQUIRED: int = 3
    
    # WebSocket
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30  # seconds
    
    # 로깅
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
