# Supply Analysis 통합 가이드

## ✅ 통합 완료 사항

supply_analysis 서비스를 메인 애플리케이션에 성공적으로 통합했습니다.

## 🎯 주요 기능

### 1. 에너지 공급 분석 서비스
- **실시간 전력 데이터**: 시간별/일별 전력 생산 데이터
- **생산량 예측**: 7일 생산량 예측
- **이상 탐지**: Isolation Forest 기반 이상 패턴 탐지
- **시설 정보**: 시설 상태 및 효율 정보

### 2. Supply Analysis 페이지
- **실시간 전력 그래프**: Line Chart로 시간별 전력 표시
- **생산량 예측**: Bar Chart로 7일 예측 표시
- **이상 탐지 결과**: 이상 패턴 목록
- **시설 정보 카드**: 현재 전력, 효율, 상태 등

### 3. 자산 관리 페이지 연동
- **supply 타입 자산**: 자동으로 공급 분석 대시보드 카드 생성
- **서비스 연결**: 카드 클릭 시 Supply Analysis 페이지로 이동

## 📁 추가된 파일

### Backend
- `backend/src/services/supply_analysis_service.py`: 공급 분석 서비스
- `backend/src/api/v1/supply.py`: 공급 분석 API 엔드포인트

### Frontend
- `frontend/src/pages/SupplyAnalysis.tsx`: 공급 분석 페이지
- Supply Analysis API 함수들 (`frontend/src/services/api.ts`)

## 🔄 사용 방법

### 1. 자산 추가
1. Assets 페이지로 이동
2. "+ 자산 추가" 버튼 클릭
3. 자산 타입 선택:
   - `solar`, `wind`, `battery`, `grid` → `supply` 서비스 연결
   - `demand` → `demand` 서비스 연결
4. 저장 후 서비스 카드 자동 생성

### 2. 공급 분석 서비스 접속
- **서비스 카드**: "에너지 공급 분석 대시보드" 카드의 "열기" 버튼 클릭
- **자산 카드**: 자산 카드의 "열기" 버튼 클릭
- Supply Analysis 페이지로 이동하여 분석 결과 확인

## 🛠️ API 엔드포인트

### Supply Analysis API
- `GET /api/v1/supply/analysis/{asset_id}`: 공급 분석 결과 조회
- `GET /api/v1/supply/realtime/{asset_id}`: 실시간 전력 데이터 조회
- `GET /api/v1/supply/forecast/{asset_id}`: 생산량 예측 조회
- `GET /api/v1/supply/anomalies/{asset_id}`: 이상 탐지 결과 조회
- `GET /api/v1/supply/facility/{asset_id}`: 시설 정보 조회
- `GET /api/v1/supply/dashboard/{asset_id}`: 대시보드 데이터 조회

## 📊 데이터 구조

### Supply Analysis Result
```typescript
{
  asset_id: string
  realtime_data: {
    labels: string[]
    values: number[]
    range_type: string
    timestamp: string
  }
  forecast: {
    forecast_days: number
    predictions: Array<{
      date: string
      day_of_week: string
      predicted_production: number
      confidence_lower: number
      confidence_upper: number
      confidence_level: number
      weather_factor: number
    }>
  }
  anomalies: {
    count: number
    anomalies: Array<{
      timestamp: string
      value: number
      score: number
      severity: string
    }>
  }
  facility: {
    id: string
    name: string
    type: string
    capacity: number
    current_power: number
    efficiency: number
    status: string
  }
  statistics: {
    total_production: number
    average_power: number
    peak_power: number
    efficiency: number
  }
}
```

## 🎨 UI 구성

### Supply Analysis 페이지
1. **통계 카드**: 현재 전력, 효율, 평균 전력, 이상 탐지
2. **실시간 전력 그래프**: Line Chart로 시간별 전력 표시
3. **시설 정보 카드**: 이름, 타입, 상태, 용량
4. **생산량 예측**: Bar Chart로 7일 예측 표시
5. **이상 탐지 결과**: 이상 패턴 목록

## 🔧 주요 기능 상세

### 1. 실시간 전력 데이터
- **시간 범위**: hour (24시간), day (7일)
- **차트**: Line Chart (Recharts)
- **자동 갱신**: 30초마다 데이터 갱신

### 2. 생산량 예측
- **예측 기간**: 7일 (기본값)
- **차트**: Bar Chart로 예측값 표시
- **신뢰 구간**: 상한/하한 표시

### 3. 이상 탐지
- **알고리즘**: Isolation Forest
- **탐지율**: 5% contamination
- **결과 표시**: 타임스탬프, 값, 심각도

### 4. 시설 정보
- **현재 전력**: 실시간 전력 생산량
- **효율**: 시설 효율 (80-95%)
- **상태**: online/offline/maintenance

## 📝 Demand vs Supply 비교

### Demand Analysis
- **용도**: 에너지 수요 분석
- **주요 기능**: 수요 예측, 이상 탐지, 데이터 품질 검증
- **카드 색상**: 보라색 그라데이션 (#667eea → #764ba2)

### Supply Analysis
- **용도**: 에너지 공급 분석
- **주요 기능**: 생산량 예측, 이상 탐지, 실시간 모니터링
- **카드 색상**: 주황색 그라데이션 (#ff9800 → #f57c00)

## 🔄 향후 개선 사항

1. **실제 데이터 연동**: IoT 센서 데이터 연동
2. **차트 개선**: 더 많은 시각화 옵션
3. **실시간 업데이트**: WebSocket을 통한 실시간 데이터 업데이트
4. **고장 진단**: 설비 고장 예측 및 진단 기능
5. **날씨 연동**: 날씨 데이터와 생산량 상관관계 분석

## 📌 참고 사항

- 현재는 샘플 데이터를 사용합니다
- 실제 프로덕션 환경에서는 IoT 센서 데이터를 연동해야 합니다
- Supply Analysis 서비스는 scikit-learn이 필요합니다
- 실시간 데이터는 30초마다 자동 갱신됩니다




