from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.collaboration import (
    CollaborationSpace,
    CollaborationSpaceMembership,
    CollaborationSpaceRole,
    CollaborationSpaceVisibility,
)
from app.auth.security import get_current_active_user

router = APIRouter(prefix="/spaces", tags=["협업 공간"])


class SpaceCreate(BaseModel):
    slug: str = Field(..., description="고유 식별자 (영문, 대시 허용)")
    name: str
    description: Optional[str] = None
    mission: Optional[str] = None
    domain_focus: Optional[str] = None
    visibility: CollaborationSpaceVisibility = CollaborationSpaceVisibility.PUBLIC
    onboarding_url: Optional[str] = Field(
        default="https://agent.gngmeta.com/co-work",
        description="팔런티어 온보딩 페이지"
    )
    external_channel: Optional[str] = Field(
        default="https://agent.gngmeta.com/co-work",
        description="협업 채널 (예: Slack, Teams)"
    )
    tags: Optional[List[str]] = None
    profile: Optional[dict] = None


class SpaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    mission: Optional[str] = None
    domain_focus: Optional[str] = None
    visibility: Optional[CollaborationSpaceVisibility] = None
    onboarding_url: Optional[str] = None
    external_channel: Optional[str] = None
    tags: Optional[List[str]] = None
    profile: Optional[dict] = None


class SpaceMembershipUpdate(BaseModel):
    role: Optional[CollaborationSpaceRole] = None
    responsibilities: Optional[str] = None
    expertise_tags: Optional[List[str]] = None
    is_core_team: Optional[bool] = None


class MemberAddRequest(BaseModel):
    user_id: int
    role: CollaborationSpaceRole = CollaborationSpaceRole.CONTRIBUTOR
    responsibilities: Optional[str] = None
    expertise_tags: Optional[List[str]] = None
    is_core_team: bool = False


