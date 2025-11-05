# 협업 에너지 온톨로지 플랫폼 - 프로젝트 개요

## 🎯 프로젝트 목표

GnG International을 위한 **팔란티어(Palantir) 스타일의 협업 온톨로지 플랫폼**을 구축했습니다. 
이 시스템은 에너지 분야의 다양한 전문가들(사용자, 에너지 공급자, 기기 운영자, 에너지 전문가)이 
함께 에너지 도메인 온톨로지를 실시간으로 구축하고 관리할 수 있는 플랫폼입니다.

## 🏗️ 시스템 아키텍처

### 핵심 구성요소

1. **Frontend (React + TypeScript)**
   - Material-UI 기반 현대적인 UI
   - React Flow를 활용한 인터랙티브 온톨로지 시각화
   - WebSocket을 통한 실시간 협업

2. **Backend (FastAPI + Python)**
   - RESTful API 및 WebSocket 서버
   - JWT 기반 인증 및 역할 기반 권한 관리
   - RDFLib를 활용한 온톨로지 처리

3. **데이터베이스 계층**
   - PostgreSQL: 사용자, 프로젝트, 변경 이력 관리
   - InfluxDB: 시계열 에너지 데이터
   - Apache Jena Fuseki: RDF 온톨로지 저장 및 SPARQL 쿼리

4. **인프라 및 모니터링**
   - Docker & Docker Compose: 컨테이너화
   - Redis: 캐싱 및 작업 큐
   - Grafana & Prometheus: 모니터링 및 알림

## ✨ 주요 기능

### 1. 역할 기반 접근 제어 (RBAC)

| 역할 | 권한 | 설명 |
|------|------|------|
| End User | 읽기, 제안 | 데이터 조회 및 개선 제안 |
| Energy Provider | 읽기, 쓰기, 검증 | 공급 데이터 입력 및 검증 |
| Device Operator | 읽기, 쓰기, 장비 등록 | 장비 메타데이터 관리 |
| Energy Expert | 전체 읽기/쓰기, 승인 | 온톨로지 구조 설계 및 검증 |
| System Admin | 전체 권한 | 시스템 관리 및 보안 |

### 2. 실시간 협업 편집

- **WebSocket 기반**: 다중 사용자가 동시에 온톨로지 편집
- **변경 사항 동기화**: 모든 변경이 즉시 다른 사용자에게 전파
- **커서 위치 공유**: 다른 사용자의 작업 위치 실시간 표시

### 3. GitHub 스타일 변경 제안 시스템

```
제안 생성 → 자동 검증 → 전문가 검토 → 토론 → 승인/거절 → 자동 병합
```

- Pull Request와 유사한 워크플로우
- 코멘트 및 토론 기능
- 변경 이력 추적 및 롤백

### 4. 온톨로지 시각화

- **그래프 뷰**: 노드-링크 다이어그램으로 관계 표시
- **계층 뷰**: 트리 구조로 상속 관계 표시
- **검색 및 필터링**: SPARQL 기반 강력한 검색

### 5. 데이터 통합

- IoT 센서 데이터 실시간 연동
- 기상 데이터 (KMA, OpenWeatherMap)
- 전력 시장 데이터
- BMS/EMS 시스템 연동

## 📦 제공된 파일 구조

```
collaborative_ontology/
├── backend/                          # FastAPI 백엔드
│   ├── main.py                      # 메인 API 애플리케이션
│   ├── models.py                    # SQLAlchemy 데이터 모델
│   ├── Dockerfile                   # 백엔드 도커 이미지
│   └── requirements.txt             # Python 의존성
│
├── frontend/                         # React 프론트엔드
│   ├── App.tsx                      # 메인 React 컴포넌트
│   ├── Dockerfile                   # 프론트엔드 도커 이미지
│   └── package.json                 # Node.js 의존성
│
├── ontology/                         # 온톨로지 정의
│   └── energy_core.ttl              # 에너지 도메인 온톨로지
│
├── docs/                             # 문서
│   └── DEPLOYMENT_KR.md             # 배포 가이드 (한글)
│
├── docker-compose.yml                # Docker Compose 설정
├── deploy.sh                         # 자동 배포 스크립트
└── README.md                         # 프로젝트 개요

압축 파일:
└── collaborative_ontology.tar.gz     # 전체 프로젝트 압축본
```

## 🚀 빠른 시작

