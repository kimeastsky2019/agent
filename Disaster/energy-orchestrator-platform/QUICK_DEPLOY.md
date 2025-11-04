# 빠른 배포 가이드

## 🚀 빠른 배포 (5분 안에)

### 1. 서버에 접속

```bash
ssh user@your-server-ip
```

### 2. 프로젝트 다운로드/업로드

```bash
# 방법 1: Git 클론
git clone <repository-url> /opt/energy-orchestrator
cd /opt/energy-orchestrator

# 방법 2: 파일 업로드 (로컬에서)
scp -r energy-orchestrator-platform user@your-server-ip:/opt/
ssh user@your-server-ip
cd /opt/energy-orchestrator-platform
```

### 3. 환경 변수 설정

```bash
# env.example 복사
cp env.example .env

# .env 파일 편집 (최소한 다음 항목 변경)
nano .env
```

**필수 변경 사항:**
- `POSTGRES_PASSWORD`: 강력한 비밀번호
- `REDIS_PASSWORD`: 강력한 비밀번호  
- `SECRET_KEY`: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`로 생성
- `JENA_ADMIN_PASSWORD`: 강력한 비밀번호
- `CORS_ORIGINS`: 실제 도메인 (없으면 `http://localhost:3000` 유지)
- `VITE_API_URL`: 실제 API URL (없으면 `http://localhost:8000` 유지)

### 4. 배포 실행

```bash
# 배포 스크립트 실행
./deploy.sh
```

또는 수동 배포:

```bash
# 가상 데이터 생성
cd backend && python3 scripts/generate_mock_data.py && cd ..

# Docker 이미지 빌드 및 시작
docker-compose -f docker-compose.prod.yml up -d --build
```

### 5. 확인

```bash
# 서비스 상태 확인
docker-compose -f docker-compose.prod.yml ps

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f

# Health Check
curl http://localhost:8000/health
```

### 6. 접속

브라우저에서:
- Frontend: http://your-server-ip:3000
- Backend API: http://your-server-ip:8000
- API Docs: http://your-server-ip:8000/docs

## 📝 주요 명령어

### 서비스 관리

```bash
# 서비스 시작
docker-compose -f docker-compose.prod.yml up -d

# 서비스 중지
docker-compose -f docker-compose.prod.yml down

# 서비스 재시작
docker-compose -f docker-compose.prod.yml restart

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f

# 특정 서비스 로그
docker-compose -f docker-compose.prod.yml logs -f backend
```

### 문제 해결

```bash
# 모든 컨테이너 상태 확인
docker-compose -f docker-compose.prod.yml ps

# 컨테이너 재빌드
docker-compose -f docker-compose.prod.yml build --no-cache

# 볼륨 초기화 (주의: 데이터 삭제됨)
docker-compose -f docker-compose.prod.yml down -v
```

## 🔒 보안 체크리스트

배포 전 확인:
- [ ] `.env` 파일의 모든 비밀번호 변경
- [ ] `SECRET_KEY` 생성 및 설정
- [ ] `CORS_ORIGINS`에 실제 도메인 설정
- [ ] 방화벽 설정 (필요한 포트만 열기)
- [ ] `.env` 파일 권한 설정: `chmod 600 .env`

## 📚 자세한 배포 가이드

더 자세한 내용은 [DEPLOYMENT.md](./DEPLOYMENT.md)를 참조하세요.