@router.get("")
async def list_spaces(
    search: Optional[str] = None,
    domain_focus: Optional[str] = None,
    visibility: Optional[CollaborationSpaceVisibility] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """사용자가 접근 가능한 협업 공간 목록"""

    query = db.query(CollaborationSpace)

    if visibility:
        query = query.filter(CollaborationSpace.visibility == visibility)

    spaces = query.order_by(CollaborationSpace.created_at.desc()).all()

    visible_spaces = []
    for space in spaces:
        membership = db.query(CollaborationSpaceMembership).filter(
            CollaborationSpaceMembership.space_id == space.id,
            CollaborationSpaceMembership.user_id == current_user.id,
            CollaborationSpaceMembership.is_active.is_(True)
        ).first()

        if space.visibility == CollaborationSpaceVisibility.PRIVATE and not (
            membership or current_user.has_admin_role
        ):
            continue

        if search:
            term = search.lower()
            if not (
                term in (space.name or "").lower()
                or term in (space.slug or "").lower()
                or term in (space.description or "").lower()
            ):
                continue

        if domain_focus and (space.domain_focus or "").lower() != domain_focus.lower():
            continue

        visible_spaces.append(
            {
                "id": space.id,
                "slug": space.slug,
                "name": space.name,
                "description": space.description,
                "mission": space.mission,
                "domain_focus": space.domain_focus,
                "visibility": space.visibility,
                "tags": space.tags,
                "onboarding_url": space.onboarding_url,
                "external_channel": space.external_channel,
                "profile": space.profile,
                "member": {
                    "is_member": membership is not None,
                    "role": membership.role if membership else None,
                    "joined_at": membership.joined_at if membership else None,
                },
                "created_at": space.created_at,
                "updated_at": space.updated_at,
            }
        )

    return {"items": visible_spaces, "total": len(visible_spaces)}


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_space(
    data: SpaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """새 협업 공간 생성"""

    if not current_user.can_coordinate_spaces:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="협업 공간을 생성할 권한이 없습니다"
        )

    existing = db.query(CollaborationSpace).filter(CollaborationSpace.slug == data.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 슬러그입니다"
        )

    space = CollaborationSpace(
        slug=data.slug,
        name=data.name,
        description=data.description,
        mission=data.mission,
        domain_focus=data.domain_focus,
        visibility=data.visibility,
        onboarding_url=data.onboarding_url,
        external_channel=data.external_channel,
        tags=data.tags,
        profile=data.profile,
        created_by=current_user.id,
        updated_by=current_user.id,
    )

    db.add(space)
    db.flush()

    membership = CollaborationSpaceMembership(
        space_id=space.id,
        user_id=current_user.id,
        role=CollaborationSpaceRole.COORDINATOR,
        responsibilities="공간 생성자",
        is_core_team=True,
        is_active=True
    )
    db.add(membership)
    db.commit()
    db.refresh(space)

    return {
        "id": space.id,
        "slug": space.slug,
        "name": space.name,
        "message": "협업 공간이 생성되었습니다"
    }


@router.get("/{space_id}")
async def get_space(
    space_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """협업 공간 상세"""

    space = db.query(CollaborationSpace).filter(CollaborationSpace.id == space_id).first()
    if not space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="협업 공간을 찾을 수 없습니다")

    membership = db.query(CollaborationSpaceMembership).filter(
        CollaborationSpaceMembership.space_id == space.id,
        CollaborationSpaceMembership.user_id == current_user.id,
        CollaborationSpaceMembership.is_active.is_(True)
    ).first()

    if space.visibility == CollaborationSpaceVisibility.PRIVATE and not (
        membership or current_user.has_admin_role
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="접근 권한이 없습니다")

    coordinators = db.query(CollaborationSpaceMembership).filter(
        CollaborationSpaceMembership.space_id == space.id,
        CollaborationSpaceMembership.role == CollaborationSpaceRole.COORDINATOR,
        CollaborationSpaceMembership.is_active.is_(True)
    ).count()

    contributors = db.query(CollaborationSpaceMembership).filter(
        CollaborationSpaceMembership.space_id == space.id,
        CollaborationSpaceMembership.is_active.is_(True)
    ).count()

    return {
        "id": space.id,
        "slug": space.slug,
        "name": space.name,
        "description": space.description,
        "mission": space.mission,
        "domain_focus": space.domain_focus,
        "visibility": space.visibility,
        "tags": space.tags,
        "onboarding_url": space.onboarding_url,
        "external_channel": space.external_channel,
        "profile": space.profile,
        "created_at": space.created_at,
        "updated_at": space.updated_at,
        "membership": {
            "is_member": membership is not None,
            "role": membership.role if membership else None,
            "joined_at": membership.joined_at if membership else None,
        },
        "metrics": {
            "coordinator_count": coordinators,
            "member_count": contributors,
        }
    }


@router.patch("/{space_id}")
async def update_space(
    space_id: int,
    data: SpaceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """협업 공간 정보 수정"""

    space = db.query(CollaborationSpace).filter(CollaborationSpace.id == space_id).first()
    if not space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="협업 공간을 찾을 수 없습니다")

    membership = db.query(CollaborationSpaceMembership).filter(
        CollaborationSpaceMembership.space_id == space.id,
        CollaborationSpaceMembership.user_id == current_user.id,
        CollaborationSpaceMembership.is_active.is_(True)
    ).first()

    if not (
        current_user.has_admin_role
        or (membership and membership.role == CollaborationSpaceRole.COORDINATOR)
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="수정 권한이 없습니다")

    if data.name is not None:
        space.name = data.name
    if data.description is not None:
        space.description = data.description
    if data.mission is not None:
        space.mission = data.mission
    if data.domain_focus is not None:
        space.domain_focus = data.domain_focus
    if data.visibility is not None:
        space.visibility = data.visibility
    if data.onboarding_url is not None:
        space.onboarding_url = data.onboarding_url
    if data.external_channel is not None:
        space.external_channel = data.external_channel
    if data.tags is not None:
        space.tags = data.tags
    if data.profile is not None:
        space.profile = data.profile

    space.updated_by = current_user.id
    db.commit()

    return {"message": "협업 공간이 업데이트되었습니다"}


@router.post("/{space_id}/join", status_code=status.HTTP_200_OK)
async def join_space(
    space_id: int,
    role: CollaborationSpaceRole = CollaborationSpaceRole.CONTRIBUTOR,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """협업 공간 참여"""

    space = db.query(CollaborationSpace).filter(CollaborationSpace.id == space_id).first()
    if not space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="협업 공간을 찾을 수 없습니다")

    membership = db.query(CollaborationSpaceMembership).filter(
        CollaborationSpaceMembership.space_id == space.id,
        CollaborationSpaceMembership.user_id == current_user.id
    ).first()

    if membership and membership.is_active:
        return {"message": "이미 참여 중입니다"}

    if space.visibility == CollaborationSpaceVisibility.PRIVATE and not current_user.has_admin_role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="초대가 필요한 공간입니다")

    if membership:
        membership.is_active = True
        membership.role = role
        membership.joined_at = datetime.utcnow()
    else:
        membership = CollaborationSpaceMembership(
            space_id=space.id,
            user_id=current_user.id,
            role=role,
            is_active=True,
        )
        db.add(membership)

    db.commit()

    return {"message": "협업 공간에 참여했습니다"}


