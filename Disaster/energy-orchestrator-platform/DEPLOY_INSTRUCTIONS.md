# 서버 배포 가이드

## 서버 정보
- **IP**: 34.47.89.217
- **User**: metal
- **Key File**: energy-orchestrator-platform.pem

## 배포 방법

### 1. 키 파일 확인

키 파일이 있는 위치를 확인하세요:

```bash
# 키 파일 찾기
find ~ -name "*energy-orchestrator*.pem" 2>/dev/null

# 또는 Downloads 폴더 확인
ls ~/Downloads/*.pem
```

### 2. 키 파일 권한 설정

```bash
chmod 600 energy-orchestrator-platform.pem
```

### 3. 서버 접속 테스트

```bash
ssh -i energy-orchestrator-platform.pem metal@34.47.89.217
```

### 4. 자동 배포 실행

```bash
cd /Users/donghokim/Documents/myworkspace/AI_Agent/Disaster/energy-orchestrator-platform

# 키 파일 경로 지정
./deploy-to-server.sh [KEY_FILE_PATH]

# 예시:
./deploy-to-server.sh ./energy-orchestrator-platform.pem
./deploy-to-server.sh ~/Downloads/energy-orchestrator-platform.pem
```

### 5. 수동 배포

#### 5.1 프로젝트 업로드

```bash
# rsync로 업로드
rsync -avz --progress \
    --exclude '.git' \
    --exclude 'node_modules' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.env' \
    --exclude '.DS_Store' \
    -e "ssh -i energy-orchestrator-platform.pem" \
    ./ metal@34.47.89.217:/opt/energy-orchestrator/
```

#### 5.2 서버에서 배포 실행

```bash
# 서버 접속
ssh -i energy-orchestrator-platform.pem metal@34.47.89.217

# 프로젝트 디렉토리 이동
cd /opt/energy-orchestrator

# 환경 변수 설정
cp env.example .env
nano .env  # 필수 설정 변경

# 배포 실행
./deploy.sh
```

## 배포 후 확인

### 서비스 상태 확인

```bash
ssh -i energy-orchestrator-platform.pem metal@34.47.89.217 \
  "cd /opt/energy-orchestrator && docker-compose -f docker-compose.prod.yml ps"
```

### Health Check

```bash
curl http://34.47.89.217:8000/health
```

### 접속 정보

배포 완료 후:
- **Frontend**: http://34.47.89.217:3000
- **Backend API**: http://34.47.89.217:8000
- **API Docs**: http://34.47.89.217:8000/docs

## 문제 해결

### 키 파일 권한 오류

```bash
chmod 600 energy-orchestrator-platform.pem
```

### 서버 접속 실패

```bash
# 연결 테스트
ssh -v -i energy-orchestrator-platform.pem metal@34.47.89.217

# 키 파일 형식 확인
file energy-orchestrator-platform.pem
```

### PPK 파일인 경우

PPK 파일(PuTTY 형식)을 PEM으로 변환:

```bash
# puttygen 설치 (macOS)
brew install putty

# 변환
puttygen energy-orchestrator-platform.ppk -O private-openssh -o energy-orchestrator-platform.pem
```

### Docker 설치 확인

```bash
ssh -i energy-orchestrator-platform.pem metal@34.47.89.217 \
  "docker --version && docker-compose --version"
```

## 로그 확인

```bash
# 모든 서비스 로그
ssh -i energy-orchestrator-platform.pem metal@34.47.89.217 \
  "cd /opt/energy-orchestrator && docker-compose -f docker-compose.prod.yml logs -f"

# 특정 서비스 로그
ssh -i energy-orchestrator-platform.pem metal@34.47.89.217 \
  "cd /opt/energy-orchestrator && docker-compose -f docker-compose.prod.yml logs -f backend"
```

## 서비스 재시작

```bash
ssh -i energy-orchestrator-platform.pem metal@34.47.89.217 \
  "cd /opt/energy-orchestrator && docker-compose -f docker-compose.prod.yml restart"
```

## 서비스 중지

```bash
ssh -i energy-orchestrator-platform.pem metal@34.47.89.217 \
  "cd /opt/energy-orchestrator && docker-compose -f docker-compose.prod.yml down"
```


