"""
Database models for Collaborative Ontology Platform
Using SQLAlchemy ORM
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum, JSON, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()

# Association Tables
user_projects = Table(
    'user_projects',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('project_id', Integer, ForeignKey('projects.id'))
)

change_reviewers = Table(
    'change_reviewers',
    Base.metadata,
    Column('change_id', Integer, ForeignKey('ontology_changes.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)

# Enums
class UserRole(enum.Enum):
    END_USER = "end_user"
    ENERGY_PROVIDER = "energy_provider"
    DEVICE_OPERATOR = "device_operator"
    ENERGY_EXPERT = "energy_expert"
    SYSTEM_ADMIN = "system_admin"

class ChangeStatus(enum.Enum):
    DRAFT = "draft"
    PROPOSED = "proposed"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    MERGED = "merged"

class OntologyChangeType(enum.Enum):
    ADD_CLASS = "add_class"
    ADD_PROPERTY = "add_property"
    ADD_INDIVIDUAL = "add_individual"
    MODIFY_CLASS = "modify_class"
    MODIFY_PROPERTY = "modify_property"
    DELETE_CLASS = "delete_class"
    DELETE_PROPERTY = "delete_property"

class NotificationType(enum.Enum):
    CHANGE_PROPOSED = "change_proposed"
    CHANGE_REVIEWED = "change_reviewed"
    CHANGE_APPROVED = "change_approved"
    CHANGE_REJECTED = "change_rejected"
    COMMENT_ADDED = "comment_added"
    MENTION = "mention"

# Models

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    organization = Column(String(100))
    department = Column(String(100))
    bio = Column(Text)
    avatar_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)

    # Relationships
    authored_changes = relationship("OntologyChange", back_populates="author", foreign_keys="OntologyChange.author_id")
    reviews = relationship("ChangeReview", back_populates="reviewer")
    comments = relationship("ChangeComment", back_populates="author")
    projects = relationship("Project", secondary=user_projects, back_populates="members")
    notifications = relationship("Notification", back_populates="user")
    activity_logs = relationship("ActivityLog", back_populates="user")

class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    ontology_namespace = Column(String(255), unique=True, nullable=False)
    is_public = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    members = relationship("User", secondary=user_projects, back_populates="projects")
    ontology_versions = relationship("OntologyVersion", back_populates="project")
    changes = relationship("OntologyChange", back_populates="project")

class OntologyVersion(Base):
    __tablename__ = 'ontology_versions'

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    version_number = Column(String(20), nullable=False)
    commit_message = Column(Text)
    rdf_content = Column(Text, nullable=False)  # Serialized RDF
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=func.now())
    is_current = Column(Boolean, default=False)

    # Relationships
    project = relationship("Project", back_populates="ontology_versions")

class OntologyChange(Base):
    __tablename__ = 'ontology_changes'

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    change_type = Column(SQLEnum(OntologyChangeType), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(SQLEnum(ChangeStatus), default=ChangeStatus.DRAFT)
    change_data = Column(JSON, nullable=False)  # Actual change content
    parent_version_id = Column(Integer, ForeignKey('ontology_versions.id'))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    approved_at = Column(DateTime)
    merged_at = Column(DateTime)

    # Relationships
    project = relationship("Project", back_populates="changes")
    author = relationship("User", back_populates="authored_changes", foreign_keys=[author_id])
    reviewers = relationship("User", secondary=change_reviewers)
    reviews = relationship("ChangeReview", back_populates="change")
    comments = relationship("ChangeComment", back_populates="change")

class ChangeReview(Base):
    __tablename__ = 'change_reviews'

    id = Column(Integer, primary_key=True, index=True)
    change_id = Column(Integer, ForeignKey('ontology_changes.id'), nullable=False)
    reviewer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    approved = Column(Boolean)
    comment = Column(Text)
    reviewed_at = Column(DateTime, default=func.now())

    # Relationships
    change = relationship("OntologyChange", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")

class ChangeComment(Base):
    __tablename__ = 'change_comments'

    id = Column(Integer, primary_key=True, index=True)
    change_id = Column(Integer, ForeignKey('ontology_changes.id'), nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    parent_comment_id = Column(Integer, ForeignKey('change_comments.id'))  # For threaded comments
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    change = relationship("OntologyChange", back_populates="comments")
    author = relationship("User", back_populates="comments")
    replies = relationship("ChangeComment")

class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type = Column(SQLEnum(NotificationType), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    link = Column(String(255))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="notifications")

class ActivityLog(Base):
    __tablename__ = 'activity_logs'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action_type = Column(String(50), nullable=False)
    resource_type = Column(String(50))  # e.g., "ontology_change", "comment"
    resource_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="activity_logs")

class DataSource(Base):
    __tablename__ = 'data_sources'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # e.g., "iot", "weather", "market"
    description = Column(Text)
    connection_config = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_sync = Column(DateTime)

class DataMapping(Base):
    __tablename__ = 'data_mappings'

    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, ForeignKey('data_sources.id'), nullable=False)
    source_field = Column(String(100), nullable=False)
    ontology_property = Column(String(255), nullable=False)
    transformation_rule = Column(JSON)  # Optional data transformation
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

class ValidationRule(Base):
    __tablename__ = 'validation_rules'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    rule_type = Column(String(50), nullable=False)  # e.g., "consistency", "completeness"
    sparql_query = Column(Text)  # SPARQL query for validation
    severity = Column(String(20), default="warning")  # "error", "warning", "info"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

class ValidationResult(Base):
    __tablename__ = 'validation_results'

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey('validation_rules.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    passed = Column(Boolean, nullable=False)
    message = Column(Text)
    details = Column(JSON)
    validated_at = Column(DateTime, default=func.now())

# Database connection and session management
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@localhost/collaborative_ontology"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
