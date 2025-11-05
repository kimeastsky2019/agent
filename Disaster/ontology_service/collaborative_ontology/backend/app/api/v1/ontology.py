from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.db.session import get_db
from app.models.user import User
from app.models.ontology import (
    OntologyClass,
    OntologyProperty,
    OntologyRelationship,
    OntologyStatus
)
from app.auth.security import get_current_active_user, require_editor
from app.models.audit import AuditLog, AuditAction

router = APIRouter(prefix="/ontology", tags=["온톨로지"])


# Pydantic 스키마
class OntologyClassCreate(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    namespace: str = "energy"
    metadata: Optional[dict] = None
    tags: Optional[List[str]] = None


class OntologyClassUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    metadata: Optional[dict] = None
    tags: Optional[List[str]] = None
    status: Optional[OntologyStatus] = None


class PropertyCreate(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    data_type: str
    unit: Optional[str] = None
    is_required: bool = False
    default_value: Optional[str] = None
    constraints: Optional[dict] = None


class RelationshipCreate(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    target_class_id: int
    relationship_type: str
    cardinality: str = "one-to-many"
    is_bidirectional: bool = False
    inverse_name: Optional[str] = None


# 온톨로지 클래스 관리
@router.get("/classes")
async def list_classes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    namespace: Optional[str] = None,
    status: Optional[OntologyStatus] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """온톨로지 클래스 목록 조회"""
    
    query = db.query(OntologyClass)
    
    if namespace:
        query = query.filter(OntologyClass.namespace == namespace)
    
    if status:
        query = query.filter(OntologyClass.status == status)
    
    if search:
        query = query.filter(
            (OntologyClass.name.ilike(f"%{search}%")) |
            (OntologyClass.display_name.ilike(f"%{search}%")) |
            (OntologyClass.description.ilike(f"%{search}%"))
        )
    
    total = query.count()
    classes = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": [
            {
                "id": cls.id,
                "name": cls.name,
                "display_name": cls.display_name,
                "description": cls.description,
                "namespace": cls.namespace,
                "parent_id": cls.parent_id,
                "status": cls.status,
                "created_at": cls.created_at,
                "updated_at": cls.updated_at
            }
            for cls in classes
        ]
    }


@router.get("/classes/{class_id}")
async def get_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """온톨로지 클래스 상세 조회"""
    
    ontology_class = db.query(OntologyClass).filter(OntologyClass.id == class_id).first()
    
    if not ontology_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="클래스를 찾을 수 없습니다"
        )
    
    return {
        "id": ontology_class.id,
        "name": ontology_class.name,
        "display_name": ontology_class.display_name,
        "description": ontology_class.description,
        "namespace": ontology_class.namespace,
        "uri": ontology_class.uri,
        "version": ontology_class.version,
        "status": ontology_class.status,
        "parent_id": ontology_class.parent_id,
        "metadata": ontology_class.metadata,
        "tags": ontology_class.tags,
        "properties": [
            {
                "id": prop.id,
                "name": prop.name,
                "display_name": prop.display_name,
                "data_type": prop.data_type,
                "unit": prop.unit,
                "is_required": prop.is_required
            }
            for prop in ontology_class.properties
        ],
        "relationships": [
            {
                "id": rel.id,
                "name": rel.name,
                "display_name": rel.display_name,
                "target_class_id": rel.target_class_id,
                "relationship_type": rel.relationship_type
            }
            for rel in ontology_class.relationships_as_source
        ],
        "created_by": ontology_class.created_by,
        "updated_by": ontology_class.updated_by,
        "created_at": ontology_class.created_at,
        "updated_at": ontology_class.updated_at
    }


@router.post("/classes", status_code=status.HTTP_201_CREATED)
async def create_class(
    data: OntologyClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor)
):
    """온톨로지 클래스 생성"""
    
    # 중복 체크
    existing = db.query(OntologyClass).filter(
        OntologyClass.name == data.name,
        OntologyClass.namespace == data.namespace
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="같은 이름의 클래스가 이미 존재합니다"
        )
    
    # URI 생성
    uri = f"urn:{data.namespace}:{data.name}"
    
    # 클래스 생성
    ontology_class = OntologyClass(
        name=data.name,
        display_name=data.display_name,
        description=data.description,
        parent_id=data.parent_id,
        namespace=data.namespace,
        uri=uri,
        metadata=data.metadata,
        tags=data.tags,
        created_by=current_user.id,
        status=OntologyStatus.DRAFT
    )
    
    db.add(ontology_class)
    db.commit()
    db.refresh(ontology_class)
    
    # 감사 로그
    audit_log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action=AuditAction.CREATE,
        resource_type="ontology_class",
        resource_id=ontology_class.id,
        description=f"Created class: {ontology_class.name}",
        success=True
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "id": ontology_class.id,
        "message": "클래스가 생성되었습니다"
    }


