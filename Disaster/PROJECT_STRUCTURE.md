# Disaster 프로젝트 전체 구조

## 📁 디렉토리 구조

```
Disaster/
├── Guide/                          # 프로젝트 가이드 문서
│   ├── README_시작가이드.md
│   ├── 프로젝트_구조_및_Quick_Start.md
│   ├── 프로젝트_핵심요약.md
│   ├── 플랫폼_개발_가이드.md
│   └── 핵심기능_구현_코드샘플.md
│
├── energy-orchestrator-platform/   # 메인 플랫폼 (통합 서비스)
│   ├── backend/                    # FastAPI 백엔드
│   │   ├── Dockerfile
│   │   ├── Dockerfile.prod
│   │   ├── requirements.txt
│   │   ├── data/
│   │   │   └── mock/
│   │   │       └── mock_data.json
│   │   ├── scripts/
│   │   │   ├── generate_mock_data.py
│   │   │   └── README.md
│   │   └── src/
│   │       ├── agents/             # AI 에이전트
│   │       │   ├── base_agent.py
│   │       │   ├── decision_maker.py
│   │       │   ├── disaster_analyzer.py
│   │       │   └── energy_analyzer.py
│   │       ├── api/                # API 엔드포인트
│   │       │   └── v1/
│   │       │       ├── assets.py
│   │       │       ├── auth.py
│   │       │       ├── demand.py
│   │       │       ├── devices.py
│   │       │       ├── disasters.py
│   │       │       ├── energy.py
│   │       │       ├── orchestrator.py
│   │       │       ├── supply.py
│   │       │       ├── users.py
│   │       │       └── weather.py
│   │       ├── config.py           # 설정 관리
│   │       ├── database.py         # 데이터베이스 연결
│   │       ├── main.py             # FastAPI 앱 진입점
│   │       ├── models/             # 데이터 모델
│   │       ├── schemas/            # Pydantic 스키마
│   │       │   ├── asset.py
│   │       │   ├── device.py
│   │       │   ├── disaster.py
│   │       │   ├── energy.py
│   │       │   ├── orchestrator.py
│   │       │   ├── user.py
│   │       │   └── weather.py
│   │       └── services/           # 비즈니스 로직
│   │           ├── auth_service.py
│   │           ├── demand_analysis_service.py
│   │           ├── supply_analysis_service.py
│   │           └── weather_service.py
│   │
│   ├── frontend/                    # React + TypeScript 프론트엔드
│   │   ├── Dockerfile
│   │   ├── Dockerfile.prod
│   │   ├── nginx.conf
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── vite.config.ts
│   │   ├── public/
│   │   │   └── index.html
│   │   └── src/
│   │       ├── App.tsx
│   │       ├── main.tsx
│   │       ├── components/          # React 컴포넌트
│   │       │   ├── AddAssetDialog.tsx
│   │       │   ├── AssetCard.tsx
│   │       │   ├── Dashboard/
│   │       │   ├── DisasterAlert/
│   │       │   ├── EnergyMap.tsx
│   │       │   ├── Layout.tsx
│   │       │   ├── ServiceCard.tsx
│   │       │   └── WeatherCard.tsx
│   │       ├── contexts/
│   │       │   └── AuthContext.tsx
│   │       ├── pages/              # 페이지 컴포넌트
│   │       │   ├── Analytics.tsx
│   │       │   ├── Assets.tsx
│   │       │   ├── DemandAnalysis.tsx
│   │       │   ├── Disasters.tsx
│   │       │   ├── Home.tsx
│   │       │   ├── Login.tsx
│   │       │   └── SupplyAnalysis.tsx
│   │       ├── services/
│   │       │   └── api.ts
│   │       ├── store/              # Redux 상태 관리
│   │       │   ├── slices/
│   │       │   │   ├── authSlice.ts
│   │       │   │   ├── disasterSlice.ts
│   │       │   │   └── energySlice.ts
│   │       │   └── store.ts
│   │       ├── styles/
│   │       │   └── theme.ts
│   │       └── types/
│   │           └── index.ts
│   │
│   ├── docker-compose.yml          # 개발 환경 Docker Compose
│   ├── docker-compose.prod.yml     # 프로덕션 환경 Docker Compose
│   ├── deploy.sh                   # 배포 스크립트
│   ├── deploy-full.sh
│   ├── deploy-to-server.sh
│   ├── start-backend.sh
│   ├── start-frontend.sh
│   ├── setup-domain.sh
│   ├── env.example                 # 환경변수 예제
│   │
│   ├── CODE_REVIEW.md              # 코드 검토 보고서
│   ├── DEPLOYMENT.md               # 배포 가이드
│   ├── DEPLOYMENT_CHECKLIST.md     # 배포 체크리스트
│   ├── DEPLOY_INSTRUCTIONS.md
│   ├── DEPLOY_NOW.md
│   ├── QUICK_DEPLOY.md
│   ├── QUICK_START.md
│   ├── README.md
│   ├── INTEGRATION_GUIDE.md
│   ├── DIGITALTWIN_INTEGRATION_GUIDE.md
│   ├── SUPPLY_INTEGRATION_GUIDE.md
│   ├── WEATHER_INTEGRATION_GUIDE.md
│   └── MOCK_DATA_GUIDE.md
│
├── ontology_service/               # 온톨로지 서비스
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements.txt
│   ├── app.py                      # Flask 메인 애플리케이션
│   ├── ontology_builder.py        # 온톨로지 생성 및 관리
│   ├── data_processor.py          # 데이터 분석 및 처리
│   ├── frontend.html               # 웹 인터페이스
│   ├── test_api.py                # API 테스트
│   ├── quick_start.sh
│   ├── quick_start.bat
│   ├── example_data/
│   │   └── sample_timeseries.csv
│   ├── README.md
│   ├── ADVANCED_GUIDE.md
│   └── PROJECT_SUMMARY.md
│
├── image_brodcasting/              # 이미지 방송 서비스 (안전 모니터링)
│   ├── Dockerfile
│   ├── app.py                      # Flask 애플리케이션
│   ├── dashboard.html              # 대시보드
│   ├── generate_demo_data.py      # 데모 데이터 생성
│   ├── test_system.py             # 시스템 테스트
│   ├── requirements.txt
│   ├── start.sh
│   ├── README.md
│   ├── QUICKSTART.md
│   └── SYSTEM_OVERVIEW.md
│
├── supply_analysis/                # 공급 분석 서비스
│   ├── docker-compose.yml
│   ├── start.sh
│   ├── README.md
│   ├── ai-agent/                   # AI 에이전트 서비스
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── app/
│   │       ├── main.py
│   │       └── agents/
│   │           ├── anomaly_detector.py
│   │           ├── fault_diagnostics.py
│   │           └── production_forecaster.py
│   ├── backend/                    # 백엔드 API
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── app/
│   │       ├── main.py
│   │       └── api/
│   │           ├── energy.py
│   │           ├── facilities.py
│   │           └── weather.py
│   ├── frontend/                   # React 프론트엔드
│   │   ├── Dockerfile
│   │   ├── package.json
│   │   └── src/
│   │       ├── App.jsx
│   │       ├── index.js
│   │       ├── components/
│   │       │   ├── AIAlertsPanel.jsx
│   │       │   ├── EnergyBarChart.jsx
│   │       │   ├── FacilityCard.jsx
│   │       │   ├── Header.jsx
│   │       │   ├── RealtimePowerChart.jsx
│   │       │   └── WeatherCard.jsx
│   │       ├── services/
│   │       │   └── api.js
│   │       └── theme/
│   │           └── theme.js
│   └── docs/
│       ├── AI_AGENT.md
│       ├── API.md
│       └── DEPLOYMENT.md
│
├── demand_analysis/                # 수요 분석 서비스
│   ├── energy_agent.py             # 에너지 에이전트
│   ├── energy_dashboard.html      # 대시보드
│   ├── energy_predictions.csv     # 예측 결과
│   ├── processed_energy_data.csv  # 처리된 데이터
│   ├── analysis_summary.json      # 분석 요약
│   └── README.md
│
├── digitaltwin_matching/           # 디지털 트윈 매칭
│   ├── smart_grid_digital_twin.py # 스마트 그리드 디지털 트윈
│   ├── advanced_scenarios.py      # 고급 시나리오
│   ├── dashboard.html             # 대시보드
│   ├── smart_grid_simulation_results.csv
│   └── README.md
│
└── weather-app/                    # 날씨 애플리케이션
    ├── package.json
    ├── README.md
    ├── public/
    │   └── index.html
    ├── build/                      # 빌드 결과물
    │   ├── asset-manifest.json
    │   └── static/
    └── src/
        ├── App.js
        ├── index.js
        ├── i18n.js                 # 다국어 지원
        ├── components/
        │   ├── EnergyCorrelations.js
        │   ├── ErrorBoundary.js
        │   ├── Header.js
        │   ├── LanguageSelector.js
        │   ├── LoadingSpinner.js
        │   ├── Sidebar.js
        │   ├── SimpleWeatherDashboard.js
        │   ├── WeatherCharts.js
        │   ├── WeatherDashboard.js
        │   ├── WeatherMap.js
        │   ├── WeatherPredictions.js
        │   └── WeatherStats.js
        └── services/
            └── weatherService.js
```

