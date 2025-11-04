# 가상 데이터 가이드

## 개요

시스템의 전체 서비스가 작동하도록 가상 데이터가 생성되었습니다. 이 가이드는 가상 데이터를 생성하고 사용하는 방법을 설명합니다.

## 빠른 시작

### 1. 가상 데이터 생성

```bash
cd backend
python3 scripts/generate_mock_data.py
```

이 명령어는 다음을 생성합니다:
- **11개의 에너지 자산** (태양광, 풍력, 배터리, 수요 섹터)
- **8개의 재난 이벤트** (활성 3개, 해결됨 5개)
- **216개의 에너지 측정값** (최근 24시간)
- **279개의 수요 데이터** (최근 93일)
- **120개의 공급 데이터** (최근 30일)

### 2. 서비스 시작

```bash
# Docker Compose로 전체 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 3. 프론트엔드 접속

브라우저에서 다음 URL에 접속:
- 프론트엔드: http://localhost:3000
- 백엔드 API: http://localhost:8000
- API 문서: http://localhost:8000/docs

## 생성된 데이터 상세

### 자산 (Assets)

다양한 유형의 에너지 자산이 생성됩니다:

- **태양광 발전소** (Solar): 500-5000 kW 용량
- **풍력 발전소** (Wind): 1000-3000 kW 용량
- **배터리 저장소** (Battery): 200-1000 kW 용량
- **수요 섹터** (Demand): 에너지 소비 지역

위치: 도쿄, 오사카, 요코하마, 나고야, 후쿠오카

### 재난 (Disasters)

다양한 유형의 재난 이벤트:

- **지진** (Earthquake): 심각도 3-7
- **태풍** (Typhoon): 심각도 2-5
- **홍수** (Flood): 심각도 1-4
- **산불** (Wildfire): 심각도 2-5

### 에너지 데이터

- **생산 데이터**: 시간대별 패턴 반영 (태양광은 낮에 높음)
- **소비 데이터**: 시간대별 패턴 반영 (아침/저녁 피크)
- **밸런스**: 생산량과 소비량의 차이 계산

## API 엔드포인트 테스트

### 자산 관리

```bash
# 자산 목록 조회
curl http://localhost:8000/api/v1/assets

# 자산 생성
curl -X POST http://localhost:8000/api/v1/assets \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Solar Farm",
    "type": "solar",
    "capacity_kw": 2000.0,
    "location": {"lat": 35.6762, "lon": 139.6503}
  }'

# 특정 자산 조회
curl http://localhost:8000/api/v1/assets/{asset_id}

# 자산 삭제
curl -X DELETE http://localhost:8000/api/v1/assets/{asset_id}
```

### 재난 모니터링

```bash
# 재난 목록 조회
curl http://localhost:8000/api/v1/disasters

# 활성 재난만 조회
curl http://localhost:8000/api/v1/disasters/active

# 특정 재난 조회
curl http://localhost:8000/api/v1/disasters/{disaster_id}
```

### 에너지 관리

```bash
# 에너지 밸런스
curl http://localhost:8000/api/v1/energy/balance

# 생산량 조회
curl http://localhost:8000/api/v1/energy/production

# 소비량 조회
curl http://localhost:8000/api/v1/energy/consumption
```

### 수요 분석

```bash
# 수요 분석 결과 조회
curl http://localhost:8000/api/v1/demand/analysis/{asset_id}

# 수요 분석 실행
curl -X POST http://localhost:8000/api/v1/demand/analysis/{asset_id}/analyze
```

### 공급 분석

```bash
# 공급 분석 결과 조회
curl http://localhost:8000/api/v1/supply/analysis/{asset_id}

# 실시간 전력 데이터
curl http://localhost:8000/api/v1/supply/realtime/{asset_id}?range=hour

# 생산량 예측
curl http://localhost:8000/api/v1/supply/forecast/{asset_id}?days=7

# 이상 탐지
curl http://localhost:8000/api/v1/supply/anomalies/{asset_id}

