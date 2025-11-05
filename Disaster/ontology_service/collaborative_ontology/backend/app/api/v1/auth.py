from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.auth.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    get_current_active_user
)
from app.models.audit import AuditLog, AuditAction
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["인증"])


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str
    organization: str = None
    department: str = None


@router.post("/register", response_model=TokenResponse)
async def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """새 사용자 등록"""
    
    # 이메일 중복 체크
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다"
        )
    
    # 사용자명 중복 체크
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용중인 사용자명입니다"
        )
    
    # 사용자 생성
    user = User(
        email=data.email,
        username=data.username,
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
        organization=data.organization,
        department=data.department,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 감사 로그
    audit_log = AuditLog(
        user_id=user.id,
        username=user.username,
        action=AuditAction.CREATE,
        resource_type="user",
        resource_id=user.id,
        description=f"New user registered: {user.email}",
        success=True
    )
    db.add(audit_log)
    db.commit()
    
    # 토큰 생성
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name
        }
    }


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """로그인"""
    
    # 사용자 조회 (이메일 또는 사용자명)
    user = db.query(User).filter(
        (User.email == form_data.username) | (User.username == form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        # 실패 감사 로그
        audit_log = AuditLog(
            username=form_data.username,
            action=AuditAction.FAILED_LOGIN,
            resource_type="auth",
            description=f"Failed login attempt: {form_data.username}",
            success=False
        )
        db.add(audit_log)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 계정입니다"
        )
    
    # 마지막 로그인 시간 업데이트
    user.last_login = datetime.utcnow()
    db.commit()
    
    # 성공 감사 로그
    audit_log = AuditLog(
        user_id=user.id,
        username=user.username,
        action=AuditAction.LOGIN,
        resource_type="auth",
        description=f"User logged in: {user.email}",
        success=True
    )
    db.add(audit_log)
    db.commit()
    
    # 토큰 생성
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "roles": user.roles,
            "organization": user.organization
        }
    }


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """현재 사용자 정보 조회"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "roles": current_user.roles,
        "organization": current_user.organization,
        "department": current_user.department,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """로그아웃"""
    
    # 감사 로그
    audit_log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action=AuditAction.LOGOUT,
        resource_type="auth",
        description=f"User logged out: {current_user.email}",
        success=True
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "로그아웃되었습니다"}