@router.put("/classes/{class_id}")
async def update_class(
    class_id: int,
    data: OntologyClassUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor)
):
    """온톨로지 클래스 수정"""
    
    ontology_class = db.query(OntologyClass).filter(OntologyClass.id == class_id).first()
    
    if not ontology_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="클래스를 찾을 수 없습니다"
        )
    
    # 변경사항 추적
    changes = {}
    
    if data.display_name is not None:
        changes["display_name"] = {"old": ontology_class.display_name, "new": data.display_name}
        ontology_class.display_name = data.display_name
    
    if data.description is not None:
        changes["description"] = {"old": ontology_class.description, "new": data.description}
        ontology_class.description = data.description
    
    if data.parent_id is not None:
        changes["parent_id"] = {"old": ontology_class.parent_id, "new": data.parent_id}
        ontology_class.parent_id = data.parent_id
    
    if data.metadata is not None:
        ontology_class.metadata = data.metadata
    
    if data.tags is not None:
        ontology_class.tags = data.tags
    
    if data.status is not None:
        changes["status"] = {"old": ontology_class.status, "new": data.status}
        ontology_class.status = data.status
    
    ontology_class.updated_by = current_user.id
    db.commit()
    
    # 감사 로그
    audit_log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action=AuditAction.UPDATE,
        resource_type="ontology_class",
        resource_id=ontology_class.id,
        description=f"Updated class: {ontology_class.name}",
        changes=changes,
        success=True
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "클래스가 업데이트되었습니다"}


@router.delete("/classes/{class_id}")
async def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor)
):
    """온톨로지 클래스 삭제"""
    
    ontology_class = db.query(OntologyClass).filter(OntologyClass.id == class_id).first()
    
    if not ontology_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="클래스를 찾을 수 없습니다"
        )
    
    # 감사 로그
    audit_log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action=AuditAction.DELETE,
        resource_type="ontology_class",
        resource_id=ontology_class.id,
        description=f"Deleted class: {ontology_class.name}",
        success=True
    )
    db.add(audit_log)
    
    db.delete(ontology_class)
    db.commit()
    
    return {"message": "클래스가 삭제되었습니다"}


# 속성 관리
@router.post("/classes/{class_id}/properties", status_code=status.HTTP_201_CREATED)
async def create_property(
    class_id: int,
    data: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor)
):
    """온톨로지 속성 생성"""
    
    # 클래스 존재 확인
    ontology_class = db.query(OntologyClass).filter(OntologyClass.id == class_id).first()
    
    if not ontology_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="클래스를 찾을 수 없습니다"
        )
    
    # 속성 생성
    prop = OntologyProperty(
        name=data.name,
        display_name=data.display_name,
        description=data.description,
        class_id=class_id,
        data_type=data.data_type,
        unit=data.unit,
        is_required=data.is_required,
        default_value=data.default_value,
        constraints=data.constraints,
        created_by=current_user.id,
        status=OntologyStatus.DRAFT
    )
    
    db.add(prop)
    db.commit()
    db.refresh(prop)
    
    return {
        "id": prop.id,
        "message": "속성이 생성되었습니다"
    }


# 관계 관리
@router.post("/classes/{class_id}/relationships", status_code=status.HTTP_201_CREATED)
async def create_relationship(
    class_id: int,
    data: RelationshipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor)
):
    """온톨로지 관계 생성"""
    
    # 클래스 존재 확인
    source_class = db.query(OntologyClass).filter(OntologyClass.id == class_id).first()
    target_class = db.query(OntologyClass).filter(OntologyClass.id == data.target_class_id).first()
    
    if not source_class or not target_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="클래스를 찾을 수 없습니다"
        )
    
    # 관계 생성
    rel = OntologyRelationship(
        name=data.name,
        display_name=data.display_name,
        description=data.description,
        source_class_id=class_id,
        target_class_id=data.target_class_id,
        relationship_type=data.relationship_type,
        cardinality=data.cardinality,
        is_bidirectional=data.is_bidirectional,
        inverse_name=data.inverse_name,
        created_by=current_user.id,
        status=OntologyStatus.DRAFT
    )
    
    db.add(rel)
    db.commit()
    db.refresh(rel)
    
    return {
        "id": rel.id,
        "message": "관계가 생성되었습니다"
    }
