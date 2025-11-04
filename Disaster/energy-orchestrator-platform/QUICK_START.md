# 빠른 시작 가이드

## 문제 해결: localhost:3000 연결 불가

### 문제 원인
프론트엔드 서버가 실행되지 않았거나 Node.js가 설치되지 않았습니다.

## 해결 방법

### 방법 1: Node.js 설치 후 직접 실행 (권장)

#### 1단계: Node.js 설치

**macOS (Homebrew 사용):**
```bash
brew install node
```

**또는 공식 웹사이트에서 설치:**
- https://nodejs.org/ 에서 LTS 버전 다운로드 및 설치

**설치 확인:**
```bash
node --version  # v20.x.x 이상이어야 함
npm --version   # 10.x.x 이상이어야 함
```

#### 2단계: 프론트엔드 의존성 설치 및 실행

```bash
cd /Users/donghokim/Documents/myworkspace/AI_Agent/Disaster/energy-orchestrator-platform/frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

서버가 실행되면:
- 브라우저에서 http://localhost:3000 접속
- 또는 터미널에 표시된 URL 확인

### 방법 2: Docker 사용 (Node.js 설치 불필요)

#### 1단계: Docker 설치 확인

```bash
docker --version
docker-compose --version
```

Docker가 설치되어 있지 않다면:
- macOS: https://www.docker.com/products/docker-desktop/ 에서 다운로드

#### 2단계: Docker Compose로 전체 서비스 실행

```bash
cd /Users/donghokim/Documents/myworkspace/AI_Agent/Disaster/energy-orchestrator-platform

# Docker 네트워크 생성
docker network create energy-net 2>/dev/null || true

# 전체 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f frontend
```

### 방법 3: 백엔드만 실행 (프론트엔드 없이 API 테스트)

```bash
cd /Users/donghokim/Documents/myworkspace/AI_Agent/Disaster/energy-orchestrator-platform/backend

# Python 가상환경 생성
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

API 문서 접속:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## 포트 확인

다른 프로그램이 포트를 사용 중일 수 있습니다:

```bash
# 포트 3000 확인
lsof -i :3000

# 포트 8000 확인
lsof -i :8000
```

포트가 사용 중이면:
- 해당 프로세스 종료
- 또는 다른 포트 사용 (package.json의 port 설정 변경)

## 문제 해결 체크리스트

- [ ] Node.js 설치 확인 (`node --version`)
- [ ] npm 설치 확인 (`npm --version`)
- [ ] 프론트엔드 디렉토리에서 `npm install` 실행
- [ ] `npm run dev` 실행 후 터미널에 URL 확인
- [ ] 포트 3000이 사용 가능한지 확인
- [ ] 방화벽 설정 확인 (macOS 방화벽)
- [ ] 브라우저 캐시 삭제 후 재시도

## 추가 정보

### 프론트엔드 개발 서버 설정

`frontend/vite.config.ts`에서 포트 변경 가능:
```typescript
server: {
  host: '0.0.0.0',
  port: 3000,  // 여기서 포트 변경
}
```

### 백엔드 API URL 설정

`frontend/src/services/api.ts`에서 API URL 확인:
```typescript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
```

환경 변수 설정:
```bash
# frontend/.env 파일 생성
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

## 다음 단계

1. 프론트엔드 서버 실행 확인
2. http://localhost:3000 접속
3. 대시보드에서 카드와 지도 확인
4. 날씨 정보 표시 확인

문제가 계속되면 터미널 에러 메시지를 확인하세요!




