# 🌐 Collaborative Energy Ontology Platform

Palantir 스타일의 협업형 에너지 온톨로지 플랫폼 - 모든 이해관계자가 함께 만드는 에너지 지식 시스템

## 🎯 주요 기능

### 1. 역할 기반 접근 제어 (RBAC)
- **관리자 (Admin)**: 전체 시스템 관리, 사용자 권한 부여
- **온톨로지 편집자 (Ontology Editor)**: 온톨로지 생성 및 수정
- **도메인 전문가 (Domain Expert)**: 변경 제안 및 리뷰
- **에너지 공급자 (Energy Provider)**: 공급 관련 데이터 기여
- **기기 운영자 (Device Operator)**: 기기 정보 관리
- **일반 사용자 (Viewer)**: 조회 권한

### 2. 협업 워크플로우
```
제안 생성 → 전문가 리뷰 → 토론 → 승인/거부 → 온톨로지 업데이트
```

### 3. 온톨로지 버전 관리
- Git 스타일 버전 관리
- 변경 히스토리 추적
- 롤백 기능
- 브랜치 및 병합

### 4. 실시간 협업
- WebSocket 기반 실시간 업데이트
- 동시 편집 감지
- 변경사항 실시간 알림
- 온라인 사용자 표시

### 5. 거버넌스 및 감사
- 모든 변경사항 로깅
- 승인 프로세스 추적
- 규정 준수 보고서
- 데이터 품질 검증

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │ Ontology │  │ Proposal │  │ Version  │  │  Admin  ││
│  │  Editor  │  │  System  │  │ History  │  │  Panel  ││
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘│
└─────────────────────────────────────────────────────────┘
                            │
                    REST API / WebSocket
                            │
┌─────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │   Auth   │  │Ontology  │  │Workflow  │  │  Audit  ││
│  │  & RBAC  │  │  Service │  │  Engine  │  │  Logger ││
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘│
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                Database (PostgreSQL)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │  Users   │  │Ontology  │  │Proposals │  │  Audit  ││
│  │  Roles   │  │ Entities │  │ Reviews  │  │  Logs   ││
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘│
└─────────────────────────────────────────────────────────┘
```

## 📁 프로젝트 구조

```
collaborative_ontology/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy 모델
│   │   ├── schemas/         # Pydantic 스키마
│   │   ├── services/        # 비즈니스 로직
│   │   ├── api/            # API 엔드포인트
│   │   ├── auth/           # 인증/인가
│   │   ├── websocket/      # 실시간 협업
│   │   └── main.py         # FastAPI 앱
│   ├── alembic/            # DB 마이그레이션
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # React 컴포넌트
│   │   ├── pages/          # 페이지
│   │   ├── services/       # API 서비스
│   │   └── store/          # 상태 관리
│   └── package.json
├── docker-compose.yml
└── README.md
```

## 🚀 시작하기

### 1. 환경 설정
```bash
# 저장소 클론
git clone <repository-url>
cd collaborative_ontology

# 환경 변수 설정
cp .env.example .env
```

### 2. Docker로 실행
```bash
docker-compose up -d
```

### 3. 개별 실행

#### 백엔드
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### 프론트엔드
```bash
cd frontend
npm install
npm start
```

## 📊 데이터 모델

### 온톨로지 엔티티
- **클래스 (Class)**: 에너지 개념 (예: 태양광 패널, 배터리)
- **속성 (Property)**: 클래스의 특성
- **관계 (Relationship)**: 클래스 간 연결
- **인스턴스 (Instance)**: 실제 데이터

### 협업 워크플로우
- **제안 (Proposal)**: 변경 제안서
- **리뷰 (Review)**: 전문가 검토
- **댓글 (Comment)**: 토론 내용
- **승인 (Approval)**: 최종 승인

## 🔒 보안 기능

- JWT 기반 인증
- 역할 기반 접근 제어
- API 요청 제한
- 감사 로그
- 데이터 암호화

## 🌍 다국어 지원

- 한국어 (기본)
- 영어
- UI 다국어 지원

## 📈 모니터링

- 사용자 활동 추적
- 시스템 성능 모니터링
- 온톨로지 품질 메트릭
- 협업 통계

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이선스

MIT License

## 👥 팀

GnG International - Energy Ontology Team

## 📞 연락처

- Email: support@gnginternational.com
- Website: https://gnginternational.com