# 시설 정보
curl http://localhost:8000/api/v1/supply/facility/{asset_id}
```

### 디지털 트윈

```bash
# 디지털 트윈 상태 조회
curl http://localhost:8000/api/v1/digitaltwin/state/{asset_id}

# 디지털 트윈 초기화
curl -X POST http://localhost:8000/api/v1/digitaltwin/initialize/{asset_id}

# 제어 사이클 실행
curl -X POST http://localhost:8000/api/v1/digitaltwin/cycle/{asset_id}

# 성능 지표 조회
curl http://localhost:8000/api/v1/digitaltwin/metrics/{asset_id}

# 시뮬레이션 시작
curl http://localhost:8000/api/v1/digitaltwin/simulation/{asset_id}?duration_hours=24&time_step_minutes=15
```

## 데이터 구조

### 자산 (Asset)

```json
{
  "id": "uuid",
  "name": "Solar Farm Tokyo",
  "type": "solar",
  "capacity_kw": 1000.0,
  "location": {
    "lat": 35.6762,
    "lon": 139.6503
  },
  "status": "online",
  "service_type": "supply",
  "created_at": "2024-01-01T00:00:00"
}
```

### 재난 (Disaster)

```json
{
  "id": "uuid",
  "event_type": "earthquake",
  "severity": 4,
  "location": {
    "lat": 35.6762,
    "lon": 139.6503
  },
  "affected_radius_km": 50.0,
  "start_time": "2024-01-01T00:00:00",
  "end_time": null,
  "status": "active"
}
```

### 에너지 밸런스

```json
{
  "total_production": 1500.0,
  "total_consumption": 800.0,
  "balance": 700.0,
  "timestamp": "2024-01-01T00:00:00"
}
```

## 데이터 저장 위치

가상 데이터는 다음 위치에 저장됩니다:

```
backend/data/mock/mock_data.json
```

## 데이터 재생성

데이터를 다시 생성하려면:

```bash
cd backend
python3 scripts/generate_mock_data.py
```

**주의**: 이 작업은 기존 데이터를 덮어씁니다.

## 시스템 동작 확인

### 1. 프론트엔드에서 확인

1. http://localhost:3000 접속
2. 자산 목록 페이지에서 생성된 자산 확인
3. 재난 페이지에서 재난 이벤트 확인
4. 에너지 대시보드에서 에너지 밸런스 확인
5. 수요/공급 분석 페이지에서 분석 결과 확인

### 2. API 문서에서 확인

1. http://localhost:8000/docs 접속
2. 각 API 엔드포인트를 "Try it out"으로 테스트
3. 응답 데이터 확인

### 3. 로그 확인

```bash
# 백엔드 로그
docker-compose logs backend

# 프론트엔드 로그
docker-compose logs frontend

# 전체 로그
docker-compose logs -f
```

## 문제 해결

### 데이터가 로드되지 않는 경우

1. 데이터 파일이 생성되었는지 확인:
   ```bash
   ls -la backend/data/mock/mock_data.json
   ```

2. 데이터 생성 스크립트 다시 실행:
   ```bash
   cd backend
   python3 scripts/generate_mock_data.py
   ```

3. 백엔드 재시작:
   ```bash
   docker-compose restart backend
   ```

### API가 데이터를 반환하지 않는 경우

1. API 문서에서 직접 테스트: http://localhost:8000/docs
2. 백엔드 로그 확인:
   ```bash
   docker-compose logs backend
   ```
3. 데이터 파일 형식 확인:
   ```bash
   cat backend/data/mock/mock_data.json | jq '.assets | length'
   ```

## 다음 단계

1. **실제 데이터 연동**: 실제 데이터베이스와 연동
2. **외부 API 연동**: 날씨 API, 재난 API 등 실제 데이터 소스 연결
3. **ML 모델 통합**: 실제 머신러닝 모델로 예측 및 분석
4. **실시간 스트리밍**: WebSocket을 통한 실시간 데이터 스트리밍

## 참고 자료

- [가상 데이터 생성 스크립트 README](backend/scripts/README.md)
- [API 문서](http://localhost:8000/docs)
- [프로젝트 구조 가이드](프로젝트_구조_및_Quick_Start.md)




