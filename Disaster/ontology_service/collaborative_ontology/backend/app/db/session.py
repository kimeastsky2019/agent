from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os

from app.core.config import settings

# 데이터베이스 엔진 생성
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# 세션 팩토리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """데이터베이스 초기화"""
    from app.db.base_class import Base
    from app.models import (
        User, UserSession,
        OntologyClass, OntologyProperty, OntologyRelationship, OntologyInstance, OntologyVersion,
        Proposal, Review, Comment, Notification, CollaborationSession,
        CollaborationSpace, CollaborationSpaceMembership,
        AuditLog, DataQualityMetric, SystemMetric, ComplianceReport
    )
    
    # 테이블 생성
    Base.metadata.create_all(bind=engine)