@router.get("/{space_id}/members")
async def list_members(
    space_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """협업 공간 참여자 목록"""

    space = db.query(CollaborationSpace).filter(CollaborationSpace.id == space_id).first()
    if not space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="협업 공간을 찾을 수 없습니다")

    membership = db.query(CollaborationSpaceMembership).filter(
        CollaborationSpaceMembership.space_id == space.id,
        CollaborationSpaceMembership.user_id == current_user.id,
        CollaborationSpaceMembership.is_active.is_(True)
    ).first()

    if space.visibility == CollaborationSpaceVisibility.PRIVATE and not (
        membership or current_user.has_admin_role
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="접근 권한이 없습니다")

    members = db.query(CollaborationSpaceMembership).filter(
        CollaborationSpaceMembership.space_id == space.id,
        CollaborationSpaceMembership.is_active.is_(True)
    ).order_by(CollaborationSpaceMembership.joined_at.asc()).all()

    return {
        "items": [
            {
                "user_id": member.user_id,
                "role": member.role,
                "responsibilities": member.responsibilities,
                "expertise_tags": member.expertise_tags,
                "is_core_team": member.is_core_team,
                "joined_at": member.joined_at,
                "contribution_hours": member.contribution_hours,
            }
            for member in members
        ]
    }


@router.post("/{space_id}/members", status_code=status.HTTP_201_CREATED)
async def add_member(
    space_id: int,
    payload: MemberAddRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """협업 공간에 멤버 추가 (코디네이터 전용)"""

    space = db.query(CollaborationSpace).filter(CollaborationSpace.id == space_id).first()
    if not space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="협업 공간을 찾을 수 없습니다")

    membership = db.query(CollaborationSpaceMembership).filter(
        CollaborationSpaceMembership.space_id == space.id,
        CollaborationSpaceMembership.user_id == current_user.id,
        CollaborationSpaceMembership.is_active.is_(True)
    ).first()

    if not (
        current_user.has_admin_role
        or (membership and membership.role == CollaborationSpaceRole.COORDINATOR)
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="멤버를 추가할 권한이 없습니다")

    target = db.query(CollaborationSpaceMembership).filter(
        CollaborationSpaceMembership.space_id == space.id,
        CollaborationSpaceMembership.user_id == payload.user_id
    ).first()

    if target:
        target.role = payload.role
        target.responsibilities = payload.responsibilities
        target.expertise_tags = payload.expertise_tags
        target.is_core_team = payload.is_core_team
        target.is_active = True
        target.joined_at = target.joined_at or datetime.utcnow()
    else:
        target = CollaborationSpaceMembership(
            space_id=space.id,
            user_id=payload.user_id,
            role=payload.role,
            responsibilities=payload.responsibilities,
            expertise_tags=payload.expertise_tags,
            is_core_team=payload.is_core_team,
            is_active=True
        )
        db.add(target)

    db.commit()

    return {"message": "멤버가 추가되었습니다"}


@router.patch("/{space_id}/members/{user_id}")
async def update_member(
    space_id: int,
    user_id: int,
    data: SpaceMembershipUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """협업 공간 멤버십 업데이트"""

    space = db.query(CollaborationSpace).filter(CollaborationSpace.id == space_id).first()
    if not space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="협업 공간을 찾을 수 없습니다")

    membership = db.query(CollaborationSpaceMembership).filter(
        CollaborationSpaceMembership.space_id == space.id,
        CollaborationSpaceMembership.user_id == current_user.id,
        CollaborationSpaceMembership.is_active.is_(True)
    ).first()

    if not (
        current_user.has_admin_role
        or (membership and membership.role == CollaborationSpaceRole.COORDINATOR)
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="멤버를 수정할 권한이 없습니다")

    target = db.query(CollaborationSpaceMembership).filter(
        CollaborationSpaceMembership.space_id == space.id,
        CollaborationSpaceMembership.user_id == user_id
    ).first()

    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="멤버십을 찾을 수 없습니다")

    if data.role is not None:
        target.role = data.role
    if data.responsibilities is not None:
        target.responsibilities = data.responsibilities
    if data.expertise_tags is not None:
        target.expertise_tags = data.expertise_tags
    if data.is_core_team is not None:
        target.is_core_team = data.is_core_team

    db.commit()

    return {"message": "멤버십이 업데이트되었습니다"}

