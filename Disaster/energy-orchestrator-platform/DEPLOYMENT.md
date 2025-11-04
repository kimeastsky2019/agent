# 배포 가이드

## 프로덕션 배포 가이드

이 문서는 Energy Orchestrator Platform을 프로덕션 환경에 배포하는 방법을 설명합니다.

## 사전 요구사항

### 서버 요구사항

- **운영체제**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **메모리**: 최소 8GB RAM (권장: 16GB+)
- **디스크**: 최소 50GB 여유 공간
- **CPU**: 최소 4코어 (권장: 8코어+)

### 소프트웨어 요구사항

- Docker 20.10+
- Docker Compose 2.0+
- Git
- curl

### 설치 확인

```bash
# Docker 확인
docker --version
docker-compose --version

# Git 확인
git --version
```

## 1. 서버 설정

### 1.1 Docker 설치

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 1.2 방화벽 설정

```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8000/tcp  # Backend API (필요시)
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

## 2. 프로젝트 배포

### 2.1 프로젝트 클론

```bash
# 프로젝트 디렉토리 생성
sudo mkdir -p /opt/energy-orchestrator
sudo chown $USER:$USER /opt/energy-orchestrator

# 프로젝트 클론 또는 파일 업로드
cd /opt/energy-orchestrator
git clone <repository-url> .
# 또는
# scp로 파일 업로드
```

### 2.2 환경 변수 설정

`.env` 파일을 생성하고 프로덕션 설정을 입력합니다:

```bash
cd /opt/energy-orchestrator
cat > .env << 'EOF'
# Application
APP_NAME=Energy Orchestrator Platform
APP_VERSION=1.0.0
ENVIRONMENT=production
DEBUG=false

# Database
POSTGRES_USER=energy_admin
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=energy_db
DB_PORT=5432

# Redis
REDIS_PASSWORD=<strong-password>
REDIS_PORT=6379

# Security (반드시 변경하세요!)
SECRET_KEY=<generate-strong-secret-key-32-chars-min>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (프로덕션 도메인)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# External APIs
WEATHER_API_KEY=<your-weather-api-key>
OPENAI_API_KEY=<your-openai-api-key>
ANTHROPIC_API_KEY=<your-anthropic-api-key>

# Jena
JENA_ADMIN_PASSWORD=<strong-password>
JENA_PORT=3030

# Kafka
KAFKA_EXTERNAL_HOST=your-server-ip-or-domain
KAFKA_PORT=9092

# Ports
FRONTEND_PORT=80
BACKEND_PORT=8000
MQTT_PORT=1883
MQTT_WS_PORT=9001

# Frontend
VITE_API_URL=https://api.yourdomain.com
VITE_WS_URL=wss://api.yourdomain.com/ws
EOF

# 파일 권한 설정
chmod 600 .env
```

**중요**: 다음 값들을 반드시 변경하세요:
- `POSTGRES_PASSWORD`: 강력한 비밀번호
- `REDIS_PASSWORD`: 강력한 비밀번호
- `SECRET_KEY`: 최소 32자 이상의 랜덤 문자열
- `JENA_ADMIN_PASSWORD`: 강력한 비밀번호
- `CORS_ORIGINS`: 실제 도메인으로 변경
- `VITE_API_URL`: 실제 API URL로 변경

### 2.3 SECRET_KEY 생성

```bash
# Python으로 생성
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 또는 OpenSSL로 생성
openssl rand -hex 32
```

## 3. 배포 실행

### 3.1 자동 배포 스크립트 사용

```bash
cd /opt/energy-orchestrator
./deploy.sh
```

### 3.2 수동 배포

```bash
# 1. 가상 데이터 생성
cd backend
python3 scripts/generate_mock_data.py
cd ..

# 2. Docker 이미지 빌드
docker-compose -f docker-compose.prod.yml build

# 3. 서비스 시작
docker-compose -f docker-compose.prod.yml up -d

# 4. 로그 확인
docker-compose -f docker-compose.prod.yml logs -f
```

## 4. 배포 확인

### 4.1 서비스 상태 확인

```bash
# 모든 서비스 상태 확인
docker-compose -f docker-compose.prod.yml ps

# 특정 서비스 로그 확인
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend
```

### 4.2 Health Check

```bash
# Backend Health Check
curl http://localhost:8000/health

# Backend Readiness Check
curl http://localhost:8000/ready
```

### 4.3 브라우저에서 확인

- Frontend: http://your-server-ip
- Backend API: http://your-server-ip:8000
- API Docs: http://your-server-ip:8000/docs

## 5. Nginx 리버스 프록시 설정 (선택사항)

도메인을 사용하는 경우 Nginx를 리버스 프록시로 설정할 수 있습니다:

### 5.1 Nginx 설치

```bash
sudo apt-get update
sudo apt-get install nginx
```

### 5.2 Nginx 설정

```bash
sudo nano /etc/nginx/sites-available/energy-orchestrator
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 5.3 Nginx 활성화

