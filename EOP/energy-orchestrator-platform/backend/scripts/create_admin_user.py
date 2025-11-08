#!/usr/bin/env python3
"""
초기 관리자 사용자 생성 스크립트

사용법:
    python scripts/create_admin_user.py
    python scripts/create_admin_user.py --email admin@example.com --password secure_password
"""

import sys
import os
import argparse
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from src.database import SessionLocal, engine, Base
from src.models.user import User, UserRole
from src.config import settings
import getpass

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_admin_user(email: str, password: str, full_name: str = None) -> bool:
    """관리자 사용자 생성"""
    # 데이터베이스 테이블 생성
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        # 기존 사용자 확인
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"❌ 사용자가 이미 존재합니다: {email}")
            if existing_user.role == UserRole.ADMIN:
                print(f"   이미 관리자 권한을 가지고 있습니다.")
            else:
                # 일반 사용자를 관리자로 승격
                response = input(f"   기존 사용자를 관리자로 승격하시겠습니까? (y/n): ")
                if response.lower() == 'y':
                    existing_user.role = UserRole.ADMIN
                    existing_user.is_active = True
                    db.commit()
                    print(f"✅ 사용자가 관리자로 승격되었습니다: {email}")
                    return True
            return False
        
        # 비밀번호 해싱
        hashed_password = pwd_context.hash(password)
        
        # 관리자 사용자 생성
        admin_user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name or "Administrator",
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"✅ 관리자 사용자가 생성되었습니다:")
        print(f"   이메일: {email}")
        print(f"   이름: {admin_user.full_name}")
        print(f"   역할: {admin_user.role.value}")
        print(f"   ID: {admin_user.id}")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ 오류 발생: {e}")
        return False
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="초기 관리자 사용자 생성")
    parser.add_argument(
        "--email",
        type=str,
        default=None,
        help="관리자 이메일 주소"
    )
    parser.add_argument(
        "--password",
        type=str,
        default=None,
        help="관리자 비밀번호 (보안상 권장하지 않음)"
    )
    parser.add_argument(
        "--full-name",
        type=str,
        default=None,
        help="관리자 이름"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("관리자 사용자 생성 스크립트")
    print("=" * 60)
    
    # 이메일 입력
    if args.email:
        email = args.email
    else:
        email = input("관리자 이메일 주소를 입력하세요: ").strip()
        if not email:
            print("❌ 이메일 주소는 필수입니다.")
            sys.exit(1)
    
    # 비밀번호 입력
    if args.password:
        password = args.password
    else:
        password = getpass.getpass("관리자 비밀번호를 입력하세요: ")
        if not password:
            print("❌ 비밀번호는 필수입니다.")
            sys.exit(1)
        
        password_confirm = getpass.getpass("비밀번호를 다시 입력하세요: ")
        if password != password_confirm:
            print("❌ 비밀번호가 일치하지 않습니다.")
            sys.exit(1)
    
    # 이름 입력
    full_name = args.full_name
    if not full_name:
        full_name = input("이름을 입력하세요 (선택사항): ").strip() or None
    
    # 관리자 사용자 생성
    success = create_admin_user(email, password, full_name)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ 관리자 사용자 생성이 완료되었습니다.")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ 관리자 사용자 생성에 실패했습니다.")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()

