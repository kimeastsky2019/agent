# 협업 에너지 온톨로지 플랫폼 - 배포 가이드

## 개요

이 시스템은 GnG International을 위한 팔란티어 스타일의 협업 온톨로지 플랫폼입니다. 
에너지 분야의 다양한 전문가들이 함께 에너지 온톨로지를 구축하고 관리할 수 있습니다.

## 시스템 요구사항

### 최소 사양
- CPU: 4 Core
- RAM: 8 GB
- 디스크: 50 GB SSD
- OS: Ubuntu 20.04 LTS 이상 또는 macOS

### 권장 사양
- CPU: 8 Core
- RAM: 16 GB
- 디스크: 100 GB SSD
- OS: Ubuntu 22.04 LTS

### 필수 소프트웨어
- Docker 20.10 이상
- Docker Compose 2.0 이상
- Git

## 설치 가이드

### 1. Docker 및 Docker Compose 설치

#### Ubuntu/Debian
```bash
# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 재로그인 후 확인
docker --version
docker-compose --version
```

#### macOS
```bash
# Homebrew를 통한 설치
brew install docker
brew install docker-compose
```

### 2. 프로젝트 클론 및 설정

```bash
# 저장소 클론
git clone <repository-url>
cd collaborative_ontology

# 환경 변수 파일 생성
cat > .env << EOF
# Database
POSTGRES_DB=collaborative_ontology
POSTGRES_USER=ontology_user
POSTGRES_PASSWORD=change_this_password

# Redis
REDIS_URL=redis://redis:6379/0

# InfluxDB
INFLUXDB_TOKEN=your-influxdb-token-here
INFLUXDB_ORG=gng_energy
INFLUXDB_BUCKET=energy_data

# Backend
SECRET_KEY=your-super-secret-key-change-in-production-$(openssl rand -hex 32)
CORS_ORIGINS=http://localhost:3000,http://localhost:80

# Fuseki
FUSEKI_ADMIN_PASSWORD=change_this_password
EOF

# 권한 설정
chmod 600 .env
```

### 3. 시스템 실행

```bash
# Docker 이미지 빌드 및 컨테이너 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그 확인
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 4. 초기 데이터 설정

```bash
# 데이터베이스 마이그레이션
docker-compose exec backend alembic upgrade head

# 초기 온톨로지 로드
docker-compose exec backend python scripts/load_ontology.py

# 테스트 사용자 생성
docker-compose exec backend python scripts/create_test_users.py
```

## 서비스 접속 정보

### 주요 서비스
| 서비스 | URL | 설명 |
|--------|-----|------|
| 프론트엔드 | http://localhost:3000 | React 웹 애플리케이션 |
| 백엔드 API | http://localhost:8000 | FastAPI REST API |
| API 문서 | http://localhost:8000/docs | Swagger UI |
| Fuseki | http://localhost:3030 | SPARQL Endpoint |
| Grafana | http://localhost:3001 | 모니터링 대시보드 |
| Prometheus | http://localhost:9090 | 메트릭 수집 |

### 기본 로그인 정보

#### 시스템 관리자
```
Username: admin
Password: admin123
Role: System Admin
```

#### 에너지 전문가
```
Username: expert1
Password: expert123
Role: Energy Expert
```

#### 에너지 공급자
```
Username: provider1
Password: provider123
Role: Energy Provider
```

## 운영 및 관리

### 서비스 관리 명령어

```bash
# 모든 서비스 시작
docker-compose start

# 모든 서비스 중지
docker-compose stop

# 특정 서비스 재시작
docker-compose restart backend

# 서비스 상태 확인
docker-compose ps

# 리소스 사용량 확인
docker stats
```

### 로그 관리

```bash
# 실시간 로그 보기
docker-compose logs -f

# 최근 100줄의 로그만 보기
docker-compose logs --tail=100