---

## 📊 주요 서비스 개요

### 1. energy-orchestrator-platform (메인 플랫폼)
- **기술 스택**: FastAPI (Backend), React + TypeScript (Frontend)
- **주요 기능**:
  - 에너지 관리 및 모니터링
  - 재난 분석 및 대응
  - IoT 디바이스 관리
  - AI 기반 의사결정
- **통합 서비스**:
  - ontology-service
  - image-broadcasting
  - supply_analysis
  - demand_analysis

### 2. ontology_service
- **기술 스택**: Flask, RDFLib
- **주요 기능**:
  - 온톨로지 생성 및 관리
  - 시계열 데이터 분석
  - 이미지 데이터 분석
  - SPARQL 쿼리

### 3. image_broadcasting
- **기술 스택**: Flask
- **주요 기능**:
  - 실시간 안전 모니터링
  - CCTV 영상 분석
  - 위험 상황 탐지
  - 자동 경보 시스템

### 4. supply_analysis
- **기술 스택**: FastAPI (Backend), React (Frontend)
- **주요 기능**:
  - 공급 분석
  - AI 기반 이상 탐지
  - 고장 진단
  - 생산 예측

### 5. demand_analysis
- **기술 스택**: Python
- **주요 기능**:
  - 수요 분석
  - 에너지 예측
  - 대시보드 시각화

