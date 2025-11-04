# 온톨로지 구축 서비스

시계열 데이터와 이미지 데이터를 기반으로 온톨로지를 생성하고 관리할 수 있는 웹 서비스입니다.

## 주요 기능

### 1. 데이터 업로드 및 분석
- **시계열 데이터**: CSV, JSON, Excel 파일 지원
  - 기본 통계 분석
  - 시간 범위 및 빈도 감지
  - 추세 및 이상치 감지
  
- **이미지 데이터**: JPG, PNG, GIF 등 지원
  - 메타데이터 추출 (크기, 형식, 색상 분석)
  - EXIF 데이터 추출
  - 색상 히스토그램 분석

### 2. 온톨로지 생성 및 관리
- RDFLib 기반 OWL 온톨로지 생성
- 시계열 및 이미지 데이터를 온톨로지 개념으로 매핑
- 온톨로지 내보내기 (OWL/XML 형식)

### 3. SPARQL 쿼리
- 표준 SPARQL 쿼리 실행
- 온톨로지 데이터 검색 및 추론

### 4. 시각화
- 온톨로지 그래프 구조 시각화
- 노드 및 엣지 관계 표시

## 설치 방법

### 1. 필수 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 서버 실행

```bash
python app.py
```

서버가 http://localhost:5000 에서 실행됩니다.

### 3. 웹 인터페이스 접속

브라우저에서 `frontend.html` 파일을 열거나, 웹 서버를 통해 접속하세요.

```bash
# 간단한 웹 서버 실행 (옵션)
python -m http.server 8080
```

그 다음 http://localhost:8080/frontend.html 에 접속합니다.

## 사용 방법

### 1. 데이터 업로드

**시계열 데이터 예시 (CSV)**:
```csv
timestamp,temperature,humidity
2024-01-01 00:00:00,23.5,65.2
2024-01-01 01:00:00,23.3,66.1
2024-01-01 02:00:00,23.1,67.0
```

**이미지 데이터**:
- JPG, PNG 등의 이미지 파일 업로드
- 자동으로 메타데이터 추출

### 2. 온톨로지 생성

1. "온톨로지 생성" 탭으로 이동
2. 온톨로지 이름 입력
3. "온톨로지 생성" 버튼 클릭

### 3. 데이터를 온톨로지에 추가

API를 통해 업로드된 데이터를 온톨로지에 추가할 수 있습니다:

```python
import requests

# 시계열 데이터 추가
response = requests.post('http://localhost:5000/api/ontology/add_timeseries', json={
    'ontology_name': 'my_ontology',
    'filepath': 'uploads/ts_1234567890_data.csv',
    'concept_name': 'TemperatureSensor'
})

# 이미지 데이터 추가
response = requests.post('http://localhost:5000/api/ontology/add_image', json={
    'ontology_name': 'my_ontology',
    'filepath': 'uploads/img_1234567890_photo.jpg',
    'concept_name': 'ProductImage'
})
```

### 4. SPARQL 쿼리 실행

기본 쿼리 예시:

```sparql
# 모든 트리플 조회
SELECT ?s ?p ?o 
WHERE { 
    ?s ?p ?o 
} 
LIMIT 10

# 시계열 데이터 조회
PREFIX ts: <http://example.org/ontology/timeseries/>
SELECT ?timeseries ?datapoint ?value
WHERE {
    ?timeseries a ts:TimeSeries .
    ?timeseries ts:hasDataPoint ?datapoint .
    ?datapoint ts:hasValue ?value .
}

# 이미지 메타데이터 조회
PREFIX img: <http://example.org/ontology/image/>
SELECT ?image ?width ?height
WHERE {
    ?image a img:Image .
    ?image img:hasWidth ?width .
    ?image img:hasHeight ?height .
}
```

## API 엔드포인트

### 데이터 업로드
- `POST /api/upload/timeseries` - 시계열 데이터 업로드
- `POST /api/upload/image` - 이미지 데이터 업로드

### 온톨로지 관리
- `POST /api/ontology/create` - 새 온톨로지 생성
- `POST /api/ontology/add_timeseries` - 시계열 데이터 추가
- `POST /api/ontology/add_image` - 이미지 데이터 추가
- `GET /api/ontology/list` - 온톨로지 목록 조회
- `GET /api/ontology/export/<name>` - 온톨로지 내보내기

### 쿼리 및 시각화
- `POST /api/ontology/query` - SPARQL 쿼리 실행
- `GET /api/ontology/visualize/<name>` - 온톨로지 시각화 데이터

## 프로젝트 구조

```
ontology_service/
├── app.py                  # Flask 메인 애플리케이션
├── ontology_builder.py     # 온톨로지 생성 및 관리
├── data_processor.py       # 데이터 분석 및 처리
├── frontend.html           # 웹 인터페이스
├── requirements.txt        # Python 패키지 의존성
├── uploads/               # 업로드된 파일 저장
└── ontologies/            # 생성된 온톨로지 저장
```

## 온톨로지 구조

### 클래스 계층
- `TimeSeries`: 시계열 데이터
  - `DataPoint`: 개별 데이터 포인트
- `Image`: 이미지 데이터
  - `ImageMetadata`: 이미지 메타데이터

### 프로퍼티
- 시계열 관련:
  - `hasTimestamp`: 타임스탬프
  - `hasValue`: 값
  - `hasDataPoint`: 데이터 포인트 관계
  
- 이미지 관련:
  - `hasWidth`: 너비
  - `hasHeight`: 높이
  - `hasFormat`: 형식

## 확장 가능성

### 1. 더 많은 데이터 타입 지원
- 비디오 데이터
- 오디오 데이터
- 텍스트 문서

### 2. 고급 분석 기능
- 머신러닝 기반 특징 추출
- 시계열 예측
- 이미지 객체 감지 (YOLO, DETR 등)

### 3. 온톨로지 추론
- OWL 추론 엔진 통합 (Pellet, HermiT)
- 규칙 기반 추론

### 4. 협업 기능
- 다중 사용자 지원
- 버전 관리
- 온톨로지 병합

## 기술 스택

- **백엔드**: Flask, Python 3.8+
- **온톨로지**: RDFLib, OWL
- **데이터 처리**: Pandas, NumPy, Pillow
- **프론트엔드**: React, TailwindCSS

## 라이선스

MIT License

## 문제 해결

### CORS 오류
프론트엔드와 백엔드를 다른 포트에서 실행할 경우 CORS 오류가 발생할 수 있습니다. 
Flask-CORS가 이미 설정되어 있으므로 대부분의 경우 문제없이 작동합니다.

### 파일 업로드 크기 제한
큰 파일 업로드 시 Flask의 기본 크기 제한을 초과할 수 있습니다. 
`app.py`에서 다음 설정을 추가하세요:

```python
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
```

### 메모리 부족
대용량 데이터 처리 시 메모리 부족 문제가 발생할 수 있습니다. 
배치 처리나 스트리밍 방식을 고려하세요.

## 기여

이슈 제보 및 풀 리퀘스트를 환영합니다!