### 1. 압축 파일 다운로드 및 압축 해제

```bash
# 압축 파일 다운로드 (Claude에서 제공된 링크 사용)
# 압축 해제
tar -xzf collaborative_ontology.tar.gz
cd collaborative_ontology
```

### 2. 자동 배포 스크립트 실행

```bash
# 실행 권한 부여
chmod +x deploy.sh

# 배포 실행
./deploy.sh
```

이 스크립트가 자동으로 다음을 수행합니다:
- 필수 프로그램 확인 (Docker, Docker Compose, Git)
- 환경 변수 파일 생성
- Docker 이미지 빌드
- 모든 서비스 시작
- 데이터베이스 초기화
- 온톨로지 로드
- 테스트 사용자 생성

### 3. 서비스 접속

배포 완료 후 다음 URL로 접속:

- **프론트엔드**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **SPARQL 엔드포인트**: http://localhost:3030
- **Grafana**: http://localhost:3001
- **Prometheus**: http://localhost:9090

### 4. 로그인

```
Username: admin
Password: admin123
```

## 🔧 수동 설치 방법

자동 스크립트를 사용하지 않고 수동으로 설치하려면:

```bash
# 1. 환경 변수 설정
cp .env.example .env
nano .env  # 비밀번호 등 수정

# 2. Docker 이미지 빌드 및 실행
docker-compose build
docker-compose up -d

# 3. 데이터베이스 초기화
docker-compose exec backend alembic upgrade head

# 4. 온톨로지 로드
docker cp ontology/energy_core.ttl collaborative_ontology_fuseki:/fuseki/

# 5. 서비스 상태 확인
docker-compose ps
```

## 📊 에너지 온톨로지 구조

제공된 `energy_core.ttl` 파일에는 다음과 같은 클래스들이 정의되어 있습니다:

### 핵심 클래스
- `EnergySystem`: 모든 에너지 시스템의 기본 클래스
- `EnergySource`: 에너지 생성 시스템
- `EnergyConsumer`: 에너지 소비 시스템
- `EnergyStorage`: 에너지 저장 시스템
- `EnergyNetwork`: 에너지 배전 인프라

### 재생에너지 소스
- `SolarPowerPlant`: 태양광 발전소
- `WindTurbine`: 풍력 터빈
- `HydropowerPlant`: 수력 발전소
- `GeothermalPlant`: 지열 발전소

### 에너지 저장
- `BatteryEnergyStorageSystem`: 배터리 저장 시스템
- `PumpedHydroStorage`: 양수 발전
- `FlywheelEnergyStorage`: 플라이휠 저장
- `CompressedAirEnergyStorage`: 압축 공기 저장

### 그리드 인프라
- `PowerGrid`: 전력망
- `Microgrid`: 마이크로그리드
- `Substation`: 변전소
- `Transformer`: 변압기

### 특별 클래스
- `SolarGuardAI`: GnG International의 AI 예측 모델 (96% 정확도)

## 🔐 보안 고려사항

### 1. 인증 및 권한
- JWT 토큰 기반 인증
- 역할 기반 접근 제어 (RBAC)
- API 엔드포인트별 권한 체크

### 2. 데이터 보안
- 프로덕션 환경에서는 HTTPS 사용 필수
- 데이터베이스 연결 암호화
- 민감 정보 환경 변수로 관리

### 3. 운영 보안
- 모든 비밀번호를 강력한 값으로 변경
- 정기적인 보안 업데이트
- 감사 로그 활성화

## 📈 성능 최적화

### 추천 설정

**PostgreSQL**
```yaml
POSTGRES_SHARED_BUFFERS: 2GB
POSTGRES_EFFECTIVE_CACHE_SIZE: 6GB
POSTGRES_WORK_MEM: 64MB
```

**Fuseki**
```yaml
JVM_ARGS: "-Xmx4g -Xms2g"
```

**Redis**
```yaml
maxmemory: 2gb
maxmemory-policy: allkeys-lru
```

## 🔄 워크플로우 예시

### 새 온톨로지 클래스 추가

1. **사용자/운영자**: 제안 생성
```json
{
  "title": "풍력 터빈 클래스 추가",
  "change_type": "add_class",
  "data": {
    "uri": "http://gng-energy.com/ontology/core#WindTurbine",
    "label": "Wind Turbine",
    "parent_classes": ["EnergySource"]
  }
}
```

