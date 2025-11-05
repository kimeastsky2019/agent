from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Boolean,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base_class import Base

class ProposalStatus(str, enum.Enum):
    """제안 상태"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    WITHDRAWN = "withdrawn"

class ProposalType(str, enum.Enum):
    """제안 타입"""
    CREATE = "create"  # 새로운 엔티티 생성
    UPDATE = "update"  # 기존 엔티티 수정
    DELETE = "delete"  # 엔티티 삭제
    MERGE = "merge"    # 엔티티 병합

class ReviewDecision(str, enum.Enum):
    """리뷰 결정"""
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_CHANGES = "request_changes"
    ABSTAIN = "abstain"

class Proposal(Base):
    """변경 제안"""
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)

    # 기본 정보
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    
    # 제안 타입 및 대상
    proposal_type = Column(SQLEnum(ProposalType), nullable=False)
    entity_type = Column(String, nullable=False)  # class, property, relationship, instance
    entity_id = Column(Integer, nullable=True)  # 기존 엔티티 ID (update/delete의 경우)
    
    # 변경 내용 (JSON)
    proposed_changes = Column(JSON, nullable=False)  # 제안된 변경사항
    current_state = Column(JSON, nullable=True)  # 현재 상태 (비교용)
    
    # 상태
    status = Column(SQLEnum(ProposalStatus), default=ProposalStatus.DRAFT, index=True)
    
    # 우선순위 및 카테고리
    priority = Column(String, default="medium")  # low, medium, high, critical
    category = Column(String, nullable=True)  # 카테고리 (예: "data_quality", "new_feature")
    tags = Column(JSON, nullable=True)
    
    # 근거 및 영향 분석
    rationale = Column(Text, nullable=True)  # 제안 이유
    impact_analysis = Column(Text, nullable=True)  # 영향 분석
    affected_entities = Column(JSON, nullable=True)  # 영향받는 엔티티들
    
    # 승인 요구사항
    required_approvals = Column(Integer, default=2)  # 필요한 승인 수
    current_approvals = Column(Integer, default=0)  # 현재 승인 수
    
    # 작성자 및 담당자
    author_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    assigned_to = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    space_id = Column(Integer, ForeignKey('collaboration_spaces.id', ondelete='SET NULL'), nullable=True)

    # 마감일
    deadline = Column(DateTime(timezone=True), nullable=True)

    # 생성/수정 정보
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    author = relationship("User", foreign_keys=[author_id], back_populates="proposals")
    assignee = relationship("User", foreign_keys=[assigned_to])
    reviews = relationship("Review", back_populates="proposal", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="proposal", cascade="all, delete-orphan")
    space = relationship("CollaborationSpace", back_populates="proposals")

    def __repr__(self):
        return f"<Proposal {self.id}: {self.title}>"


class Review(Base):
    """제안 리뷰"""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    
    # 제안 및 리뷰어
    proposal_id = Column(Integer, ForeignKey('proposals.id', ondelete='CASCADE'), nullable=False)
    reviewer_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # 리뷰 내용
    decision = Column(SQLEnum(ReviewDecision), nullable=False)
    comment = Column(Text, nullable=True)
    
    # 상세 피드백 (구조화된 데이터)
    feedback = Column(JSON, nullable=True)  # {aspect: rating, comments}
    
    # 조건부 승인
    conditions = Column(Text, nullable=True)  # 승인 조건
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    proposal = relationship("Proposal", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")
    
    def __repr__(self):
        return f"<Review {self.id} - {self.decision}>"


class Comment(Base):
    """제안 토론 댓글"""
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    
    # 제안 및 작성자
    proposal_id = Column(Integer, ForeignKey('proposals.id', ondelete='CASCADE'), nullable=False)
    author_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # 댓글 내용
    content = Column(Text, nullable=False)
    
    # 스레드 (대댓글)
    parent_id = Column(Integer, ForeignKey('comments.id', ondelete='CASCADE'), nullable=True)
    
    # 첨부 파일
    attachments = Column(JSON, nullable=True)  # 파일 정보 리스트
    
    # 멘션
    mentions = Column(JSON, nullable=True)  # 멘션된 사용자 ID 리스트
    
    # 편집 정보
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime(timezone=True), nullable=True)
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    proposal = relationship("Proposal", back_populates="comments")
    author = relationship("User", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")
    
    def __repr__(self):
        return f"<Comment {self.id}>"


class Notification(Base):
    """알림"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    
    # 수신자
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # 알림 내용
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String, nullable=False)  # proposal_submitted, review_requested, comment_added
    
    # 관련 엔티티
    related_entity_type = Column(String, nullable=True)  # proposal, comment, review
    related_entity_id = Column(Integer, nullable=True)
    
    # 링크
    link = Column(String, nullable=True)
    
    # 상태
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<Notification {self.id} - {self.title}>"


