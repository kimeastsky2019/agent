from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base_class import Base

class OntologyEntityType(str, enum.Enum):
    """온톨로지 엔티티 타입"""
    CLASS = "class"
    PROPERTY = "property"
    RELATIONSHIP = "relationship"
    INSTANCE = "instance"

class OntologyStatus(str, enum.Enum):
    """온톨로지 상태"""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

class OntologyClass(Base):
    """온톨로지 클래스 (예: SolarPanel, Battery, EnergyStorage)"""
    __tablename__ = "ontology_classes"

    id = Column(Integer, primary_key=True, index=True)
    
    # 기본 정보
    name = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # 계층 구조
    parent_id = Column(Integer, ForeignKey('ontology_classes.id', ondelete='SET NULL'), nullable=True)
    namespace = Column(String, default="energy", index=True)  # 네임스페이스
    
    # 메타데이터
    uri = Column(String, unique=True, nullable=False)  # Unique identifier (예: urn:energy:SolarPanel)
    version = Column(String, default="1.0.0")
    status = Column(SQLEnum(OntologyStatus), default=OntologyStatus.DRAFT)
    
    # 추가 속성 (JSON)
    metadata = Column(JSON, nullable=True)  # 유연한 메타데이터 저장
    tags = Column(JSON, nullable=True)  # 태그 리스트
    
    # 생성/수정 정보
    created_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    updated_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    parent = relationship("OntologyClass", remote_side=[id], backref="subclasses")
    properties = relationship("OntologyProperty", back_populates="ontology_class", cascade="all, delete-orphan")
    relationships_as_source = relationship("OntologyRelationship", foreign_keys="OntologyRelationship.source_class_id", back_populates="source_class")
    relationships_as_target = relationship("OntologyRelationship", foreign_keys="OntologyRelationship.target_class_id", back_populates="target_class")
    instances = relationship("OntologyInstance", back_populates="ontology_class")
    
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    
    def __repr__(self):
        return f"<OntologyClass {self.name}>"


class OntologyProperty(Base):
    """온톨로지 속성 (예: capacity, efficiency, voltage)"""
    __tablename__ = "ontology_properties"

    id = Column(Integer, primary_key=True, index=True)
    
    # 기본 정보
    name = Column(String, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # 속한 클래스
    class_id = Column(Integer, ForeignKey('ontology_classes.id', ondelete='CASCADE'), nullable=False)
    
    # 데이터 타입
    data_type = Column(String, nullable=False)  # string, integer, float, boolean, date, json
    unit = Column(String, nullable=True)  # 단위 (예: kW, V, %)
    
    # 제약 조건
    is_required = Column(Boolean, default=False)
    default_value = Column(String, nullable=True)
    constraints = Column(JSON, nullable=True)  # min, max, regex, enum 등
    
    # 메타데이터
    metadata = Column(JSON, nullable=True)
    status = Column(SQLEnum(OntologyStatus), default=OntologyStatus.DRAFT)
    
    # 생성/수정 정보
    created_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    updated_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    ontology_class = relationship("OntologyClass", back_populates="properties")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    
    def __repr__(self):
        return f"<OntologyProperty {self.name}>"


class OntologyRelationship(Base):
    """온톨로지 관계 (예: SolarPanel -produces-> Energy)"""
    __tablename__ = "ontology_relationships"

    id = Column(Integer, primary_key=True, index=True)
    
    # 기본 정보
    name = Column(String, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # 관계 정의
    source_class_id = Column(Integer, ForeignKey('ontology_classes.id', ondelete='CASCADE'), nullable=False)
    target_class_id = Column(Integer, ForeignKey('ontology_classes.id', ondelete='CASCADE'), nullable=False)
    
    # 관계 타입
    relationship_type = Column(String, nullable=False)  # has, produces, consumes, connects_to, etc.
    cardinality = Column(String, default="one-to-many")  # one-to-one, one-to-many, many-to-many
    
    # 방향성
    is_bidirectional = Column(Boolean, default=False)
    inverse_name = Column(String, nullable=True)  # 역방향 관계 이름
    
    # 메타데이터
    metadata = Column(JSON, nullable=True)
    status = Column(SQLEnum(OntologyStatus), default=OntologyStatus.DRAFT)
    
    # 생성/수정 정보
    created_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    updated_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    source_class = relationship("OntologyClass", foreign_keys=[source_class_id], back_populates="relationships_as_source")
    target_class = relationship("OntologyClass", foreign_keys=[target_class_id], back_populates="relationships_as_target")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    
    def __repr__(self):
        return f"<OntologyRelationship {self.name}>"


class OntologyInstance(Base):
    """온톨로지 인스턴스 (예: 실제 태양광 패널 #12345)"""
    __tablename__ = "ontology_instances"

    id = Column(Integer, primary_key=True, index=True)
    
    # 기본 정보
    name = Column(String, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # 속한 클래스
    class_id = Column(Integer, ForeignKey('ontology_classes.id', ondelete='CASCADE'), nullable=False)
    
    # 속성 값들 (JSON으로 저장)
    property_values = Column(JSON, nullable=False)  # {property_name: value}
    
    # 외부 참조
    external_id = Column(String, nullable=True)  # 외부 시스템 ID
    external_source = Column(String, nullable=True)  # 외부 시스템 출처
    
    # 메타데이터
    metadata = Column(JSON, nullable=True)
    status = Column(SQLEnum(OntologyStatus), default=OntologyStatus.ACTIVE)
    
    # 생성/수정 정보
    created_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    updated_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    ontology_class = relationship("OntologyClass", back_populates="instances")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    
    def __repr__(self):
        return f"<OntologyInstance {self.name}>"


class OntologyVersion(Base):
    """온톨로지 버전 관리"""
    __tablename__ = "ontology_versions"

    id = Column(Integer, primary_key=True, index=True)
    
    # 버전 정보
    version_number = Column(String, nullable=False, index=True)  # 1.0.0, 1.1.0, 2.0.0
    version_name = Column(String, nullable=True)  # 버전 이름 (예: "Initial Release")
    description = Column(Text, nullable=True)
    
    # 엔티티 정보
    entity_type = Column(SQLEnum(OntologyEntityType), nullable=False)
    entity_id = Column(Integer, nullable=False)  # class_id, property_id, relationship_id
    
    # 변경 내용 (JSON Diff)
    changes = Column(JSON, nullable=False)  # 변경된 필드들
    full_snapshot = Column(JSON, nullable=True)  # 전체 스냅샷 (옵션)
    
    # 생성 정보
    created_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    creator = relationship("User")
    
    def __repr__(self):
        return f"<OntologyVersion {self.version_number} - {self.entity_type}:{self.entity_id}>"
