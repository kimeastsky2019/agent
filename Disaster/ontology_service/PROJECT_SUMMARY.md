# 온톨로지 구축 서비스 - 프로젝트 요약

## 📋 개요
시계열 데이터와 이미지 데이터를 기반으로 온톨로지를 자동으로 생성하고 관리할 수 있는 완전한 웹 서비스입니다.

## 🎯 핵심 기능

### 1. 데이터 처리
- ✅ 시계열 데이터 (CSV, JSON, Excel)
  - 자동 통계 분석
  - 시간 범위 감지
  - 패턴 및 이상치 감지

- ✅ 이미지 데이터 (JPG, PNG, GIF 등)
  - 메타데이터 자동 추출
  - 색상 분석
  - EXIF 데이터 처리

### 2. 온톨로지 관리
- ✅ RDFLib 기반 OWL 온톨로지 생성
- ✅ SPARQL 쿼리 지원
- ✅ 온톨로지 시각화
- ✅ OWL/XML 형식 내보내기

### 3. 웹 인터페이스
- ✅ React 기반 직관적인 UI
- ✅ 파일 업로드 및 실시간 분석
- ✅ 대화형 쿼리 인터페이스
- ✅ 그래프 시각화

## 📁 파일 구조

```
ontology_service/
├── 📄 app.py                   # Flask 백엔드 서버
├── 📄 ontology_builder.py      # 온톨로지 생성/관리 엔진
├── 📄 data_processor.py        # 데이터 분석 모듈
├── 📄 frontend.html            # React 웹 인터페이스
├── 📄 test_api.py              # API 테스트 스크립트
├── 📄 requirements.txt         # Python 패키지 의존성
├── 📄 README.md               # 기본 사용 가이드
├── 📄 ADVANCED_GUIDE.md       # 고급 사용 가이드
├── 📄 Dockerfile              # Docker 설정
├── 📄 docker-compose.yml      # Docker Compose 설정
├── 📄 quick_start.sh          # Linux/Mac 빠른 시작
├── 📄 quick_start.bat         # Windows 빠른 시작
├── 📁 example_data/           # 예제 데이터
│   └── sample_timeseries.csv
└── 📁 .gitignore              # Git 무시 파일
```

## 🚀 빠른 시작

### 방법 1: 자동 설치 스크립트

**Linux/Mac:**
```bash
chmod +x quick_start.sh
./quick_start.sh
python app.py
```

**Windows:**
```cmd
quick_start.bat
python app.py
```

### 방법 2: 수동 설치

```bash
# 1. 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 서버 실행
python app.py
```

### 방법 3: Docker

```bash
docker-compose up -d
```

## 🔌 API 엔드포인트

| 엔드포인트 | 메서드 | 설명 |
|----------|--------|------|
| `/api/health` | GET | 서버 상태 확인 |
| `/api/upload/timeseries` | POST | 시계열 데이터 업로드 |
| `/api/upload/image` | POST | 이미지 업로드 |
| `/api/ontology/create` | POST | 온톨로지 생성 |
| `/api/ontology/add_timeseries` | POST | 시계열 데이터 추가 |
| `/api/ontology/add_image` | POST | 이미지 데이터 추가 |
| `/api/ontology/query` | POST | SPARQL 쿼리 실행 |
| `/api/ontology/list` | GET | 온톨로지 목록 |
| `/api/ontology/visualize/<name>` | GET | 그래프 시각화 |
| `/api/ontology/export/<name>` | GET | 온톨로지 다운로드 |

## 💡 사용 예제

### 1. 시계열 데이터 업로드
```python
import requests

with open('data.csv', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:5000/api/upload/timeseries',
        files=files
    )
    print(response.json())
```

### 2. 온톨로지 생성
```python
response = requests.post(
    'http://localhost:5000/api/ontology/create',
    json={'name': 'my_ontology'}
)
```

### 3. SPARQL 쿼리
```python
query = "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10"
response = requests.post(
    'http://localhost:5000/api/ontology/query',
    json={
        'ontology_name': 'my_ontology',
        'query': query
    }
)
```

## 🛠️ 기술 스택

- **백엔드**: Python 3.10+, Flask, Flask-CORS
- **온톨로지**: RDFLib 7.0, OWL
- **데이터 처리**: Pandas, NumPy, Pillow
- **프론트엔드**: React 18, TailwindCSS
- **컨테이너**: Docker, Docker Compose

## 📊 온톨로지 구조

### 핵심 클래스
```
owl:Thing
├── ts:TimeSeries (시계열)
│   └── ts:DataPoint (데이터 포인트)
└── img:Image (이미지)
    └── img:ImageMetadata (메타데이터)
```

### 주요 프로퍼티
- `ts:hasTimestamp` - 타임스탬프
- `ts:hasValue` - 값
- `ts:hasDataPoint` - 데이터 포인트 관계
- `img:hasWidth` - 너비
- `img:hasHeight` - 높이
- `img:hasFormat` - 형식

## 🎓 학습 자료

1. **README.md** - 기본 사용법 및 설치
2. **ADVANCED_GUIDE.md** - 고급 SPARQL 쿼리 및 Python 예제
3. **test_api.py** - 실제 동작하는 API 사용 예제

## 🔧 확장 아이디어

### 단기 (쉬움)
- [ ] 더 많은 파일 형식 지원 (XML, Parquet 등)
- [ ] 데이터 검증 및 오류 처리 강화
- [ ] 사용자 인증 및 권한 관리
- [ ] 온톨로지 템플릿 시스템

### 중기 (보통)
- [ ] 그래프 데이터베이스 통합 (Neo4j, RDF4J)
- [ ] 실시간 데이터 스트리밍 지원
- [ ] 고급 시각화 (D3.js, Cytoscape.js)
- [ ] 머신러닝 기반 자동 분류

### 장기 (어려움)
- [ ] OWL 추론 엔진 (Pellet, HermiT)
- [ ] 분산 온톨로지 관리
- [ ] 자연어 쿼리 인터페이스
- [ ] 온톨로지 버전 관리 시스템

## 📝 테스트

API 테스트:
```bash
python test_api.py
```

이 스크립트는 다음을 수행합니다:
1. 서버 헬스 체크
2. 샘플 데이터 업로드
3. 온톨로지 생성
4. 데이터 추가
5. SPARQL 쿼리 실행
6. 결과 시각화

## 🐛 문제 해결

### 포트 충돌
```bash
# 다른 포트로 실행
python app.py --port 5001
```

### CORS 오류
Flask-CORS가 설정되어 있지만, 문제가 있다면:
```python
# app.py에서
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

### 대용량 파일
```python
# app.py에 추가
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
```

## 📄 라이선스
MIT License - 자유롭게 사용, 수정, 배포 가능

## 🤝 기여
이슈 제보 및 풀 리퀘스트 환영!

---

**버전**: 1.0.0  
**최종 업데이트**: 2025-11-04  
**제작자**: Claude (Anthropic)