```bash
sudo ln -s /etc/nginx/sites-available/energy-orchestrator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5.4 SSL 인증서 (Let's Encrypt)

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 6. 시스템 서비스 설정 (선택사항)

Docker Compose를 systemd 서비스로 등록:

```bash
sudo nano /etc/systemd/system/energy-orchestrator.service
```

```ini
[Unit]
Description=Energy Orchestrator Platform
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/energy-orchestrator
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

활성화:

```bash
sudo systemctl daemon-reload
sudo systemctl enable energy-orchestrator
sudo systemctl start energy-orchestrator
```

## 7. 모니터링 및 로그

### 7.1 로그 확인

```bash
# 모든 서비스 로그
docker-compose -f docker-compose.prod.yml logs -f

# 특정 서비스 로그
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend

# 최근 100줄
docker-compose -f docker-compose.prod.yml logs --tail=100
```

### 7.2 리소스 사용량 확인

```bash
# 컨테이너 리소스 사용량
docker stats

# 디스크 사용량
docker system df
```

## 8. 백업 및 복구

### 8.1 데이터베이스 백업

```bash
# PostgreSQL 백업
docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres energy_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 볼륨 백업
docker run --rm -v energy-orchestrator-platform_postgres_data_prod:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup_$(date +%Y%m%d_%H%M%S).tar.gz /data
```

### 8.2 데이터베이스 복구

```bash
# SQL 파일로 복구
docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres energy_db < backup.sql

# 볼륨 복구
docker run --rm -v energy-orchestrator-platform_postgres_data_prod:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /
```

## 9. 업데이트 및 유지보수

### 9.1 업데이트 방법

```bash
# 1. 코드 업데이트
cd /opt/energy-orchestrator
git pull

# 2. 이미지 재빌드
docker-compose -f docker-compose.prod.yml build --no-cache

# 3. 서비스 재시작
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# 4. 로그 확인
docker-compose -f docker-compose.prod.yml logs -f
```

### 9.2 정기 유지보수

```bash
# 사용하지 않는 이미지 삭제
docker image prune -a

# 사용하지 않는 볼륨 삭제
docker volume prune

# 전체 시스템 정리
docker system prune -a
```

## 10. 문제 해결

### 10.1 서비스가 시작되지 않는 경우

```bash
# 로그 확인
docker-compose -f docker-compose.prod.yml logs

# 서비스 상태 확인
docker-compose -f docker-compose.prod.yml ps

# 컨테이너 재시작
docker-compose -f docker-compose.prod.yml restart backend
```

### 10.2 데이터베이스 연결 오류

```bash
# 데이터베이스 상태 확인
docker-compose -f docker-compose.prod.yml exec db pg_isready -U postgres

# 데이터베이스 연결 테스트
docker-compose -f docker-compose.prod.yml exec db psql -U postgres -d energy_db -c "SELECT 1;"
```

### 10.3 포트 충돌

```bash
# 포트 사용 확인
sudo netstat -tulpn | grep :8000
sudo lsof -i :8000

# .env 파일에서 포트 변경
nano .env
```

## 11. 보안 권장사항

1. **강력한 비밀번호 사용**: 모든 비밀번호를 강력하게 설정
2. **환경 변수 보호**: `.env` 파일 권한을 600으로 설정
3. **방화벽 설정**: 필요한 포트만 열기
4. **SSL/TLS 사용**: HTTPS 사용 권장
5. **정기 업데이트**: Docker 이미지 및 시스템 정기 업데이트
6. **로그 모니터링**: 비정상적인 접근 시도 모니터링
7. **백업**: 정기적인 데이터 백업

## 12. 성능 최적화

### 12.1 백엔드 워커 수 조정

`backend/Dockerfile.prod`에서 워커 수 조정:

```dockerfile
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 12.2 데이터베이스 연결 풀 크기 조정

`.env` 파일에서:

```bash
DATABASE_POOL_SIZE=20
```

### 12.3 Redis 캐싱 활용

Redis를 캐싱 레이어로 활용하여 성능 향상

## 13. 지원 및 문의

배포 관련 문제가 있으면:
1. 로그 확인: `docker-compose -f docker-compose.prod.yml logs`
2. Health Check 확인: `curl http://localhost:8000/health`
3. 이슈 등록: GitHub Issues

---

**배포 완료 후 다음을 확인하세요:**
- ✅ 모든 서비스가 정상 실행 중
- ✅ Health Check 통과
- ✅ 프론트엔드 접속 가능
- ✅ API 문서 접속 가능
- ✅ 데이터베이스 연결 정상
- ✅ 로그에 에러 없음


