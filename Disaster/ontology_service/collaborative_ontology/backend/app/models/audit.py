from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base_class import Base

class AuditAction(str, enum.Enum):
    """감사 액션 타입"""
    # 인증/인가
    LOGIN = "login"
    LOGOUT = "logout"
    FAILED_LOGIN = "failed_login"
    
    # CRUD 작업
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    
    # 협업
    SUBMIT_PROPOSAL = "submit_proposal"
    REVIEW_PROPOSAL = "review_proposal"
    APPROVE_PROPOSAL = "approve_proposal"
    REJECT_PROPOSAL = "reject_proposal"
    COMMENT = "comment"
    
    # 권한
    GRANT_PERMISSION = "grant_permission"
    REVOKE_PERMISSION = "revoke_permission"
    
    # 시스템
    EXPORT_DATA = "export_data"
    IMPORT_DATA = "import_data"
    BACKUP = "backup"
    RESTORE = "restore"

class AuditLog(Base):
    """감사 로그 - 모든 중요한 작업 기록"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # 사용자 정보
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    username = Column(String, nullable=True)  # 사용자 삭제 시에도 기록 유지
    
    # 액션 정보
    action = Column(SQLEnum(AuditAction), nullable=False, index=True)
    resource_type = Column(String, nullable=False, index=True)  # user, class, property, proposal
    resource_id = Column(Integer, nullable=True)
    
    # 상세 정보
    description = Column(Text, nullable=True)
    changes = Column(JSON, nullable=True)  # before/after 값
    
    # 메타데이터
    metadata = Column(JSON, nullable=True)  # 추가 컨텍스트 정보
    
    # 요청 정보
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    request_method = Column(String, nullable=True)  # GET, POST, PUT, DELETE
    request_path = Column(String, nullable=True)
    
    # 결과
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    
    # 타임스탬프
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog {self.id}: {self.action} on {self.resource_type}>"


class DataQualityMetric(Base):
    """데이터 품질 메트릭"""
    __tablename__ = "data_quality_metrics"

    id = Column(Integer, primary_key=True, index=True)
    
    # 엔티티 정보
    entity_type = Column(String, nullable=False, index=True)
    entity_id = Column(Integer, nullable=False)
    
    # 품질 점수
    completeness_score = Column(Integer, default=0)  # 0-100
    accuracy_score = Column(Integer, default=0)  # 0-100
    consistency_score = Column(Integer, default=0)  # 0-100
    overall_score = Column(Integer, default=0)  # 0-100
    
    # 이슈
    issues = Column(JSON, nullable=True)  # 발견된 문제점 리스트
    
    # 권장사항
    recommendations = Column(JSON, nullable=True)  # 개선 권장사항
    
    # 평가 정보
    evaluated_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    evaluated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    evaluator = relationship("User")
    
    def __repr__(self):
        return f"<DataQualityMetric {self.entity_type}:{self.entity_id} - {self.overall_score}>"


class SystemMetric(Base):
    """시스템 메트릭 및 통계"""
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True)
    
    # 메트릭 타입
    metric_type = Column(String, nullable=False, index=True)  # user_activity, proposal_stats, etc.
    
    # 메트릭 데이터
    metrics = Column(JSON, nullable=False)  # 실제 메트릭 값들
    
    # 기간
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<SystemMetric {self.metric_type} - {self.period_start}>"


class ComplianceReport(Base):
    """규정 준수 보고서"""
    __tablename__ = "compliance_reports"

    id = Column(Integer, primary_key=True, index=True)
    
    # 보고서 정보
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(String, nullable=False)  # gdpr, audit, quality
    
    # 기간
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # 보고서 내용
    findings = Column(JSON, nullable=False)  # 발견사항
    violations = Column(JSON, nullable=True)  # 위반사항
    recommendations = Column(JSON, nullable=True)  # 권장사항
    
    # 생성 정보
    generated_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 파일
    file_path = Column(String, nullable=True)  # PDF 보고서 경로
    
    # Relationships
    generator = relationship("User")
    
    def __repr__(self):
        return f"<ComplianceReport {self.id}: {self.title}>"
