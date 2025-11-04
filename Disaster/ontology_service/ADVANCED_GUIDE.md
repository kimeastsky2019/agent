# 고급 사용 가이드

## SPARQL 쿼리 예제

### 1. 기본 쿼리

#### 모든 클래스 조회
```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?class ?label
WHERE {
    ?class a owl:Class .
    OPTIONAL { ?class rdfs:label ?label }
}
```

#### 모든 프로퍼티 조회
```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?property ?type ?label
WHERE {
    ?property a ?type .
    FILTER (?type = owl:ObjectProperty || ?type = owl:DatatypeProperty)
    OPTIONAL { ?property rdfs:label ?label }
}
```

### 2. 시계열 데이터 쿼리

#### 모든 시계열 조회
```sparql
PREFIX ts: <http://example.org/ontology/timeseries/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?timeseries ?label ?filepath
WHERE {
    ?timeseries a ts:TimeSeries .
    OPTIONAL { ?timeseries rdfs:label ?label }
    OPTIONAL { ?timeseries <http://example.org/ontology/hasFilePath> ?filepath }
}
```

#### 특정 값 범위의 데이터 포인트 조회
```sparql
PREFIX ts: <http://example.org/ontology/timeseries/>

SELECT ?datapoint ?value ?timestamp
WHERE {
    ?timeseries a ts:TimeSeries .
    ?timeseries ts:hasDataPoint ?datapoint .
    ?datapoint ts:hasValue ?value .
    OPTIONAL { ?datapoint ts:hasTimestamp ?timestamp }
    FILTER (?value > 25.0 && ?value < 30.0)
}
ORDER BY DESC(?value)
LIMIT 10
```

#### 시계열 데이터 통계
```sparql
PREFIX ts: <http://example.org/ontology/timeseries/>

SELECT ?timeseries (COUNT(?datapoint) as ?count) (AVG(?value) as ?avg_value)
WHERE {
    ?timeseries a ts:TimeSeries .
    ?timeseries ts:hasDataPoint ?datapoint .
    ?datapoint ts:hasValue ?value .
}
GROUP BY ?timeseries
```

### 3. 이미지 데이터 쿼리

#### 모든 이미지 조회
```sparql
PREFIX img: <http://example.org/ontology/image/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?image ?label ?width ?height ?format
WHERE {
    ?image a img:Image .
    OPTIONAL { ?image rdfs:label ?label }
    OPTIONAL { ?image img:hasWidth ?width }
    OPTIONAL { ?image img:hasHeight ?height }
    OPTIONAL { ?image img:hasFormat ?format }
}
```

#### 특정 크기 이상의 이미지 조회
```sparql
PREFIX img: <http://example.org/ontology/image/>

SELECT ?image ?width ?height
WHERE {
    ?image a img:Image .
    ?image img:hasWidth ?width .
    ?image img:hasHeight ?height .
    FILTER (?width > 1000 && ?height > 1000)
}
ORDER BY DESC(?width)
```

#### 이미지 종횡비 계산
```sparql
PREFIX img: <http://example.org/ontology/image/>

SELECT ?image ?width ?height (?width / ?height as ?aspect_ratio)
WHERE {
    ?image a img:Image .
    ?image img:hasWidth ?width .
    ?image img:hasHeight ?height .
    FILTER (?height > 0)
}
```

### 4. 복합 쿼리

#### 특정 날짜 범위의 데이터와 관련 이미지
```sparql
PREFIX ts: <http://example.org/ontology/timeseries/>
PREFIX img: <http://example.org/ontology/image/>
PREFIX ex: <http://example.org/ontology/>

SELECT ?data ?timestamp ?image
WHERE {
    {
        ?data a ts:TimeSeries .
        ?data ts:hasDataPoint ?point .
        ?point ts:hasTimestamp ?timestamp .
        FILTER (?timestamp >= "2024-01-01T00:00:00"^^xsd:dateTime && 
                ?timestamp <= "2024-12-31T23:59:59"^^xsd:dateTime)
    }
    UNION
    {
        ?image a img:Image .
    }
}
```

