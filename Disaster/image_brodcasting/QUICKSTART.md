# 🚀 빠른 시작 가이드

## ⚡ 5분 만에 시작하기

### 1단계: 시스템 실행
```bash
cd safety_monitoring_system
./start.sh
```

또는 수동 실행:
```bash
cd backend
pip install -r requirements.txt --break-system-packages
python app.py
```

### 2단계: 대시보드 접속
웹 브라우저에서 `frontend/dashboard.html` 파일을 엽니다.

### 3단계: 모니터링 시작
1. "모니터링 시작" 버튼 클릭
2. 실시간 데이터가 자동으로 수집됩니다
3. 위험 상황 발생 시 자동 경보

---

## 📊 주요 기능

### 실시간 모니터링
- 5개 카메라 동시 감시
- 화재, 연기, 이상행동 자동 감지
- 3초 이내 즉시 알림

### 보고서 생성
- 일일/주간/월간 자동 생성
- 통계 분석 및 권장사항

### AI 질의응답
- "화재 사고 통계" 등 자연어 질문
- 실시간 답변 제공

---

## 🧪 테스트

```bash
# API 테스트
python test_system.py

# 데모 데이터 생성
python generate_demo_data.py
```

---

## 📞 도움말

- 상세 문서: `README.md`
- 시스템 개요: `SYSTEM_OVERVIEW.md`

**이제 "모니터링 시작"을 클릭하세요!** 🎉
