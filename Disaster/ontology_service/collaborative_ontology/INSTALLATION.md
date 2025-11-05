# 🚀 설치 및 실행 가이드

## 📋 사전 요구사항

- Docker & Docker Compose
- Python 3.11+ (로컬 실행 시)
- Node.js 18+ (로컬 실행 시)
- PostgreSQL 16+ (로컬 실행 시)

## 🐳 Docker로 실행 (권장)

### 1. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# 필요시 .env 파일 수정 (SECRET_KEY 등)
nano .env
```

### 2. Docker Compose로 전체 시스템 실행

```bash
# 모든 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 특정 서비스만 재시작
docker-compose restart backend
docker-compose restart frontend
```

### 3. 초기 데이터 생성

```bash
# 백엔드 컨테이너에 접속
docker-compose exec backend bash

# 초기 데이터 스크립트 실행
python init_data.py

# 컨테이너 종료
exit
```

### 4. 접속

- **프론트엔드**: http://localhost:3000
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/api/v1/docs
- **pgAdmin**: http://localhost:5050 (admin@gnginternational.com / admin123)

### 5. 서비스 중지

```bash
# 모든 서비스 중지
docker-compose down

# 볼륨까지 삭제 (데이터 초기화)
docker-compose down -v
```

## 💻 로컬 개발 환경 실행

### 백엔드 설정

```bash
cd backend

# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp ../.env.example .env

# PostgreSQL 데이터베이스 생성
createdb collaborative_ontology

# 초기 데이터 생성
python init_data.py

# 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 프론트엔드 설정

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm start
```

## 🔐 기본 로그인 정보

초기 데이터 스크립트 실행 후 다음 계정으로 로그인할 수 있습니다:

| 역할 | 이메일 | 비밀번호 | 권한 |
|------|--------|----------|------|
| 관리자 | admin@gnginternational.com | changeme123 | 전체 권한 |
| 편집자 | editor@gnginternational.com | editor123 | 온톨로지 편집 |
| 전문가 | expert@gnginternational.com | expert123 | 리뷰 및 승인 |
| 공급자 | provider@kepco.com | provider123 | 데이터 기여 |

**⚠️ 중요**: 운영 환경에서는 반드시 비밀번호를 변경하세요!

## 🧪 테스트

### 백엔드 테스트

```bash
cd backend
pytest
```

### API 테스트

```bash
# 헬스체크
curl http://localhost:8000/health

# 로그인
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@gnginternational.com&password=changeme123"
```

## 📊 데이터베이스 관리

### Alembic 마이그레이션

```bash
cd backend

# 마이그레이션 생성
alembic revision --autogenerate -m "설명"

# 마이그레이션 적용
alembic upgrade head

# 롤백
alembic downgrade -1
```

### pgAdmin 접속

1. http://localhost:5050 접속
2. admin@gnginternational.com / admin123 로그인
3. 서버 추가:
   - Host: postgres
   - Port: 5432
   - Database: collaborative_ontology
   - Username: ontology_user
   - Password: ontology_pass

## 🔧 문제 해결

### 포트 충돌

```bash
# 포트 사용 확인
# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Linux/Mac
lsof -i :8000
lsof -i :3000
```

### Docker 캐시 정리

```bash
# Docker 이미지 재빌드
docker-compose build --no-cache

# 미사용 리소스 정리
docker system prune -a
```

### 데이터베이스 초기화

```bash
# Docker 볼륨 삭제
docker-compose down -v

# 다시 시작
docker-compose up -d

# 초기 데이터 재생성
docker-compose exec backend python init_data.py
```

## 📝 개발 팁

### 백엔드 핫 리로드

Docker Compose는 기본적으로 볼륨 마운트로 핫 리로드가 활성화되어 있습니다.
코드 변경 시 자동으로 서버가 재시작됩니다.

### 프론트엔드 개발

React 개발 서버도 핫 리로드가 활성화되어 있어 코드 변경 시 자동으로 브라우저가 새로고침됩니다.

### API 문서 활용

http://localhost:8000/api/v1/docs 에서 Swagger UI를 통해 API를 테스트할 수 있습니다.

## 🌐 배포

### 운영 환경 설정

1. .env 파일에서 DEBUG=false 설정
2. SECRET_KEY를 강력한 랜덤 값으로 변경
3. 데이터베이스 비밀번호 변경
4. CORS 설정에 실제 도메인 추가

### Docker Compose 운영 모드

```bash
# 운영 모드로 빌드
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 📧 문의

문제가 발생하거나 질문이 있으시면:

- Email: support@gnginternational.com
- GitHub Issues: [프로젝트 저장소]/issues