2. **시스템**: 자동 검증 실행
   - 온톨로지 일관성 체크
   - 중복 확인
   - 명명 규칙 검증

3. **전문가**: 검토 및 승인
   - 제안 내용 검토
   - 필요시 코멘트 추가
   - 승인 또는 거절

4. **시스템**: 자동 병합
   - 승인 시 온톨로지에 자동 추가
   - 모든 클라이언트에 실시간 업데이트
   - 버전 이력 저장

## 🌐 프로덕션 배포

### GCP (Google Cloud Platform) 배포

```bash
# 1. GKE 클러스터 생성
gcloud container clusters create ontology-cluster \
  --zone=asia-northeast3-a \
  --num-nodes=3

# 2. Kubernetes 배포
kubectl apply -f k8s/ --namespace=collaborative-ontology

# 3. 로드 밸런서 설정
kubectl apply -f k8s/ingress.yaml
```

자세한 내용은 `docs/DEPLOYMENT_KR.md` 참조

## 🔍 모니터링

### Grafana 대시보드

1. http://localhost:3001 접속
2. 로그인: admin / grafana_admin
3. Data Sources에서 InfluxDB 연결
4. 다음 메트릭 모니터링:
   - API 응답 시간
   - 동시 사용자 수
   - WebSocket 연결 수
   - 온톨로지 변경 빈도
   - 시스템 리소스 사용량

### Prometheus 메트릭

- CPU/메모리 사용량
- 데이터베이스 쿼리 성능
- API 엔드포인트별 응답 시간
- 에러율 및 성공률

## 🛠️ 개발 가이드

### Backend 로컬 개발

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend 로컬 개발

```bash
cd frontend
npm install
npm start
```

### API 테스트

```bash
# Swagger UI
http://localhost:8000/docs

# ReDoc
http://localhost:8000/redoc

# SPARQL 쿼리 예시
curl -X POST http://localhost:3030/ontology/sparql \
  -H "Content-Type: application/sparql-query" \
  -d "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10"
```

## 📚 추가 리소스

### 문서
- [시스템 아키텍처](collaborative_ontology_architecture.md)
- [배포 가이드](docs/DEPLOYMENT_KR.md)
- [API 문서](http://localhost:8000/docs)

### 코드
- [Backend 메인](backend_main.py)
- [Frontend App](frontend_App.tsx)
- [온톨로지](energy_core.ttl)

### 설정
- [Docker Compose](docker-compose.yml)
- [배포 스크립트](deploy.sh)

## 🤝 기여 및 지원

### 문의
- **이메일**: dongho@gng-energy.com
- **회사**: GnG International
- **GitHub**: [저장소 URL]

### 기여 방법
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📋 로드맵

### Phase 1 (완료)
- ✅ 기본 아키텍처 설계
- ✅ 역할 기반 접근 제어
- ✅ 실시간 협업 기능
- ✅ 변경 제안 시스템

### Phase 2 (Q1 2025)
- AI 기반 온톨로지 추천
- 자동 데이터 매핑
- 모바일 앱
- 고급 분석 도구

### Phase 3 (Q2 2025)
- 블록체인 기반 검증
- 다국어 지원 (한국어, 영어)
- 플러그인 시스템
- 엔터프라이즈 기능

## ⚠️ 중요 참고사항

1. **프로덕션 배포 전**:
   - 모든 비밀번호를 강력한 값으로 변경
   - HTTPS 설정
   - 정기 백업 스케줄 설정
   - 방화벽 규칙 설정

2. **성능**:
   - 최소 8GB RAM 권장
   - SSD 스토리지 권장
   - 프로덕션 환경에서는 별도 데이터베이스 서버 사용 권장

3. **보안**:
   - `.env` 파일을 절대 Git에 커밋하지 말 것
   - 정기적인 보안 패치 적용
   - 접근 로그 모니터링

## 🎉 결론

이 시스템은 GnG International의 에너지 관리 플랫폼에 통합되어 다양한 이해관계자들이 
협력적으로 에너지 온톨로지를 구축하고 관리할 수 있는 강력한 도구를 제공합니다.

팔란티어 스타일의 데이터 통합과 실시간 협업 기능으로 에너지 도메인 지식을 
체계적으로 관리하고 공유할 수 있습니다.

**시작하려면 `deploy.sh`를 실행하세요!**

---

*Made with ❤️ for GnG International*
*Powered by Claude AI*
