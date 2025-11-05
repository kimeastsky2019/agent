from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.db.base_class import Base

# 역할 정의
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ONTOLOGY_EDITOR = "ontology_editor"
    DOMAIN_EXPERT = "domain_expert"
    ENERGY_PROVIDER = "energy_provider"
    DEVICE_OPERATOR = "device_operator"
    ENERGY_CONSUMER = "energy_consumer"
    POLICY_MAKER = "policy_maker"
    VOLUNTEER = "volunteer"
    VIEWER = "viewer"

# 사용자-역할 다대다 관계 테이블
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('role', SQLEnum(UserRole))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # 조직 정보
    organization = Column(String, nullable=True)
    department = Column(String, nullable=True)
    position = Column(String, nullable=True)
    
    # 연락처
    phone = Column(String, nullable=True)
    
    # 전문 분야
    expertise_areas = Column(String, nullable=True)  # JSON 형태로 저장
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    roles = relationship("UserRole", secondary=user_roles, backref="users")
    proposals = relationship("Proposal", back_populates="author", foreign_keys="Proposal.author_id")
    reviews = relationship("Review", back_populates="reviewer")
    comments = relationship("Comment", back_populates="author")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"
    
    @property
    def has_admin_role(self):
        return UserRole.ADMIN in self.roles or self.is_superuser
    
    @property
    def can_edit_ontology(self):
        return UserRole.ONTOLOGY_EDITOR in self.roles or self.has_admin_role

    @property
    def can_review(self):
        return UserRole.DOMAIN_EXPERT in self.roles or self.has_admin_role

    @property
    def can_coordinate_spaces(self):
        return any(
            role in self.roles
            for role in [
                UserRole.ADMIN,
                UserRole.ONTOLOGY_EDITOR,
                UserRole.VOLUNTEER,
                UserRole.POLICY_MAKER,
            ]
        )


class UserSession(Base):
    """사용자 세션 관리 (실시간 협업용)"""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    session_token = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # WebSocket 연결 정보
    websocket_id = Column(String, nullable=True)
    current_page = Column(String, nullable=True)  # 현재 보고 있는 페이지
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<UserSession {self.user_id} - {self.session_token[:8]}...>"
