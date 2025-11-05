#!/usr/bin/env python3
"""초기 데이터 생성 스크립트"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.models.ontology import OntologyClass, OntologyProperty, OntologyStatus
from app.auth.security import get_password_hash
from app.core.config import settings


def create_initial_users(db: Session):
    """초기 사용자 생성"""
    
    print("🔐 Creating initial users...")
    
    # 슈퍼유저 생성
    admin = db.query(User).filter(User.email == settings.FIRST_SUPERUSER_EMAIL).first()
    if not admin:
        admin = User(
            email=settings.FIRST_SUPERUSER_EMAIL,
            username=settings.FIRST_SUPERUSER_USERNAME,
            hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            full_name="System Administrator",
            is_active=True,
            is_superuser=True,
            organization="GnG International"
        )
        db.add(admin)
        print(f"  ✅ Created admin user: {admin.email}")
    else:
        print(f"  ⏭️  Admin user already exists: {admin.email}")
    
    # 샘플 사용자들 생성
    sample_users = [
        {
            "email": "editor@gnginternational.com",
            "username": "ontology_editor",
            "password": "editor123",
            "full_name": "온톨로지 편집자",
            "role": UserRole.ONTOLOGY_EDITOR,
            "organization": "GnG International",
            "department": "Data Engineering"
        },
        {
            "email": "expert@gnginternational.com",
            "username": "domain_expert",
            "password": "expert123",
            "full_name": "도메인 전문가",
            "role": UserRole.DOMAIN_EXPERT,
            "organization": "GnG International",
            "department": "Energy Systems"
        },
        {
            "email": "provider@kepco.com",
            "username": "energy_provider",
            "password": "provider123",
            "full_name": "에너지 공급자",
            "role": UserRole.ENERGY_PROVIDER,
            "organization": "KEPCO",
            "department": "Smart Grid"
        }
    ]
    
    for user_data in sample_users:
        user = db.query(User).filter(User.email == user_data["email"]).first()
        if not user:
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                hashed_password=get_password_hash(user_data["password"]),
                full_name=user_data["full_name"],
                is_active=True,
                organization=user_data["organization"],
                department=user_data.get("department")
            )
            # 역할 할당
            user.roles = [user_data["role"]]
            db.add(user)
            print(f"  ✅ Created user: {user.email} ({user_data['role']})")
        else:
            print(f"  ⏭️  User already exists: {user.email}")
    
    db.commit()
    print("✅ Users created successfully\n")


def create_initial_ontology(db: Session):
    """초기 온톨로지 생성"""
    
    print("📚 Creating initial ontology...")
    
    # 기본 에너지 클래스들
    base_classes = [
        {
            "name": "EnergyResource",
            "display_name": "에너지 자원",
            "description": "모든 에너지 자원의 기본 클래스",
            "namespace": "energy"
        },
        {
            "name": "SolarPanel",
            "display_name": "태양광 패널",
            "description": "태양 에너지를 전기로 변환하는 장치",
            "namespace": "energy",
            "parent_name": "EnergyResource"
        },
        {
            "name": "WindTurbine",
            "display_name": "풍력 터빈",
            "description": "바람 에너지를 전기로 변환하는 장치",
            "namespace": "energy",
            "parent_name": "EnergyResource"
        },
        {
            "name": "Battery",
            "display_name": "배터리",
            "description": "전기 에너지 저장 장치",
            "namespace": "energy"
        },
        {
            "name": "EnergyStorage",
            "display_name": "에너지 저장 시스템",
            "description": "에너지를 저장하는 시스템",
            "namespace": "energy"
        },
        {
            "name": "SmartMeter",
            "display_name": "스마트 미터",
            "description": "전력 사용량을 측정하고 모니터링하는 장치",
            "namespace": "energy"
        }
    ]
    
    created_classes = {}
    
    for class_data in base_classes:
        cls = db.query(OntologyClass).filter(
            OntologyClass.name == class_data["name"],
            OntologyClass.namespace == class_data["namespace"]
        ).first()
        
        if not cls:
            parent_id = None
            if "parent_name" in class_data:
                parent = created_classes.get(class_data["parent_name"])
                if parent:
                    parent_id = parent.id
            
            uri = f"urn:{class_data['namespace']}:{class_data['name']}"
            
            cls = OntologyClass(
                name=class_data["name"],
                display_name=class_data["display_name"],
                description=class_data["description"],
                namespace=class_data["namespace"],
                parent_id=parent_id,
                uri=uri,
                status=OntologyStatus.ACTIVE
            )
            db.add(cls)
            db.flush()  # ID 생성을 위해
            created_classes[class_data["name"]] = cls
            print(f"  ✅ Created class: {cls.name}")
        else:
            created_classes[class_data["name"]] = cls
            print(f"  ⏭️  Class already exists: {cls.name}")
    
    db.commit()
    
    # 기본 속성 추가
    print("\n📝 Adding properties...")
    
    properties = [
        {
            "class_name": "SolarPanel",
            "name": "capacity",
            "display_name": "용량",
            "description": "패널의 최대 출력 용량",
            "data_type": "float",
            "unit": "kW",
            "is_required": True
        },
        {
            "class_name": "SolarPanel",
            "name": "efficiency",
            "display_name": "효율",
            "description": "에너지 변환 효율",
            "data_type": "float",
            "unit": "%",
            "is_required": False
        },
        {
            "class_name": "Battery",
            "name": "capacity",
            "display_name": "용량",
            "description": "배터리 저장 용량",
            "data_type": "float",
            "unit": "kWh",
            "is_required": True
        },
        {
            "class_name": "Battery",
            "name": "voltage",
            "display_name": "전압",
            "description": "배터리 전압",
            "data_type": "float",
            "unit": "V",
            "is_required": True
        },
        {
            "class_name": "SmartMeter",
            "name": "reading_interval",
            "display_name": "측정 주기",
            "description": "데이터 측정 주기",
            "data_type": "integer",
            "unit": "seconds",
            "is_required": False,
            "default_value": "60"
        }
    ]
    
    for prop_data in properties:
        cls = created_classes.get(prop_data["class_name"])
        if cls:
            prop = db.query(OntologyProperty).filter(
                OntologyProperty.class_id == cls.id,
                OntologyProperty.name == prop_data["name"]
            ).first()
            
            if not prop:
                prop = OntologyProperty(
                    name=prop_data["name"],
                    display_name=prop_data["display_name"],
                    description=prop_data["description"],
                    class_id=cls.id,
                    data_type=prop_data["data_type"],
                    unit=prop_data.get("unit"),
                    is_required=prop_data.get("is_required", False),
                    default_value=prop_data.get("default_value"),
                    status=OntologyStatus.ACTIVE
                )
                db.add(prop)
                print(f"  ✅ Added property: {cls.name}.{prop.name}")
            else:
                print(f"  ⏭️  Property already exists: {cls.name}.{prop.name}")
    
    db.commit()
    print("✅ Ontology created successfully\n")


def main():
    """메인 함수"""
    print("🚀 Initializing Collaborative Ontology Platform\n")
    
    db = SessionLocal()
    
    try:
        create_initial_users(db)
        create_initial_ontology(db)
        
        print("✨ Initialization complete!")
        print("\n📋 Default credentials:")
        print(f"  Admin: {settings.FIRST_SUPERUSER_EMAIL} / {settings.FIRST_SUPERUSER_PASSWORD}")
        print("  Editor: editor@gnginternational.com / editor123")
        print("  Expert: expert@gnginternational.com / expert123")
        print("  Provider: provider@kepco.com / provider123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
