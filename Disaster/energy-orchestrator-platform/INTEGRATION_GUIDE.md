# Demand Analysis 통합 가이드

## ✅ 통합 완료 사항

demand_analysis 서비스를 메인 애플리케이션에 성공적으로 통합했습니다.

## 🎯 주요 기능

### 1. 자산 관리 페이지 개선
- **자산 추가 기능**: "+ 자산 추가" 버튼으로 새 자산 추가
- **카드 형태 표시**: 자산을 카드 형태로 표시
- **서비스 연결**: 자산 타입에 따라 demand 또는 supply 분석 서비스와 연결

### 2. 서비스 카드
- **에너지 수요 분석 대시보드**: demand 타입 자산에 대한 카드
- **에너지 공급 분석 대시보드**: supply 타입 자산에 대한 카드
- **"열기" 버튼**: 카드 클릭 시 해당 서비스 페이지로 이동

### 3. Demand Analysis 페이지
- 자산별 수요 분석 결과 표시
- 데이터 품질 점수
- 이상 탐지 결과
- 에너지 통계
- 7일 예측

## 📁 추가된 파일

### Backend
- `backend/src/services/demand_analysis_service.py`: Demand 분석 서비스
- `backend/src/api/v1/demand.py`: Demand 분석 API 엔드포인트

### Frontend
- `frontend/src/components/AssetCard.tsx`: 자산 카드 컴포넌트
- `frontend/src/components/ServiceCard.tsx`: 서비스 카드 컴포넌트
- `frontend/src/components/AddAssetDialog.tsx`: 자산 추가 다이얼로그
- `frontend/src/pages/DemandAnalysis.tsx`: Demand 분석 페이지

## 🔄 사용 방법

### 1. 자산 추가
1. Assets 페이지로 이동
2. "+ 자산 추가" 버튼 클릭
3. 자산 정보 입력:
   - 이름: 자산 이름
   - 타입: solar, wind, battery, demand, grid 등
   - 용량: kW 단위
   - 위치: 위도, 경도 (선택사항)
4. "저장" 버튼 클릭

### 2. 서비스 카드 확인
- 자산 추가 후 자산 타입에 따라 서비스 카드가 자동 생성됩니다
- demand 타입: "에너지 수요 분석 대시보드" 카드
- supply 타입: "에너지 공급 분석 대시보드" 카드

### 3. 분석 서비스 접속
- 서비스 카드의 "열기" 버튼 클릭
- 또는 자산 카드의 "열기" 버튼 클릭
- Demand Analysis 페이지로 이동하여 분석 결과 확인

## 🛠️ API 엔드포인트

### Assets API
- `GET /api/v1/assets`: 자산 목록 조회
- `POST /api/v1/assets`: 자산 생성
- `GET /api/v1/assets/{asset_id}`: 자산 조회
- `DELETE /api/v1/assets/{asset_id}`: 자산 삭제

### Demand Analysis API
- `GET /api/v1/demand/analysis/{asset_id}`: 수요 분석 결과 조회
- `POST /api/v1/demand/analysis/{asset_id}/analyze`: 수요 분석 실행
- `GET /api/v1/demand/dashboard/{asset_id}`: 대시보드 데이터 조회

## 📊 데이터 구조

### Asset
```typescript
{
  id: string
  name: string
  type: 'solar' | 'wind' | 'battery' | 'demand' | 'grid'
  capacity_kw: number
  location?: { lat: number, lon: number }
  status: 'online' | 'offline' | 'maintenance'
  service_type: 'demand' | 'supply'
  created_at: string
}
```

### Demand Analysis Result
```typescript
{
  asset_id: string
  quality_report: {
    quality_score: number
    total_records: number
    missing_values: object
    duplicates: number
  }
  statistics: {
    total_energy: number
    peak_demand: number
    average_consumption: number
  }
  anomalies: {
    count: number
    percentage: number
    anomalies: array
  }
  predictions: {
    forecast_days: number
    predictions: array
  }
}
```

## 🎨 UI 구성

### Assets 페이지
1. **헤더**: 제목 + 자산 추가 버튼
2. **통계 카드**: 총 자산, 운영 중, 총 용량, 평균 용량
3. **서비스 대시보드 카드**: demand/supply 분석 대시보드
4. **자산 목록**: 개별 자산 카드

### Demand Analysis 페이지
1. **데이터 품질 점수**: 0-100 점
2. **이상 탐지**: 이상 개수 및 비율
3. **통계**: 총 에너지, 피크 수요, 평균 소비
4. **7일 예측**: 일별 예측 값

## 🔧 향후 개선 사항

1. **실제 데이터 연동**: CSV 파일 업로드 및 분석
2. **차트 시각화**: Plotly를 사용한 인터랙티브 차트
3. **실시간 업데이트**: WebSocket을 통한 실시간 데이터 업데이트
4. **공급 분석**: Supply 분석 서비스 통합
5. **데이터베이스 통합**: PostgreSQL에 실제 데이터 저장

## 📝 참고 사항

- 현재는 임시 저장소(메모리)를 사용합니다
- 실제 프로덕션 환경에서는 데이터베이스에 저장해야 합니다
- Demand Analysis 서비스는 scikit-learn이 필요합니다
- CSV 파일 업로드 기능은 향후 구현 예정입니다




