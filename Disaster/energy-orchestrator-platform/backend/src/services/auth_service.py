from sqlalchemy.orm import Session
from src.schemas.user import UserCreate, UserResponse, Token
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    async def register(self, user: UserCreate) -> UserResponse:
        """회원가입"""
        # 실제 구현에서는 DB에 저장
        hashed_password = pwd_context.hash(user.password)
        return UserResponse(
            id="1",
            email=user.email,
            full_name=user.full_name,
            role="user",
            is_active=True,
            created_at=datetime.now()
        )
    
    async def login(self, email: str, password: str) -> Token:
        """로그인"""
        # 고정 사용자 정보 확인
        if email == "info@gngmeta.com" and password == "admin1234":
            access_token = self._create_access_token(data={"sub": email})
            return Token(access_token=access_token, token_type="bearer")
        else:
            raise ValueError("Invalid email or password")
    
    def _create_access_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