## Python 고급 사용 예제

### 1. 배치 데이터 업로드

```python
import os
import requests
from pathlib import Path

API_BASE = 'http://localhost:5000/api'

def batch_upload_timeseries(directory):
    """디렉토리의 모든 CSV 파일 업로드"""
    results = []
    
    for file_path in Path(directory).glob('*.csv'):
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'text/csv')}
            response = requests.post(f'{API_BASE}/upload/timeseries', files=files)
            results.append({
                'filename': file_path.name,
                'success': response.json().get('success'),
                'filepath': response.json().get('filepath')
            })
    
    return results

# 사용 예
results = batch_upload_timeseries('./data/timeseries/')
for result in results:
    print(f"{result['filename']}: {'성공' if result['success'] else '실패'}")
```

### 2. 온톨로지 자동 구축

```python
def auto_build_ontology(ontology_name, data_directory):
    """디렉토리의 모든 데이터로 온톨로지 자동 구축"""
    
    # 1. 온톨로지 생성
    response = requests.post(f'{API_BASE}/ontology/create', 
                           json={'name': ontology_name})
    if not response.json().get('success'):
        return False
    
    # 2. 시계열 데이터 추가
    for csv_file in Path(data_directory).glob('**/*.csv'):
        # 파일 업로드
        with open(csv_file, 'rb') as f:
            files = {'file': (csv_file.name, f, 'text/csv')}
            upload_response = requests.post(f'{API_BASE}/upload/timeseries', 
                                          files=files)
        
        if upload_response.json().get('success'):
            filepath = upload_response.json()['filepath']
            
            # 온톨로지에 추가
            concept_name = csv_file.stem.replace('_', ' ').title()
            requests.post(f'{API_BASE}/ontology/add_timeseries', json={
                'ontology_name': ontology_name,
                'filepath': filepath,
                'concept_name': concept_name
            })
    
    # 3. 이미지 데이터 추가
    for img_file in Path(data_directory).glob('**/*.{jpg,png,jpeg}'):
        with open(img_file, 'rb') as f:
            files = {'file': (img_file.name, f)}
            upload_response = requests.post(f'{API_BASE}/upload/image', 
                                          files=files)
        
        if upload_response.json().get('success'):
            filepath = upload_response.json()['filepath']
            concept_name = img_file.stem.replace('_', ' ').title()
            requests.post(f'{API_BASE}/ontology/add_image', json={
                'ontology_name': ontology_name,
                'filepath': filepath,
                'concept_name': concept_name
            })
    
    return True

# 사용 예
auto_build_ontology('my_project', './data/')
```

### 3. 고급 쿼리 및 분석

```python
def analyze_timeseries_patterns(ontology_name):
    """시계열 패턴 분석"""
    
    # 모든 시계열 데이터 조회
    query = """
    PREFIX ts: <http://example.org/ontology/timeseries/>
    SELECT ?timeseries ?datapoint ?value
    WHERE {
        ?timeseries a ts:TimeSeries .
        ?timeseries ts:hasDataPoint ?datapoint .
        ?datapoint ts:hasValue ?value .
    }
    """
    
    response = requests.post(f'{API_BASE}/ontology/query', json={
        'ontology_name': ontology_name,
        'query': query
    })
    
    results = response.json().get('results', [])
    
    # 데이터 분석
    import pandas as pd
    df = pd.DataFrame(results)
    
    if 'value' in df.columns:
        df['value'] = pd.to_numeric(df['value'])
        
        analysis = {
            'count': len(df),
            'mean': df['value'].mean(),
            'std': df['value'].std(),
            'min': df['value'].min(),
            'max': df['value'].max()
        }
        
        return analysis
    
    return None

# 사용 예
analysis = analyze_timeseries_patterns('my_ontology')
print(f"분석 결과: {analysis}")
```

### 4. 온톨로지 병합