# 특정 시간 이후의 로그 보기
docker-compose logs --since=1h backend
```

### 백업 및 복원

#### 데이터베이스 백업
```bash
# PostgreSQL 백업
docker-compose exec postgres pg_dump -U ontology_user collaborative_ontology > backup_$(date +%Y%m%d).sql

# InfluxDB 백업
docker-compose exec influxdb influx backup /tmp/backup
docker cp collaborative_ontology_influxdb:/tmp/backup ./influxdb_backup_$(date +%Y%m%d)
```

#### 온톨로지 백업
```bash
# Fuseki 데이터 백업
docker cp collaborative_ontology_fuseki:/fuseki ./fuseki_backup_$(date +%Y%m%d)
```

#### 복원
```bash
# PostgreSQL 복원
cat backup_20250101.sql | docker-compose exec -T postgres psql -U ontology_user collaborative_ontology

# InfluxDB 복원
docker cp influxdb_backup_20250101 collaborative_ontology_influxdb:/tmp/backup
docker-compose exec influxdb influx restore /tmp/backup
```

## 성능 튜닝

### PostgreSQL 최적화

```bash
# docker-compose.yml에서 PostgreSQL 설정 조정
environment:
  POSTGRES_SHARED_BUFFERS: 2GB
  POSTGRES_EFFECTIVE_CACHE_SIZE: 6GB
  POSTGRES_WORK_MEM: 64MB
  POSTGRES_MAINTENANCE_WORK_MEM: 512MB
  POSTGRES_MAX_CONNECTIONS: 200
```

### Fuseki 메모리 설정

```bash
# docker-compose.yml에서 JVM 옵션 조정
environment:
  JVM_ARGS: "-Xmx4g -Xms2g"
```

### Redis 메모리 제한

```bash
# docker-compose.yml에 추가
redis:
  command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
```

## 모니터링

### Grafana 대시보드 설정

1. Grafana 접속: http://localhost:3001
2. 로그인: admin / grafana_admin
3. Data Sources에서 InfluxDB 연결
4. 제공된 대시보드 JSON 파일 Import

### 주요 메트릭
- API 응답 시간
- 동시 사용자 수
- WebSocket 연결 수
- 데이터베이스 쿼리 성능
- 온톨로지 변경 빈도

## 보안 강화

### 1. SSL/TLS 인증서 설정

```bash
# Let's Encrypt 인증서 발급 (프로덕션)
sudo apt-get install certbot
sudo certbot certonly --standalone -d your-domain.com

# 인증서 파일 복사
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem docker/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem docker/ssl/
```

### 2. 방화벽 설정

```bash
# UFW 설치 및 설정
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 3. 비밀번호 변경

```bash
# 환경 변수 파일(.env) 편집
nano .env

# 다음 항목들을 강력한 비밀번호로 변경:
# - POSTGRES_PASSWORD
# - SECRET_KEY
# - FUSEKI_ADMIN_PASSWORD
# - INFLUXDB_TOKEN

# 변경 후 서비스 재시작
docker-compose restart
```

## 문제 해결

### 일반적인 문제

#### 1. 컨테이너가 시작되지 않음

```bash
# 로그 확인
docker-compose logs backend

# 오류 원인 파악 후 재시작
docker-compose restart backend
```

#### 2. 데이터베이스 연결 실패

```bash
# PostgreSQL 상태 확인
docker-compose exec postgres pg_isready -U ontology_user

# 네트워크 확인
docker network inspect collaborative_ontology_ontology_network
```

#### 3. 디스크 공간 부족

```bash
# 사용하지 않는 이미지 정리
docker system prune -a

# 볼륨 정리 (주의: 데이터 손실 가능)
docker volume prune
```

#### 4. 메모리 부족

```bash
# 컨테이너 메모리 사용량 확인
docker stats

# 불필요한 서비스 중지
docker-compose stop grafana prometheus
```

### 성능 문제

#### API 응답 속도가 느림

