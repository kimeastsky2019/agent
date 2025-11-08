from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.schemas.user import UserCreate, UserResponse, Token
from src.models.user import User, UserRole
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.config import settings
import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    async def register(self, user: UserCreate) -> UserResponse:
        """회원가입"""
        # 이메일 중복 확인
        existing_user = self.db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise ValueError("Email already registered")
        
        # 비밀번호 해싱
        hashed_password = pwd_context.hash(user.password)
        
        # 새 사용자 생성
        db_user = User(
            email=user.email,
            hashed_password=hashed_password,
            full_name=user.full_name,
            role=UserRole.USER,
            is_active=True
        )
        
        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            logger.info(f"User registered: {user.email}")
            
            return UserResponse(
                id=str(db_user.id),
                email=db_user.email,
                full_name=db_user.full_name,
                role=db_user.role.value,
                is_active=db_user.is_active,
                created_at=db_user.created_at
            )
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Registration failed: {e}")
            raise ValueError("Registration failed. Email may already be registered.")
    
    async def login(self, email: str, password: str) -> Token:
        """로그인 - 데이터베이스 기반 인증"""
        # 사용자 조회
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            logger.warning(f"Login attempt with non-existent email: {email}")
            raise ValueError("Invalid email or password")
        
        # 비활성 사용자 확인
        if not user.is_active:
            logger.warning(f"Login attempt with inactive account: {email}")
            raise ValueError("Account is inactive")
        
        # 비밀번호 검증
        if not pwd_context.verify(password, user.hashed_password):
            logger.warning(f"Invalid password attempt for: {email}")
            raise ValueError("Invalid email or password")
        
        # JWT 토큰 생성
        access_token = self._create_access_token(data={"sub": email, "role": user.role.value})
        logger.info(f"User logged in: {email}")
        
        return Token(access_token=access_token, token_type="bearer")
    
    def _create_access_token(self, data: dict, expires_delta: timedelta = None):
        """JWT 액세스 토큰 생성"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> dict:
        """JWT 토큰 검증"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            raise ValueError("Invalid token")
    
    def get_user_by_email(self, email: str) -> User:
        """이메일로 사용자 조회"""
        return self.db.query(User).filter(User.email == email).first()

