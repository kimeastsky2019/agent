from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.models.collaboration import (
    Proposal,
    Review,
    Comment,
    Notification,
    CollaborationSpace,
    CollaborationSpaceMembership,
    CollaborationSpaceRole,
    CollaborationSpaceVisibility,
    ProposalStatus,
    ProposalType,
    ReviewDecision
)
from app.auth.security import get_current_active_user, require_reviewer
from app.models.audit import AuditLog, AuditAction

router = APIRouter(prefix="/proposals", tags=["협업"])


# Pydantic 스키마
class ProposalCreate(BaseModel):
    title: str
    description: str
    proposal_type: ProposalType
    entity_type: str
    entity_id: Optional[int] = None
    proposed_changes: dict
    rationale: Optional[str] = None
    impact_analysis: Optional[str] = None
    priority: str = "medium"
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    space_id: Optional[int] = None


class ProposalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    proposed_changes: Optional[dict] = None
    rationale: Optional[str] = None
    impact_analysis: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[ProposalStatus] = None
    space_id: Optional[int] = None


class ReviewCreate(BaseModel):
    decision: ReviewDecision
    comment: Optional[str] = None
    feedback: Optional[dict] = None
    conditions: Optional[str] = None


class CommentCreate(BaseModel):
    content: str
    parent_id: Optional[int] = None
    mentions: Optional[List[int]] = None


# 제안 관리
@router.get("")
async def list_proposals(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[ProposalStatus] = None,
    proposal_type: Optional[ProposalType] = None,
    author_id: Optional[int] = None,
    assigned_to: Optional[int] = None,
    space_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """제안 목록 조회"""
    
    query = db.query(Proposal)
    
    if status:
        query = query.filter(Proposal.status == status)
    
    if proposal_type:
        query = query.filter(Proposal.proposal_type == proposal_type)
    
    if author_id:
        query = query.filter(Proposal.author_id == author_id)
    
    if assigned_to:
        query = query.filter(Proposal.assigned_to == assigned_to)

    if space_id is not None:
        query = query.filter(Proposal.space_id == space_id)
    
    total = query.count()
    proposals = query.order_by(Proposal.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": [
            {
                "id": p.id,
                "title": p.title,
                "description": p.description[:200] if p.description else None,
                "proposal_type": p.proposal_type,
                "entity_type": p.entity_type,
                "status": p.status,
                "priority": p.priority,
                "category": p.category,
                "author_id": p.author_id,
                "current_approvals": p.current_approvals,
                "required_approvals": p.required_approvals,
                "space_id": p.space_id,
                "space_slug": p.space.slug if p.space else None,
                "space_onboarding_url": p.space.onboarding_url if p.space else None,
                "created_at": p.created_at,
                "updated_at": p.updated_at
            }
            for p in proposals
        ]
    }


