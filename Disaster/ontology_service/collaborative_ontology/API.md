# 📚 API 참조 문서

## Base URL

```
http://localhost:8000/api/v1
```

## 인증

모든 보호된 엔드포인트는 JWT Bearer 토큰이 필요합니다.

```http
Authorization: Bearer <access_token>
```

---

## 🔐 인증 (Auth)

### POST /auth/register
새 사용자 등록

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "full_name": "홍길동",
  "organization": "GnG International",
  "department": "R&D"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "full_name": "홍길동"
  }
}
```

### POST /auth/login
로그인

**Request Body (Form Data):**
```
username: user@example.com
password: password123
```

**Response:** 동일 (register와 같음)

### GET /auth/me
현재 사용자 정보 조회

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "홍길동",
  "roles": ["domain_expert"],
  "organization": "GnG International",
  "department": "R&D",
  "is_active": true,
  "created_at": "2025-01-01T00:00:00Z"
}
```

### POST /auth/logout
로그아웃

---

## 🌳 온톨로지 (Ontology)

### GET /ontology/classes
온톨로지 클래스 목록 조회

**Query Parameters:**
- `skip`: 건너뛸 항목 수 (기본: 0)
- `limit`: 가져올 항목 수 (기본: 100)
- `namespace`: 네임스페이스 필터
- `status`: 상태 필터 (draft, active, deprecated, archived)
- `search`: 검색어

