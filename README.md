# AI Agent Services

나노그리드 운영 시스템을 위한 AI Agent 서비스 모음입니다.

## 프로젝트 구조

- **agent/**: 메인 에이전트 서비스 (gateway, services, libs)
- **Disaster/**: 재해 대응 서비스
- **Energy_Agent/**: 에너지 에이전트 서비스
- **Merit/**: ETM React 서비스
- **NanoGrid/**: 나노그리드 관련 모듈 및 스켈레톤

## 주요 서비스

### Gateway
- **gateway/**: FastAPI 기반 게이트웨이
- **gateway-nest/**: NestJS 기반 게이트웨이 (BFF)

### Services
- **dt/**: Digital Twin 서비스
- **eop/**: Energy Optimization Platform
- **forecast/**: 예측 서비스
- **monitoring/**: 모니터링 서비스
- **engagement/**: 사용자 참여 서비스

## 시작하기

### Docker Compose로 실행

```bash
cd agent
docker compose up --build
```

### 접속 정보
- **Swagger UI**: http://localhost:8080/docs
- **GraphQL Playground**: http://localhost:8080/graphql
- **Metrics**: http://localhost:8080/metrics

## 기술 스택

- **Backend**: Python (FastAPI), TypeScript (NestJS)
- **Database**: Redis
- **Container**: Docker, Docker Compose
- **Orchestration**: Kubernetes
- **Observability**: OpenTelemetry, Prometheus

## 라이선스

See LICENSE file for details.