```python
def merge_ontologies(target_ontology, source_ontologies):
    """여러 온톨로지를 하나로 병합"""
    
    # 타겟 온톨로지의 모든 트리플 조회
    all_triples = []
    
    for source in source_ontologies:
        query = "SELECT ?s ?p ?o WHERE { ?s ?p ?o }"
        response = requests.post(f'{API_BASE}/ontology/query', json={
            'ontology_name': source,
            'query': query
        })
        
        if response.json().get('success'):
            all_triples.extend(response.json().get('results', []))
    
    # 새 온톨로지에 트리플 추가
    # (실제 구현에서는 RDFLib을 사용하여 그래프를 직접 병합)
    
    return len(all_triples)
```

### 5. 데이터 유효성 검사

```python
def validate_ontology(ontology_name):
    """온톨로지 유효성 검사"""
    
    validations = {
        'has_classes': False,
        'has_properties': False,
        'has_instances': False,
        'issues': []
    }
    
    # 클래스 확인
    query = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT (COUNT(?class) as ?count)
    WHERE { ?class a owl:Class }
    """
    response = requests.post(f'{API_BASE}/ontology/query', json={
        'ontology_name': ontology_name,
        'query': query
    })
    
    if response.json().get('success'):
        count = int(response.json()['results'][0]['count'])
        validations['has_classes'] = count > 0
        if count == 0:
            validations['issues'].append('클래스가 정의되지 않았습니다')
    
    # 프로퍼티 확인
    query = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT (COUNT(?prop) as ?count)
    WHERE { 
        ?prop a ?type .
        FILTER (?type = owl:ObjectProperty || ?type = owl:DatatypeProperty)
    }
    """
    response = requests.post(f'{API_BASE}/ontology/query', json={
        'ontology_name': ontology_name,
        'query': query
    })
    
    if response.json().get('success'):
        count = int(response.json()['results'][0]['count'])
        validations['has_properties'] = count > 0
        if count == 0:
            validations['issues'].append('프로퍼티가 정의되지 않았습니다')
    
    return validations

# 사용 예
validation = validate_ontology('my_ontology')
print(f"유효성 검사 결과: {validation}")
```

## 커스터마이징

### 1. 커스텀 클래스 추가

```python
# ontology_builder.py에 추가

def add_custom_class(self, ontology_name, class_name, parent_class=None, properties=None):
    """커스텀 클래스 추가"""
    if ontology_name not in self.ontologies:
        self._load_ontology(ontology_name)
    
    g = self.ontologies[ontology_name]
    
    # 클래스 생성
    class_uri = self.EX[class_name]
    g.add((class_uri, RDF.type, OWL.Class))
    g.add((class_uri, RDFS.label, Literal(class_name)))
    
    # 부모 클래스 지정
    if parent_class:
        parent_uri = self.EX[parent_class]
        g.add((class_uri, RDFS.subClassOf, parent_uri))
    
    # 프로퍼티 추가
    if properties:
        for prop_name, prop_range in properties.items():
            prop_uri = self.EX[prop_name]
            g.add((prop_uri, RDF.type, OWL.DatatypeProperty))
            g.add((prop_uri, RDFS.domain, class_uri))
            g.add((prop_uri, RDFS.range, prop_range))
    
    self._save_ontology(ontology_name, g)
```

### 2. 커스텀 데이터 타입 지원

```python
# data_processor.py에 추가

class VideoProcessor:
    """비디오 데이터 처리"""
    
    def analyze(self, filepath):
        # OpenCV 또는 moviepy 사용
        import cv2
        
        cap = cv2.VideoCapture(filepath)
        
        metadata = {
            'filename': os.path.basename(filepath),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
        }
        
        cap.release()
        return metadata
```

## 성능 최적화

### 1. 대용량 데이터 처리

```python
def process_large_timeseries(filepath, batch_size=1000):
    """대용량 시계열 데이터 배치 처리"""
    import pandas as pd
    
    # 청크 단위로 읽기
    for chunk in pd.read_csv(filepath, chunksize=batch_size):
        # 각 청크 처리
        yield process_chunk(chunk)
```

### 2. 캐싱

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_ontology_metadata(ontology_name):
    """온톨로지 메타데이터 캐싱"""
    # 자주 조회되는 메타데이터를 캐시
    pass
```
