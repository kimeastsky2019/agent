# Digital Twin 통합 가이드

## ✅ 통합 완료 사항

digitaltwin_matching 시스템을 메인 애플리케이션에 실시간으로 통합했습니다.

## 🎯 주요 기능

### 1. 디지털 트윈 실시간 모니터링
- **실시간 시뮬레이션**: 2초 간격으로 자동 업데이트
- **전력 수요-공급 모니터링**: 실시간 수요/공급/균형 표시
- **ESS 상태**: 실시간 SOC (State of Charge) 표시
- **환경 데이터**: 온도, 일사량, 풍속, 재실 인원
- **공급원 상태**: 태양광, 풍력, 전력망 실시간 출력

### 2. AI 에이전트 제어
- **수요 반응 에이전트**: 전력 부족 시 우선순위 기반 제어
- **공급 최적화 에이전트**: 재생에너지 우선 사용 전략
- **가격 결정 에이전트**: 동적 전력 가격 결정

### 3. 실시간 시각화
- **전력 수요-공급 차트**: Area Chart로 실시간 추이 표시
- **성능 지표 차트**: 재생에너지 비율, 안정성, 비용 효율성, 종합 점수
- **공급원 상태**: 진행률 바로 실시간 출력 표시
- **ESS SOC**: 진행률 바로 SOC 표시

### 4. 성능 메트릭
- **재생에너지 비율**: 평균 재생에너지 활용률
- **안정성 점수**: 전력 균형 안정성
- **비용 효율성**: 비용 최적화 점수
- **종합 점수**: 전체 성능 지표

## 📁 추가된 파일

### Backend
- `backend/src/services/digitaltwin_service.py`: 디지털 트윈 서비스
- `backend/src/services/smart_grid_digital_twin.py`: 스마트 그리드 디지털 트윈 로직
- `backend/src/api/v1/digitaltwin.py`: 디지털 트윈 API 엔드포인트

### Frontend
- `frontend/src/pages/DigitalTwin.tsx`: 디지털 트윈 실시간 모니터링 페이지

## 🔄 사용 방법

### 1. 디지털 트윈 접속
- **자산 관리 페이지**: 각 자산 카드의 "디지털 트윈" 버튼 클릭
- **서비스 카드**: "디지털 트윈 실시간 모니터링" 카드의 "열기" 버튼 클릭
- **직접 접속**: `/digital-twin/{assetId}` 경로로 접속

### 2. 시뮬레이션 시작
1. "시뮬레이션 시작" 버튼 클릭
2. 자동으로 2초 간격으로 제어 사이클 실행
3. 실시간으로 데이터 업데이트

### 3. 시뮬레이션 중지
- "시뮬레이션 중지" 버튼 클릭
- 자동 업데이트 중지

### 4. 새로고침
- "새로고침" 버튼으로 최신 상태 확인

## 🛠️ API 엔드포인트

### Digital Twin API
- `GET /api/v1/digitaltwin/state/{asset_id}`: 현재 상태 조회
- `POST /api/v1/digitaltwin/initialize/{asset_id}`: 디지털 트윈 초기화
- `POST /api/v1/digitaltwin/cycle/{asset_id}`: 제어 사이클 실행
- `GET /api/v1/digitaltwin/metrics/{asset_id}`: 성능 지표 조회
- `GET /api/v1/digitaltwin/simulation/{asset_id}`: 시뮬레이션 시작
- `WebSocket /api/v1/digitaltwin/stream/{asset_id}`: 실시간 스트림 (향후 구현)

## 📊 데이터 구조

### Digital Twin State
```typescript
{
  asset_id: string
  timestamp: string
  environment: {
    temperature: number
    solar_radiation: number
    wind_speed: number
    occupancy: number
    humidity: number
  }
  power: {
    total_demand: number
    total_supply: number
    balance: number
    ess_soc: number
  }
  devices: {
    total: number
    active: number
    consumption: number
  }
  supplies: Array<{
    source_id: string
    source_type: string
    capacity: number
    current_output: number
    available: number
  }>
  ess: {
    capacity: number
    current_soc: number
    max_charge_rate: number
    max_discharge_rate: number
  }
}
```

