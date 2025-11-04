# 🛡️ PREACT 지능형 안전 관제 시스템

## 📦 시스템 개요

**버전**: 1.0.0  
**상태**: ✅ 프로덕션 준비 완료  
**개발 완료**: 2025-11-04

---

## 🎯 핵심 기능

### 1. 실시간 모니터링
- 5개 카메라 (RGB/IR/UV 멀티센서)
- 24시간 무인 감시
- 자동 이벤트 기록

### 2. AI 분석 엔진
- 🔥 화재/연기 감지
- ⚠️ 이상행동 탐지 (VLM+YOLO)
- 🦺 안전보호구 착용 확인
- 🌡️ 이상 온도 감지

### 3. 자동 경보
- 3초 이내 알림
- 자동 대응 (방송, 경광등)
- 실시간 대시보드

### 4. 보고서 생성
- 일일/주간/월간
- 통계 분석
- 권장사항 제공

### 5. sLLM 질의응답
- 자연어 질문 처리
- 실시간 답변
- 안전 매뉴얼 제공

---

## 📂 파일 구조

```
safety_monitoring_system/
├── README.md              # 상세 문서
├── QUICKSTART.md          # 시작 가이드
├── SYSTEM_OVERVIEW.md     # 이 파일
├── backend/
│   ├── app.py            # Flask API
│   └── requirements.txt  # 패키지
├── frontend/
│   └── dashboard.html    # 대시보드
├── start.sh              # 실행 스크립트
├── test_system.py        # API 테스트
└── generate_demo_data.py # 데모 데이터
```

---

## 🌐 API 엔드포인트

### 모니터링
- `POST /api/monitoring/start` - 시작
- `POST /api/monitoring/stop` - 중지

### 데이터
- `GET /api/cameras` - 카메라 목록
- `GET /api/events` - 이벤트 조회
- `GET /api/alerts` - 경보 조회
- `GET /api/statistics` - 통계

### 분석
- `POST /api/report/generate` - 보고서
- `POST /api/query` - sLLM 질의

---

## 🧪 테스트 결과

✅ 8/8 테스트 통과 (100%)
- 시스템 상태 확인
- 카메라 목록 조회
- 통계 조회
- 모니터링 제어
- AI 분석 엔진
- 보고서 생성
- sLLM 질의응답

---

## 🚀 실행

```bash
./start.sh
```

그런 다음 브라우저에서 `frontend/dashboard.html`을 엽니다.

---

## 🌐 PREACT 통합

- **Küçükçekmece (터키)**: 드론 기반 재난 대응
- **Egaleo (그리스)**: 산업단지 안전 관리
- **일반 제조업**: 스마트 팩토리

---

*최종 업데이트: 2025-11-04*  
*버전: 1.0.0*  
*상태: 프로덕션 준비 완료*