class CollaborationSession(Base):
    """실시간 협업 세션"""
    __tablename__ = "collaboration_sessions"

    id = Column(Integer, primary_key=True, index=True)

    # 세션 정보
    entity_type = Column(String, nullable=False)  # class, property, proposal
    entity_id = Column(Integer, nullable=False)
    space_id = Column(Integer, ForeignKey('collaboration_spaces.id', ondelete='CASCADE'), nullable=True)

    # 활성 사용자들
    active_users = Column(JSON, default=[])  # user_id 리스트

    # 잠금 정보
    locked_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    locked_at = Column(DateTime(timezone=True), nullable=True)
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    lock_holder = relationship("User")
    space = relationship("CollaborationSpace")

    def __repr__(self):
        return f"<CollaborationSession {self.entity_type}:{self.entity_id}>"


class CollaborationSpaceVisibility(str, enum.Enum):
    """협업 공간 공개 범위"""

    PUBLIC = "public"
    COMMUNITY = "community"
    PRIVATE = "private"


class CollaborationSpaceRole(str, enum.Enum):
    """협업 공간 내 역할"""

    COORDINATOR = "coordinator"
    CONTRIBUTOR = "contributor"
    REVIEWER = "reviewer"
    OBSERVER = "observer"
    DATA_STEWARD = "data_steward"


class CollaborationSpace(Base):
    """에너지 온톨로지 협업 공간"""

    __tablename__ = "collaboration_spaces"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    mission = Column(Text, nullable=True)
    domain_focus = Column(String, nullable=True)
    visibility = Column(SQLEnum(CollaborationSpaceVisibility), default=CollaborationSpaceVisibility.PUBLIC, index=True)
    onboarding_url = Column(String, nullable=True)
    external_channel = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)
    profile = Column(JSON, nullable=True)

    created_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    updated_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    creator = relationship("User", foreign_keys=[created_by], backref="created_spaces")
    updater = relationship("User", foreign_keys=[updated_by])
    memberships = relationship("CollaborationSpaceMembership", back_populates="space", cascade="all, delete-orphan")
    proposals = relationship("Proposal", back_populates="space")

    def __repr__(self):
        return f"<CollaborationSpace {self.slug}>"


class CollaborationSpaceMembership(Base):
    """협업 공간 참여자"""

    __tablename__ = "collaboration_space_memberships"

    id = Column(Integer, primary_key=True, index=True)
    space_id = Column(Integer, ForeignKey('collaboration_spaces.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role = Column(SQLEnum(CollaborationSpaceRole), default=CollaborationSpaceRole.CONTRIBUTOR, index=True)
    responsibilities = Column(Text, nullable=True)
    expertise_tags = Column(JSON, nullable=True)
    contribution_hours = Column(Integer, default=0)
    last_contribution_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    is_core_team = Column(Boolean, default=False)

    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    space = relationship("CollaborationSpace", back_populates="memberships")
    user = relationship("User", backref="collaboration_memberships")

    def __repr__(self):
        return f"<CollaborationSpaceMembership user={self.user_id} space={self.space_id}>"