1. Redis 캐시 확인
```bash
docker-compose exec redis redis-cli info stats
```

2. 데이터베이스 인덱스 확인
```bash
docker-compose exec postgres psql -U ontology_user -d collaborative_ontology -c "\di"
```

3. Nginx 로그 확인
```bash
docker-compose logs nginx | grep slow
```

## 프로덕션 배포

### GCP (Google Cloud Platform) 배포

#### 1. GKE 클러스터 생성

```bash
# gcloud CLI 설치 및 인증
gcloud auth login
gcloud config set project your-project-id

# GKE 클러스터 생성
gcloud container clusters create ontology-cluster \
  --zone=asia-northeast3-a \
  --num-nodes=3 \
  --machine-type=e2-standard-4 \
  --enable-autoscaling \
  --min-nodes=2 \
  --max-nodes=10
```

#### 2. Kubernetes 배포

```bash
# kubectl 설정
gcloud container clusters get-credentials ontology-cluster --zone=asia-northeast3-a

# 네임스페이스 생성
kubectl create namespace collaborative-ontology

# 시크릿 생성
kubectl create secret generic ontology-secrets \
  --from-literal=db-password=<strong-password> \
  --from-literal=secret-key=<secret-key> \
  --namespace=collaborative-ontology

# ConfigMap 생성
kubectl create configmap ontology-config \
  --from-file=ontology/energy_core.ttl \
  --namespace=collaborative-ontology

# 배포
kubectl apply -f k8s/ --namespace=collaborative-ontology

# 상태 확인
kubectl get pods --namespace=collaborative-ontology
kubectl get services --namespace=collaborative-ontology
```

#### 3. 로드 밸런서 설정

```bash
# Ingress 설정
kubectl apply -f k8s/ingress.yaml --namespace=collaborative-ontology

# 외부 IP 확인
kubectl get ingress --namespace=collaborative-ontology
```

### 도메인 설정

```bash
# DNS 레코드 추가
# A 레코드: ontology.gng-energy.com -> [외부 IP]
# CNAME 레코드: www.ontology.gng-energy.com -> ontology.gng-energy.com
```

## 업데이트 및 유지보수

### 애플리케이션 업데이트

```bash
# 최신 코드 가져오기
git pull origin main

# 이미지 재빌드
docker-compose build

# 서비스 재시작 (무중단)
docker-compose up -d --no-deps --build backend
docker-compose up -d --no-deps --build frontend
```

### 데이터베이스 마이그레이션

```bash
# 마이그레이션 파일 생성
docker-compose exec backend alembic revision --autogenerate -m "description"

# 마이그레이션 실행
docker-compose exec backend alembic upgrade head

# 롤백 (필요시)
docker-compose exec backend alembic downgrade -1
```

## 지원 및 문의

### 기술 지원
- 이메일: support@gng-energy.com
- Slack: #ontology-platform
- GitHub Issues: [프로젝트 저장소]

### 문서
- API 문서: http://your-domain/docs
- 개발자 가이드: [링크]
- 사용자 매뉴얼: [링크]

## 체크리스트

### 배포 전 확인사항
- [ ] 모든 비밀번호가 강력한 값으로 변경되었는지 확인
- [ ] SSL/TLS 인증서가 설정되었는지 확인
- [ ] 백업 스크립트가 설정되었는지 확인
- [ ] 모니터링 대시보드가 작동하는지 확인
- [ ] 방화벽 규칙이 올바르게 설정되었는지 확인
- [ ] 로그 로테이션이 설정되었는지 확인
- [ ] 알림 시스템이 작동하는지 확인

### 운영 체크리스트
- [ ] 일일 백업 확인
- [ ] 시스템 리소스 사용량 모니터링
- [ ] 로그 파일 검토
- [ ] 보안 업데이트 적용
- [ ] 사용자 피드백 수집
- [ ] 성능 메트릭 분석
