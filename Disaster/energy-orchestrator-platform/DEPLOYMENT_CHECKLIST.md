# 🚀 배포 준비 체크리스트

## 배포 전 필수 확인 사항

### 1. 환경 변수 설정

#### 필수 환경 변수
- [ ] `SECRET_KEY` - 최소 32자 이상의 강력한 비밀키 (생성: `openssl rand -hex 32`)
- [ ] `POSTGRES_PASSWORD` - 강력한 데이터베이스 비밀번호
- [ ] `REDIS_PASSWORD` - 강력한 Redis 비밀번호
- [ ] `JENA_ADMIN_PASSWORD` - 강력한 Jena 관리자 비밀번호
- [ ] `CORS_ORIGINS` - 실제 프로덕션 도메인 (예: `https://yourdomain.com`)
- [ ] `VITE_API_URL` - 실제 API URL (예: `https://api.yourdomain.com`)
- [ ] `VITE_WS_URL` - WebSocket URL (예: `wss://api.yourdomain.com/ws`)

#### 선택적 환경 변수
- [ ] `WEATHER_API_KEY` - 날씨 API 키 (필요시)
- [ ] `OPENAI_API_KEY` - OpenAI API 키 (필요시)
- [ ] `ANTHROPIC_API_KEY` - Anthropic API 키 (필요시)

### 2. 서버 설정 확인

#### 하드웨어 요구사항
- [ ] **메모리**: 최소 8GB RAM (권장: 16GB+)
- [ ] **디스크**: 최소 50GB 여유 공간
- [ ] **CPU**: 최소 4코어 (권장: 8코어+)

#### 소프트웨어 설치
- [ ] Docker 20.10+ 설치 확인
- [ ] Docker Compose 2.0+ 설치 확인
- [ ] Git 설치 확인

#### 방화벽 설정
- [ ] 포트 22 (SSH) 허용
- [ ] 포트 80 (HTTP) 허용
- [ ] 포트 443 (HTTPS) 허용
- [ ] 포트 8000 (Backend) - 필요시 허용
- [ ] 포트 5000 (Ontology Service) - 필요시 허용
- [ ] 포트 5001 (Image Broadcasting) - 필요시 허용

### 3. 보안 설정

#### 파일 권한
- [ ] `.env` 파일 권한: `chmod 600 .env`
- [ ] `.env` 파일이 Git에 커밋되지 않도록 확인

#### 비밀번호 정책
- [ ] 모든 기본 비밀번호 변경
- [ ] 강력한 비밀번호 사용 (최소 16자, 대소문자, 숫자, 특수문자 포함)

#### 네트워크 보안
- [ ] CORS 설정이 실제 도메인으로만 제한되는지 확인
- [ ] 프로덕션 환경에서 DEBUG=false 확인
- [ ] 프로덕션 환경에서 API 문서 비활성화 확인

### 4. Docker 설정 확인

#### 컨테이너 상태
```bash
# 모든 서비스 상태 확인
docker-compose -f docker-compose.prod.yml ps

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f
```

#### Health Check
- [ ] Backend: `curl http://localhost:8000/health`
- [ ] Ontology Service: `curl http://localhost:5000/api/health`
- [ ] Image Broadcasting: `curl http://localhost:5001/`

### 5. 데이터베이스 설정

#### 초기화
- [ ] 데이터베이스 초기화 스크립트 실행 확인
- [ ] 마이그레이션 적용 확인 (필요시)

#### 백업
- [ ] 백업 스크립트 준비
- [ ] 백업 스토리지 확인

### 6. 모니터링 및 로깅

#### 로깅
- [ ] 로그 디렉토리 확인
- [ ] 로그 로테이션 설정 확인

#### 모니터링 (선택사항)
- [ ] Prometheus 설정 (필요시)
- [ ] Grafana 설정 (필요시)
- [ ] 알림 시스템 설정 (필요시)

---

## 배포 단계별 가이드

### Step 1: 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env  # 또는 직접 생성

# .env 파일 편집
nano .env

# 파일 권한 설정
chmod 600 .env
```

### Step 2: 배포 스크립트 실행

```bash
# 배포 스크립트 실행
./deploy.sh

# 또는 수동 배포
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### Step 3: Health Check 확인

```bash
# Backend 확인
curl http://localhost:8000/health

# Ontology Service 확인
curl http://localhost:5000/api/health

# Image Broadcasting 확인
curl http://localhost:5001/

# Readiness 확인
curl http://localhost:8000/ready
```

### Step 4: 서비스 접속 확인

```bash
# Frontend 접속
curl http://localhost:80

# Backend API 접속
curl http://localhost:8000/health

# API 문서 확인 (개발 환경에서만)
curl http://localhost:8000/docs
```

---

## 배포 후 확인 사항

### 1. 서비스 상태

```bash
# 모든 서비스 상태 확인
docker-compose -f docker-compose.prod.yml ps

# 특정 서비스 로그 확인
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f ontology-service
docker-compose -f docker-compose.prod.yml logs -f image-broadcasting
```

### 2. 데이터베이스 연결

```bash
# 데이터베이스 연결 테스트
docker-compose -f docker-compose.prod.yml exec db psql -U postgres -d energy_db -c "SELECT 1;"
```

### 3. 네트워크 연결

```bash
# 서비스 간 통신 확인
docker-compose -f docker-compose.prod.yml exec backend curl http://ontology-service:5000/api/health
docker-compose -f docker-compose.prod.yml exec backend curl http://image-broadcasting:5001/
```

---

## 문제 해결

### 서비스가 시작되지 않는 경우

1. **로그 확인**
```bash
docker-compose -f docker-compose.prod.yml logs backend
```

2. **환경 변수 확인**
```bash
docker-compose -f docker-compose.prod.yml config
```

3. **컨테이너 재시작**
```bash
docker-compose -f docker-compose.prod.yml restart backend
```

### 데이터베이스 연결 오류

1. **데이터베이스 상태 확인**
```bash
docker-compose -f docker-compose.prod.yml exec db pg_isready -U postgres
```

2. **연결 문자열 확인**
```bash
echo $DATABASE_URL
```

### 포트 충돌

1. **포트 사용 확인**
```bash
sudo netstat -tulpn | grep :8000
```

2. **포트 변경**
```bash
# .env 파일에서 포트 변경
BACKEND_PORT=8001
```

---

## 유지보수

### 정기 작업

#### 일일
- [ ] 서비스 상태 확인
- [ ] 로그 확인

#### 주간
- [ ] 데이터베이스 백업 확인
- [ ] 디스크 사용량 확인
- [ ] 로그 정리

#### 월간
- [ ] 보안 업데이트 확인
- [ ] Docker 이미지 업데이트
- [ ] 시스템 리소스 확인

### 백업

```bash
# 데이터베이스 백업
docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres energy_db > backup_$(date +%Y%m%d).sql

# 볼륨 백업
docker run --rm -v energy-orchestrator-platform_postgres_data_prod:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup_$(date +%Y%m%d).tar.gz /data
```

### 업데이트

```bash
# 코드 업데이트
git pull

# 이미지 재빌드
docker-compose -f docker-compose.prod.yml build --no-cache

# 서비스 재시작
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

---

## 지원 및 문의

문제가 발생하면:
1. 로그 확인: `docker-compose -f docker-compose.prod.yml logs`
2. Health Check 확인: `curl http://localhost:8000/health`
3. [CODE_REVIEW.md](./CODE_REVIEW.md) 참고
4. [DEPLOYMENT.md](./DEPLOYMENT.md) 참고

---

**마지막 업데이트**: 2025-01-XX