### Control Cycle Result
```typescript
{
  asset_id: string
  timestamp: string
  environment: {
    temperature: number
    solar_radiation: number
    wind_speed: number
    occupancy: number
  }
  power: {
    total_demand: number
    total_supply: number
    balance: number
    ess_soc: number
  }
  supply_optimization: {
    agent: string
    renewable_ratio: number
    supply_plan: Array<any>
  }
  demand_response: {
    agent: string
    decisions: Array<any>
  }
  pricing: {
    agent: string
    price_kwh: number
  }
  performance_metrics: {
    renewable_ratio: number
    stability_score: number
    cost_efficiency: number
    ess_utilization: number
    overall_score: number
  }
}
```

## 🎨 UI 구성

### Digital Twin 페이지
1. **헤더**: 제목 + 시뮬레이션 시작/중지 버튼 + 새로고침 버튼
2. **상태 표시**: 시뮬레이션 실행 중 표시
3. **전력 메트릭 카드**: 수요, 공급, 균형, ESS SOC
4. **환경 데이터 카드**: 온도, 습도, 일사량, 풍속, 재실 인원
5. **공급원 상태 카드**: 태양광, 풍력, 전력망 출력
6. **전력 수요-공급 차트**: Area Chart
7. **성능 지표 차트**: Line Chart
8. **성능 메트릭 카드**: 재생에너지 비율, 안정성, 비용 효율성, 종합 점수

## 🔧 주요 기능 상세

### 1. 실시간 시뮬레이션
- **업데이트 간격**: 2초마다 자동 업데이트
- **제어 사이클**: AI 에이전트 협업 제어
- **데이터 저장**: 최근 100개 사이클 데이터 유지

### 2. AI 에이전트
- **수요 반응 에이전트**: 우선순위 기반 부하 제어
- **공급 최적화 에이전트**: 재생에너지 우선 사용
- **가격 결정 에이전트**: 동적 가격 결정

### 3. 차트 시각화
- **Area Chart**: 전력 수요-공급 추이
- **Line Chart**: 성능 지표 추이
- **실시간 업데이트**: 데이터 추가 시 자동 갱신

### 4. 성능 메트릭
- **재생에너지 비율**: 평균 재생에너지 활용률
- **안정성 점수**: 전력 균형 안정성 (70% 이상 목표)
- **비용 효율성**: 비용 최적화 점수 (80% 이상 목표)
- **종합 점수**: 전체 성능 지표 (70% 이상 목표)

## 📝 시뮬레이션 모델

### 수요 측
- **48개 디바이스**: 교실 20개, 사무실 5개, 급식실 3개
- **제어 모드**: 제어가능, 선택제어, 제어불가
- **우선순위**: 1(높음) ~ 10(낮음)

### 공급 측
- **태양광**: 최대 100kW (일사량 기반)
- **풍력**: 최대 50kW (풍속 기반)
- **ESS**: 200kWh 용량, 50kW 충방전
- **전력망**: 500kW 백업 전원

### 환경 데이터
- **온도**: 일일 변화 패턴 (20~30°C)
- **일사량**: 주간 6-18시 (0~800 W/m²)
- **풍속**: 랜덤 + 계절성 (0~10 m/s)
- **재실 인원**: 수업 시간 기반 (50~600명)

## 🔄 향후 개선 사항

1. **WebSocket 스트리밍**: 실시간 데이터 스트림
2. **시나리오 시뮬레이션**: 다양한 시나리오 테스트
3. **과거 데이터 조회**: 시뮬레이션 히스토리
4. **알림 기능**: 성능 지표 임계값 초과 시 알림
5. **다중 자산 동시 모니터링**: 여러 자산 동시 추적

## 📌 참고 사항

- 시뮬레이션은 2초 간격으로 자동 실행됩니다
- 최근 100개 사이클 데이터만 메모리에 유지됩니다
- 실제 IoT 센서 데이터 연동 시 더 정확한 시뮬레이션 가능
- SmartGridDigitalTwin 모듈이 필요합니다 (numpy, pandas)

## 🎯 사용 시나리오

### 1. 기본 모니터링
1. 자산 카드의 "디지털 트윈" 버튼 클릭
2. 현재 상태 확인
3. "시뮬레이션 시작" 버튼 클릭
4. 실시간 데이터 확인

### 2. 성능 분석
1. 시뮬레이션 실행
2. 성능 지표 차트 확인
3. 재생에너지 비율, 안정성 점수 확인
4. 최적화 포인트 식별

### 3. 제어 알고리즘 평가
1. 다른 알고리즘 적용
2. 성능 비교
3. 최적 알고리즘 선택