**Response:**
```json
{
  "total": 10,
  "items": [
    {
      "id": 1,
      "name": "SolarPanel",
      "display_name": "태양광 패널",
      "description": "태양 에너지를 전기로 변환하는 장치",
      "namespace": "energy",
      "parent_id": null,
      "status": "active",
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### GET /ontology/classes/{class_id}
온톨로지 클래스 상세 조회

**Response:**
```json
{
  "id": 1,
  "name": "SolarPanel",
  "display_name": "태양광 패널",
  "description": "태양 에너지를 전기로 변환하는 장치",
  "namespace": "energy",
  "uri": "urn:energy:SolarPanel",
  "version": "1.0.0",
  "status": "active",
  "parent_id": null,
  "metadata": {},
  "tags": ["renewable", "solar"],
  "properties": [
    {
      "id": 1,
      "name": "capacity",
      "display_name": "용량",
      "data_type": "float",
      "unit": "kW",
      "is_required": true
    }
  ],
  "relationships": [
    {
      "id": 1,
      "name": "produces",
      "display_name": "생산하다",
      "target_class_id": 2,
      "relationship_type": "produces"
    }
  ],
  "created_by": 1,
  "updated_by": 1,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### POST /ontology/classes
온톨로지 클래스 생성 (편집자 권한 필요)

**Request Body:**
```json
{
  "name": "SolarPanel",
  "display_name": "태양광 패널",
  "description": "태양 에너지를 전기로 변환하는 장치",
  "parent_id": null,
  "namespace": "energy",
  "metadata": {},
  "tags": ["renewable", "solar"]
}
```

**Response:**
```json
{
  "id": 1,
  "message": "클래스가 생성되었습니다"
}
```

### PUT /ontology/classes/{class_id}
온톨로지 클래스 수정 (편집자 권한 필요)

**Request Body:**
```json
{
  "display_name": "태양광 발전 패널",
  "description": "업데이트된 설명",
  "status": "active"
}
```

### DELETE /ontology/classes/{class_id}
온톨로지 클래스 삭제 (편집자 권한 필요)

### POST /ontology/classes/{class_id}/properties
속성 추가 (편집자 권한 필요)

**Request Body:**
```json
{
  "name": "efficiency",
  "display_name": "효율",
  "description": "에너지 변환 효율",
  "data_type": "float",
  "unit": "%",
  "is_required": false,
  "default_value": null,
  "constraints": {
    "min": 0,
    "max": 100
  }
}
```

### POST /ontology/classes/{class_id}/relationships
관계 추가 (편집자 권한 필요)

**Request Body:**
```json
{
  "name": "produces",
  "display_name": "생산하다",
  "description": "에너지를 생산하는 관계",
  "target_class_id": 2,
  "relationship_type": "produces",
  "cardinality": "one-to-many",
  "is_bidirectional": false,
  "inverse_name": null
}
```

---

## 🤝 협업 (Proposals)

### GET /proposals
제안 목록 조회

**Query Parameters:**
- `skip`, `limit`: 페이지네이션
- `status`: 상태 필터 (draft, submitted, under_review, approved, rejected)
- `proposal_type`: 타입 필터 (create, update, delete, merge)
- `author_id`: 작성자 ID 필터
- `assigned_to`: 담당자 ID 필터

**Response:**
```json
{
  "total": 50,
  "items": [
    {
      "id": 1,
      "title": "새로운 배터리 클래스 추가",
      "description": "리튬 이온 배터리 클래스 추가 제안",
      "proposal_type": "create",
      "entity_type": "class",
      "status": "under_review",
      "priority": "medium",
      "category": "new_feature",
      "author_id": 2,
      "current_approvals": 1,
      "required_approvals": 2,
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### GET /proposals/{proposal_id}
제안 상세 조회

**Response:**
```json
{
  "id": 1,
  "title": "새로운 배터리 클래스 추가",
  "description": "상세 설명...",
  "proposal_type": "create",
  "entity_type": "class",
  "entity_id": null,
  "proposed_changes": {
    "name": "LithiumBattery",
    "display_name": "리튬 이온 배터리"
  },
  "current_state": null,
  "status": "under_review",
  "priority": "medium",
  "category": "new_feature",
  "tags": ["battery", "energy-storage"],
  "rationale": "리튬 배터리는 중요한 에너지 저장 장치입니다",
  "impact_analysis": "기존 배터리 클래스와 호환됩니다",
  "affected_entities": [],
  "required_approvals": 2,
  "current_approvals": 1,
  "author_id": 2,
  "author_name": "도메인 전문가",
  "assigned_to": null,
  "deadline": null,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "submitted_at": "2025-01-01T01:00:00Z",
  "resolved_at": null,
  "reviews": [
    {
      "id": 1,
      "reviewer_id": 3,
      "reviewer_name": "온톨로지 편집자",
      "decision": "approve",
      "comment": "좋은 제안입니다",
      "created_at": "2025-01-01T02:00:00Z"
    }
  ],
  "comments": [
    {
      "id": 1,
      "author_id": 2,
      "author_name": "도메인 전문가",
      "content": "추가 정보입니다",
      "parent_id": null,
      "created_at": "2025-01-01T01:30:00Z"
    }
  ]
}
```

### POST /proposals
제안 생성

**Request Body:**
```json
{
  "title": "새로운 배터리 클래스 추가",
  "description": "리튬 이온 배터리 클래스 추가 제안",
  "proposal_type": "create",
  "entity_type": "class",
  "entity_id": null,
  "proposed_changes": {
    "name": "LithiumBattery",
    "display_name": "리튬 이온 배터리",
    "description": "리튬 이온 배터리 저장 장치"
  },
  "rationale": "필요성 설명",
  "impact_analysis": "영향 분석",
  "priority": "medium",
  "category": "new_feature",
  "tags": ["battery"]
}
```

### PUT /proposals/{proposal_id}
제안 수정

### POST /proposals/{proposal_id}/submit
제안 제출 (draft → submitted)

### POST /proposals/{proposal_id}/reviews
리뷰 작성 (리뷰어 권한 필요)

**Request Body:**
```json
{
  "decision": "approve",
  "comment": "잘 작성된 제안입니다",
  "feedback": {
    "completeness": 5,
    "clarity": 5,
    "impact": 4
  },
  "conditions": null
}
```

### POST /proposals/{proposal_id}/comments
댓글 작성

**Request Body:**
```json
{
  "content": "좋은 제안입니다!",
  "parent_id": null,
  "mentions": [3, 4]
}
```

### GET /proposals/{proposal_id}/comments
제안의 댓글 목록 조회

### GET /proposals/stats/summary
제안 통계

**Response:**
```json
{
  "total": 50,
  "by_status": {
    "draft": 10,
    "submitted": 5,
    "under_review": 15,
    "approved": 15,
    "rejected": 5
  },
  "my_proposals": 8,
  "my_pending_reviews": 3
}
```

---

## 📊 데이터 타입

### ProposalType
- `create`: 새 엔티티 생성
- `update`: 기존 엔티티 수정
- `delete`: 엔티티 삭제
- `merge`: 엔티티 병합

### ProposalStatus
- `draft`: 초안
- `submitted`: 제출됨
- `under_review`: 리뷰 중
- `approved`: 승인됨
- `rejected`: 거부됨
- `implemented`: 구현됨
- `withdrawn`: 철회됨

### ReviewDecision
- `approve`: 승인
- `reject`: 거부
- `request_changes`: 수정 요청
- `abstain`: 기권

### UserRole
- `admin`: 관리자
- `ontology_editor`: 온톨로지 편집자
- `domain_expert`: 도메인 전문가
- `energy_provider`: 에너지 공급자
- `device_operator`: 기기 운영자
- `viewer`: 뷰어

### OntologyStatus
- `draft`: 초안
- `active`: 활성
- `deprecated`: 사용 중단
- `archived`: 보관

---

## ⚠️ 에러 코드

### 400 Bad Request
잘못된 요청

```json
{
  "detail": "이미 등록된 이메일입니다"
}
```

### 401 Unauthorized
인증 실패

```json
{
  "detail": "인증 정보를 검증할 수 없습니다"
}
```

### 403 Forbidden
권한 없음

```json
{
  "detail": "이 작업을 수행할 권한이 없습니다"
}
```

### 404 Not Found
리소스를 찾을 수 없음

```json
{
  "detail": "클래스를 찾을 수 없습니다"
}
```

### 500 Internal Server Error
서버 오류

```json
{
  "detail": "내부 서버 오류가 발생했습니다"
}
```

---

## 📝 사용 예제

### Python 예제

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 로그인
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={
        "username": "admin@gnginternational.com",
        "password": "changeme123"
    }
)
token = response.json()["access_token"]

# 헤더 설정
headers = {"Authorization": f"Bearer {token}"}

# 온톨로지 클래스 조회
response = requests.get(
    f"{BASE_URL}/ontology/classes",
    headers=headers
)
classes = response.json()

# 제안 생성
response = requests.post(
    f"{BASE_URL}/proposals",
    headers=headers,
    json={
        "title": "새로운 클래스 추가",
        "description": "상세 설명",
        "proposal_type": "create",
        "entity_type": "class",
        "proposed_changes": {...}
    }
)
```

### JavaScript 예제

```javascript
const BASE_URL = "http://localhost:8000/api/v1";

// 로그인
const loginResponse = await fetch(`${BASE_URL}/auth/login`, {
  method: "POST",
  headers: {
    "Content-Type": "application/x-www-form-urlencoded",
  },
  body: new URLSearchParams({
    username: "admin@gnginternational.com",
    password: "changeme123",
  }),
});

const { access_token } = await loginResponse.json();

// 온톨로지 클래스 조회
const classesResponse = await fetch(`${BASE_URL}/ontology/classes`, {
  headers: {
    Authorization: `Bearer ${access_token}`,
  },
});

const classes = await classesResponse.json();

// 제안 생성
const proposalResponse = await fetch(`${BASE_URL}/proposals`, {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${access_token}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    title: "새로운 클래스 추가",
    description: "상세 설명",
    proposal_type: "create",
    entity_type: "class",
    proposed_changes: {...},
  }),
});
```