@router.get("/{proposal_id}")
async def get_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """제안 상세 조회"""
    
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="제안을 찾을 수 없습니다"
        )
    
    # 리뷰 목록
    reviews = [
        {
            "id": r.id,
            "reviewer_id": r.reviewer_id,
            "reviewer_name": r.reviewer.full_name if r.reviewer else None,
            "decision": r.decision,
            "comment": r.comment,
            "created_at": r.created_at
        }
        for r in proposal.reviews
    ]
    
    # 댓글 목록
    comments = [
        {
            "id": c.id,
            "author_id": c.author_id,
            "author_name": c.author.full_name if c.author else None,
            "content": c.content,
            "parent_id": c.parent_id,
            "created_at": c.created_at
        }
        for c in proposal.comments
    ]
    
    return {
        "id": proposal.id,
        "title": proposal.title,
        "description": proposal.description,
        "proposal_type": proposal.proposal_type,
        "entity_type": proposal.entity_type,
        "entity_id": proposal.entity_id,
        "proposed_changes": proposal.proposed_changes,
        "current_state": proposal.current_state,
        "status": proposal.status,
        "priority": proposal.priority,
        "category": proposal.category,
        "tags": proposal.tags,
        "rationale": proposal.rationale,
        "impact_analysis": proposal.impact_analysis,
        "affected_entities": proposal.affected_entities,
        "required_approvals": proposal.required_approvals,
        "current_approvals": proposal.current_approvals,
        "author_id": proposal.author_id,
        "author_name": proposal.author.full_name if proposal.author else None,
        "assigned_to": proposal.assigned_to,
        "space_id": proposal.space_id,
        "space": {
            "id": proposal.space.id,
            "slug": proposal.space.slug,
            "name": proposal.space.name,
            "visibility": proposal.space.visibility,
            "onboarding_url": proposal.space.onboarding_url,
            "external_channel": proposal.space.external_channel,
        } if proposal.space else None,
        "deadline": proposal.deadline,
        "created_at": proposal.created_at,
        "updated_at": proposal.updated_at,
        "submitted_at": proposal.submitted_at,
        "resolved_at": proposal.resolved_at,
        "reviews": reviews,
        "comments": comments
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_proposal(
    data: ProposalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """제안 생성"""

    space = None
    if data.space_id is not None:
        space = db.query(CollaborationSpace).filter(CollaborationSpace.id == data.space_id).first()
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="협업 공간을 찾을 수 없습니다"
            )

        membership = db.query(CollaborationSpaceMembership).filter(
            CollaborationSpaceMembership.space_id == data.space_id,
            CollaborationSpaceMembership.user_id == current_user.id,
            CollaborationSpaceMembership.is_active.is_(True)
        ).first()

        if not membership:
            if space.visibility == CollaborationSpaceVisibility.PRIVATE and not current_user.has_admin_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="이 협업 공간에 제안을 생성할 권한이 없습니다"
                )

            # 공개 또는 커뮤니티 공간은 자동 참여 처리
            auto_role = CollaborationSpaceRole.CONTRIBUTOR
            if current_user.can_coordinate_spaces:
                auto_role = CollaborationSpaceRole.COORDINATOR

            membership = CollaborationSpaceMembership(
                space_id=space.id,
                user_id=current_user.id,
                role=auto_role,
                is_active=True
            )
            db.add(membership)
            db.flush()

    proposal = Proposal(
        title=data.title,
        description=data.description,
        proposal_type=data.proposal_type,
        entity_type=data.entity_type,
        entity_id=data.entity_id,
        proposed_changes=data.proposed_changes,
        rationale=data.rationale,
        impact_analysis=data.impact_analysis,
        priority=data.priority,
        category=data.category,
        tags=data.tags,
        author_id=current_user.id,
        status=ProposalStatus.DRAFT,
        space_id=data.space_id
    )
    
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    
    # 감사 로그
    audit_log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action=AuditAction.SUBMIT_PROPOSAL,
        resource_type="proposal",
        resource_id=proposal.id,
        description=f"Created proposal: {proposal.title}",
        success=True
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "id": proposal.id,
        "message": "제안이 생성되었습니다"
    }


@router.put("/{proposal_id}")
async def update_proposal(
    proposal_id: int,
    data: ProposalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """제안 수정"""
    
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="제안을 찾을 수 없습니다"
        )
    
    # 작성자 또는 관리자만 수정 가능
    if proposal.author_id != current_user.id and not current_user.has_admin_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="제안을 수정할 권한이 없습니다"
        )
    
    # 이미 승인된 제안은 수정 불가
    if proposal.status == ProposalStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="승인된 제안은 수정할 수 없습니다"
        )
    
    # 업데이트
    if data.title is not None:
        proposal.title = data.title
    if data.description is not None:
        proposal.description = data.description
    if data.proposed_changes is not None:
        proposal.proposed_changes = data.proposed_changes
    if data.rationale is not None:
        proposal.rationale = data.rationale
    if data.impact_analysis is not None:
        proposal.impact_analysis = data.impact_analysis
    if data.priority is not None:
        proposal.priority = data.priority
    if data.category is not None:
        proposal.category = data.category
    if data.tags is not None:
        proposal.tags = data.tags
    if data.status is not None:
        proposal.status = data.status
        if data.status == ProposalStatus.SUBMITTED:
            proposal.submitted_at = datetime.utcnow()
    if data.space_id is not None and data.space_id != proposal.space_id:
        space = db.query(CollaborationSpace).filter(CollaborationSpace.id == data.space_id).first()
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="협업 공간을 찾을 수 없습니다"
            )

        membership = db.query(CollaborationSpaceMembership).filter(
            CollaborationSpaceMembership.space_id == data.space_id,
            CollaborationSpaceMembership.user_id == current_user.id,
            CollaborationSpaceMembership.is_active.is_(True)
        ).first()

        if not membership and space.visibility == CollaborationSpaceVisibility.PRIVATE and not current_user.has_admin_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 협업 공간에 접근할 권한이 없습니다"
            )

        if not membership and space.visibility != CollaborationSpaceVisibility.PRIVATE:
            membership = CollaborationSpaceMembership(
                space_id=space.id,
                user_id=current_user.id,
                role=CollaborationSpaceRole.COORDINATOR if current_user.can_coordinate_spaces else CollaborationSpaceRole.CONTRIBUTOR,
                is_active=True
            )
            db.add(membership)

        proposal.space_id = data.space_id

    db.commit()
    
    return {"message": "제안이 업데이트되었습니다"}


