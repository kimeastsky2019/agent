# 가상 데이터 생성 스크립트

## 개요

이 디렉토리에는 시스템의 전체 서비스가 작동하도록 가상 데이터를 생성하는 스크립트가 포함되어 있습니다.

## 사용 방법

### 1. 가상 데이터 생성

```bash
cd backend
python3 scripts/generate_mock_data.py
```

또는 Docker 컨테이너 내에서:

```bash
docker-compose exec backend python scripts/generate_mock_data.py
```

### 2. 생성되는 데이터

스크립트는 다음 데이터를 생성합니다:

- **자산 (Assets)**: 11개의 에너지 자산
  - 태양광 발전소 (Solar)
  - 풍력 발전소 (Wind)
  - 배터리 저장소 (Battery)
  - 수요 섹터 (Demand)

- **재난 (Disasters)**: 8개의 재난 이벤트
  - 활성 재난: 3개
  - 해결된 재난: 5개
  - 재난 유형: 지진, 태풍, 홍수, 산불

- **에너지 측정값**: 216개의 측정값
  - 최근 24시간 데이터
  - 생산량 및 소비량

- **수요 데이터**: 279개의 수요 분석 데이터
  - 최근 93일 데이터
  - 일일 소비량 및 피크 수요

- **공급 데이터**: 120개의 공급 분석 데이터
  - 최근 30일 데이터
  - 일일 생산량 및 효율

### 3. 데이터 저장 위치

생성된 데이터는 다음 위치에 저장됩니다:

```
backend/data/mock/mock_data.json
```

### 4. 데이터 사용

API 엔드포인트들은 `src/data/mock_data.py` 모듈을 통해 이 가상 데이터를 자동으로 로드합니다.

- 데이터 파일이 있으면: 파일에서 로드
- 데이터 파일이 없으면: 기본 데이터 생성

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

### 에너지 측정값 (Energy Reading)

```json
{
  "time": "2024-01-01T00:00:00",
  "device_id": "asset_id",
  "metric_type": "production",
  "value": 500.0,
  "unit": "kW"
}
```

## API 엔드포인트 테스트

가상 데이터가 생성된 후 다음 API를 테스트할 수 있습니다:

### 자산 API

```bash
# 자산 목록 조회
curl http://localhost:8000/api/v1/assets

# 특정 자산 조회
curl http://localhost:8000/api/v1/assets/{asset_id}
```

### 재난 API

```bash
# 재난 목록 조회
curl http://localhost:8000/api/v1/disasters

# 활성 재난 조회
curl http://localhost:8000/api/v1/disasters/active
```

### 에너지 API

```bash
# 에너지 밸런스
curl http://localhost:8000/api/v1/energy/balance

# 생산량 조회
curl http://localhost:8000/api/v1/energy/production

# 소비량 조회
curl http://localhost:8000/api/v1/energy/consumption
```

### 수요 분석 API

```bash
# 수요 분석
curl http://localhost:8000/api/v1/demand/analysis/{asset_id}
```

### 공급 분석 API

```bash
# 공급 분석
curl http://localhost:8000/api/v1/supply/analysis/{asset_id}

# 실시간 전력 데이터
curl http://localhost:8000/api/v1/supply/realtime/{asset_id}?range=hour
```

## 주의사항

- 가상 데이터는 개발 및 테스트 목적으로만 사용됩니다.
- 프로덕션 환경에서는 실제 데이터베이스를 사용해야 합니다.
- 데이터를 재생성하면 기존 데이터가 덮어씌워집니다.




