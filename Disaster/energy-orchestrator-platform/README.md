# AI-Orchestrated Disaster-Resilient Energy Sharing Network

재난 대응형 AI 에너지 공유 네트워크 플랫폼

## 개요

이 솔루션은 자연재해(지진, 태풍, 산불 등) 발생 시 AI 기반 실시간 에너지 재분배 및 대응 의사결정을 수행하는 통합 시스템입니다.

## 주요 기능

- 🗺️ **지도 기반 시각화**: Mapbox를 사용한 에너지 자산 위치 표시
- 📊 **카드 중심 UI**: Material-UI 기반의 카드 레이아웃 대시보드
- 🌤️ **기후 데이터 통합**: OpenWeatherMap API를 통한 실시간 날씨 정보
- ⚡ **실시간 에너지 모니터링**: 에너지 생산/소비 실시간 추적
- 🚨 **재난 상황 관리**: 재난 이벤트 추적 및 영향 분석
- 🤖 **AI 오케스트레이터**: Multi-Agent 기반 의사결정 시스템

## 기술 스택

### Backend
- FastAPI (Python 3.11+)
- PostgreSQL + TimescaleDB
- Redis
- Apache Kafka
- MQTT (Mosquitto)
- Apache Jena Fuseki

### Frontend
- React 18 + TypeScript
- Material-UI (MUI)
- Mapbox GL JS
- Redux Toolkit
- TanStack Query

### Infrastructure
- Docker & Docker Compose
- TimescaleDB (시계열 데이터)

## 빠른 시작

### 사전 요구사항

- Docker & Docker Compose
- Node.js 20+ LTS
- Python 3.11+

### 설치 및 실행

1. **프로젝트 클론**
```bash
cd /Users/donghokim/Documents/myworkspace/AI_Agent/Disaster/energy-orchestrator-platform
```

2. **환경 변수 설정**
```bash
cp .env.example .env
# .env 파일을 편집하여 필요한 값 설정
```

3. **Docker 서비스 시작**
```bash
docker-compose up -d
```

4. **Backend 개발 서버 실행** (별도 터미널)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Frontend 개발 서버 실행** (별도 터미널)
```bash
cd frontend
npm install
npm run dev
```

### 서비스 접속 정보

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- MQTT Broker: localhost:1883
- Kafka: localhost:9092
- Jena Fuseki: http://localhost:3030

## 프로젝트 구조

```
energy-orchestrator-platform/
├── backend/              # FastAPI Backend
│   ├── src/
│   │   ├── api/v1/      # API 엔드포인트
│   │   ├── models/      # 데이터베이스 모델
│   │   ├── schemas/     # Pydantic 스키마
│   │   ├── services/    # 비즈니스 로직
│   │   ├── agents/      # AI 에이전트
│   │   └── ml/          # ML 모델
│   └── requirements.txt
│
├── frontend/            # React Frontend
│   ├── src/
│   │   ├── components/ # UI 컴포넌트
│   │   ├── pages/      # 페이지 컴포넌트
│   │   ├── services/   # API 서비스
│   │   └── store/      # Redux store
│   └── package.json
│
├── ontology/           # 온톨로지 스키마
├── ml-models/         # ML 모델 저장소
├── infrastructure/    # 인프라 설정
└── docker-compose.yml # Docker Compose 설정
```

## 주요 컴포넌트

### 카드 중심 UI
- Energy Balance Card: 에너지 생산/소비 밸런스
- Asset Status Card: 에너지 자산 상태
- Disaster Alert Card: 재난 알림
- Weather Card: 날씨 정보

### 지도 통합
- Mapbox GL JS를 사용한 인터랙티브 지도
- 에너지 자산 위치 표시
- 마커 클릭 시 상세 정보 팝업

### 기후 데이터
- OpenWeatherMap API 연동
- 실시간 날씨 정보
- 3일 예보
- 온도, 습도, 풍속 등 상세 정보

## 개발 가이드

자세한 개발 가이드는 `/Users/donghokim/Documents/myworkspace/AI_Agent/Disaster/Guide` 폴더의 문서를 참조하세요.

- `플랫폼_개발_가이드.md`: 전체 시스템 아키텍처 및 설계
- `프로젝트_구조_및_Quick_Start.md`: 프로젝트 구조 및 실행 가이드
- `핵심기능_구현_코드샘플.md`: 핵심 기능 구현 예제

## 라이센스

MIT License

## 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.