@router.post("/{proposal_id}/submit")
async def submit_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """제안 제출"""
    
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="제안을 찾을 수 없습니다"
        )
    
    if proposal.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="제안을 제출할 권한이 없습니다"
        )
    
    if proposal.status != ProposalStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="초안 상태의 제안만 제출할 수 있습니다"
        )
    
    proposal.status = ProposalStatus.SUBMITTED
    proposal.submitted_at = datetime.utcnow()
    db.commit()
    
    # TODO: 리뷰어들에게 알림 전송
    
    return {"message": "제안이 제출되었습니다"}


# 리뷰 관리
@router.post("/{proposal_id}/reviews", status_code=status.HTTP_201_CREATED)
async def create_review(
    proposal_id: int,
    data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_reviewer)
):
    """리뷰 작성"""
    
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="제안을 찾을 수 없습니다"
        )
    
    # 이미 리뷰한 경우 체크
    existing_review = db.query(Review).filter(
        Review.proposal_id == proposal_id,
        Review.reviewer_id == current_user.id
    ).first()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 리뷰를 작성했습니다"
        )
    
    # 리뷰 생성
    review = Review(
        proposal_id=proposal_id,
        reviewer_id=current_user.id,
        decision=data.decision,
        comment=data.comment,
        feedback=data.feedback,
        conditions=data.conditions
    )
    
    db.add(review)
    
    # 승인 카운터 업데이트
    if data.decision == ReviewDecision.APPROVE:
        proposal.current_approvals += 1
        proposal.status = ProposalStatus.UNDER_REVIEW
        
        # 필요한 승인 수 달성 시
        if proposal.current_approvals >= proposal.required_approvals:
            proposal.status = ProposalStatus.APPROVED
            proposal.resolved_at = datetime.utcnow()
    
    elif data.decision == ReviewDecision.REJECT:
        proposal.status = ProposalStatus.REJECTED
        proposal.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(review)
    
    # 감사 로그
    audit_log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action=AuditAction.REVIEW_PROPOSAL,
        resource_type="proposal",
        resource_id=proposal.id,
        description=f"Reviewed proposal: {proposal.title} - {data.decision}",
        success=True
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "id": review.id,
        "message": "리뷰가 작성되었습니다"
    }


# 댓글 관리
@router.post("/{proposal_id}/comments", status_code=status.HTTP_201_CREATED)
async def create_comment(
    proposal_id: int,
    data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """댓글 작성"""
    
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="제안을 찾을 수 없습니다"
        )
    
    comment = Comment(
        proposal_id=proposal_id,
        author_id=current_user.id,
        content=data.content,
        parent_id=data.parent_id,
        mentions=data.mentions
    )
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    # TODO: 멘션된 사용자들에게 알림
    
    return {
        "id": comment.id,
        "message": "댓글이 작성되었습니다"
    }


@router.get("/{proposal_id}/comments")
async def list_comments(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """제안의 댓글 목록 조회"""
    
    comments = db.query(Comment).filter(
        Comment.proposal_id == proposal_id,
        Comment.parent_id.is_(None)  # 최상위 댓글만
    ).order_by(Comment.created_at).all()
    
    def format_comment(comment):
        return {
            "id": comment.id,
            "author_id": comment.author_id,
            "author_name": comment.author.full_name if comment.author else None,
            "content": comment.content,
            "created_at": comment.created_at,
            "replies": [format_comment(reply) for reply in comment.replies]
        }
    
    return {
        "items": [format_comment(c) for c in comments]
    }


# 통계
@router.get("/stats/summary")
async def get_proposal_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """제안 통계"""
    
    total = db.query(Proposal).count()
    draft = db.query(Proposal).filter(Proposal.status == ProposalStatus.DRAFT).count()
    submitted = db.query(Proposal).filter(Proposal.status == ProposalStatus.SUBMITTED).count()
    under_review = db.query(Proposal).filter(Proposal.status == ProposalStatus.UNDER_REVIEW).count()
    approved = db.query(Proposal).filter(Proposal.status == ProposalStatus.APPROVED).count()
    rejected = db.query(Proposal).filter(Proposal.status == ProposalStatus.REJECTED).count()
    
    my_proposals = db.query(Proposal).filter(Proposal.author_id == current_user.id).count()
    my_pending_reviews = db.query(Proposal).filter(
        Proposal.status.in_([ProposalStatus.SUBMITTED, ProposalStatus.UNDER_REVIEW])
    ).count()
    
    return {
        "total": total,
        "by_status": {
            "draft": draft,
            "submitted": submitted,
            "under_review": under_review,
            "approved": approved,
            "rejected": rejected
        },
        "my_proposals": my_proposals,
        "my_pending_reviews": my_pending_reviews
    }