### 6. digitaltwin_matching
- **기술 스택**: Python
- **주요 기능**:
  - 스마트 그리드 디지털 트윈
  - 시뮬레이션
  - 시나리오 분석

### 7. weather-app
- **기술 스택**: React
- **주요 기능**:
  - 날씨 정보 표시
  - 에너지 상관관계 분석
  - 다국어 지원

---

## 🔧 주요 설정 파일

### Docker Compose 파일
- `energy-orchestrator-platform/docker-compose.yml` - 개발 환경
- `energy-orchestrator-platform/docker-compose.prod.yml` - 프로덕션 환경
- `ontology_service/docker-compose.yml` - 온톨로지 서비스
- `supply_analysis/docker-compose.yml` - 공급 분석 서비스

### Dockerfile
- `energy-orchestrator-platform/backend/Dockerfile` - 백엔드 개발
- `energy-orchestrator-platform/backend/Dockerfile.prod` - 백엔드 프로덕션
- `energy-orchestrator-platform/frontend/Dockerfile` - 프론트엔드 개발
- `energy-orchestrator-platform/frontend/Dockerfile.prod` - 프론트엔드 프로덕션
- `ontology_service/Dockerfile` - 온톨로지 서비스
- `image_brodcasting/Dockerfile` - 이미지 방송 서비스
- `supply_analysis/*/Dockerfile` - 공급 분석 서비스들

### 배포 스크립트
- `energy-orchestrator-platform/deploy.sh` - 메인 배포 스크립트
- `energy-orchestrator-platform/deploy-full.sh` - 전체 배포
- `energy-orchestrator-platform/deploy-to-server.sh` - 서버 배포
- `supply_analysis/start.sh` - 공급 분석 시작
- `image_brodcasting/start.sh` - 이미지 방송 시작
- `ontology_service/quick_start.sh` - 온톨로지 서비스 시작

---

## 📚 문서 파일

### 가이드 문서 (Guide/)
- `README_시작가이드.md` - 시작 가이드
- `프로젝트_구조_및_Quick_Start.md` - 프로젝트 구조 및 빠른 시작
- `프로젝트_핵심요약.md` - 프로젝트 핵심 요약
- `플랫폼_개발_가이드.md` - 플랫폼 개발 가이드
- `핵심기능_구현_코드샘플.md` - 핵심 기능 구현 코드 샘플

### 메인 플랫폼 문서
- `README.md` - 메인 README
- `QUICK_START.md` - 빠른 시작 가이드
- `QUICK_DEPLOY.md` - 빠른 배포 가이드
- `DEPLOYMENT.md` - 상세 배포 가이드
- `DEPLOYMENT_CHECKLIST.md` - 배포 체크리스트
- `CODE_REVIEW.md` - 코드 검토 보고서
- `INTEGRATION_GUIDE.md` - 통합 가이드
- `DIGITALTWIN_INTEGRATION_GUIDE.md` - 디지털 트윈 통합 가이드
- `SUPPLY_INTEGRATION_GUIDE.md` - 공급 분석 통합 가이드
- `WEATHER_INTEGRATION_GUIDE.md` - 날씨 통합 가이드

### 서비스별 문서
- `ontology_service/README.md` - 온톨로지 서비스 README
- `ontology_service/ADVANCED_GUIDE.md` - 고급 가이드
- `image_brodcasting/README.md` - 이미지 방송 README
- `image_brodcasting/QUICKSTART.md` - 빠른 시작
- `supply_analysis/README.md` - 공급 분석 README
- `supply_analysis/docs/*` - API 및 배포 문서

---

## 🚀 빠른 시작

### 1. 메인 플랫폼 실행
```bash
cd energy-orchestrator-platform
docker-compose up -d
```

### 2. 온톨로지 서비스 실행
```bash
cd ontology_service
docker-compose up -d
```

### 3. 이미지 방송 서비스 실행
```bash
cd image_brodcasting
./start.sh
```

### 4. 공급 분석 서비스 실행
```bash
cd supply_analysis
./start.sh
```

---

## 📝 파일 통계

- **Python 파일**: ~50개
- **TypeScript/JavaScript 파일**: ~40개
- **Markdown 문서**: ~30개
- **Dockerfile**: 9개
- **Docker Compose 파일**: 4개
- **설정 파일**: 다수

---

**마지막 업데이트**: 2025-01-XX

