#!/usr/bin/env python3
"""
온톨로지 서비스 API 사용 예제
"""

import requests
import json
import time

API_BASE = 'http://localhost:5000/api'

def test_health():
    """헬스 체크"""
    print("=== 헬스 체크 ===")
    response = requests.get(f'{API_BASE}/health')
    print(f"상태: {response.json()}")
    print()

def upload_timeseries():
    """시계열 데이터 업로드"""
    print("=== 시계열 데이터 업로드 ===")
    
    with open('example_data/sample_timeseries.csv', 'rb') as f:
        files = {'file': ('sample_timeseries.csv', f, 'text/csv')}
        response = requests.post(f'{API_BASE}/upload/timeseries', files=files)
    
    result = response.json()
    print(f"업로드 결과: {result.get('success')}")
    if result.get('success'):
        print(f"파일 경로: {result.get('filepath')}")
        print(f"메타데이터:\n{json.dumps(result.get('metadata'), indent=2)}")
    print()
    return result.get('filepath')

def create_ontology(name):
    """온톨로지 생성"""
    print(f"=== 온톨로지 생성: {name} ===")
    
    data = {
        'name': name,
        'data_sources': []
    }
    response = requests.post(f'{API_BASE}/ontology/create', json=data)
    
    result = response.json()
    print(f"생성 결과: {result.get('success')}")
    if result.get('success'):
        print(f"온톨로지 경로: {result.get('ontology_path')}")
        print(f"온톨로지 URI: {result.get('ontology_uri')}")
    print()
    return result.get('success')

def add_timeseries_to_ontology(ontology_name, filepath, concept_name):
    """시계열 데이터를 온톨로지에 추가"""
    print(f"=== 온톨로지에 시계열 데이터 추가 ===")
    
    data = {
        'ontology_name': ontology_name,
        'filepath': filepath,
        'concept_name': concept_name
    }
    response = requests.post(f'{API_BASE}/ontology/add_timeseries', json=data)
    
    result = response.json()
    print(f"추가 결과: {result.get('success')}")
    print()
    return result.get('success')

def query_ontology(ontology_name):
    """온톨로지 쿼리"""
    print("=== 온톨로지 쿼리 (모든 트리플) ===")
    
    # 기본 쿼리: 모든 트리플 조회
    query = "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 20"
    
    data = {
        'ontology_name': ontology_name,
        'query': query
    }
    response = requests.post(f'{API_BASE}/ontology/query', json=data)
    
    result = response.json()
    print(f"쿼리 결과: {result.get('success')}")
    if result.get('success'):
        results = result.get('results', [])
        print(f"결과 개수: {len(results)}")
        for i, row in enumerate(results[:5], 1):
            print(f"{i}. {row}")
    print()

def query_timeseries_data(ontology_name):
    """시계열 데이터 쿼리"""
    print("=== 시계열 데이터 쿼리 ===")
    
    query = """
    PREFIX ts: <http://example.org/ontology/timeseries/>
    SELECT ?timeseries ?value
    WHERE {
        ?timeseries a ts:TimeSeries .
        ?timeseries ts:hasDataPoint ?datapoint .
        ?datapoint ts:hasValue ?value .
    }
    LIMIT 10
    """
    
    data = {
        'ontology_name': ontology_name,
        'query': query
    }
    response = requests.post(f'{API_BASE}/ontology/query', json=data)
    
    result = response.json()
    print(f"쿼리 결과: {result.get('success')}")
    if result.get('success'):
        results = result.get('results', [])
        print(f"결과 개수: {len(results)}")
        for i, row in enumerate(results[:10], 1):
            print(f"{i}. {row}")
    print()

def list_ontologies():
    """온톨로지 목록 조회"""
    print("=== 온톨로지 목록 ===")
    
    response = requests.get(f'{API_BASE}/ontology/list')
    result = response.json()
    
    if result.get('success'):
        ontologies = result.get('ontologies', [])
        print(f"총 {len(ontologies)}개의 온톨로지:")
        for ont in ontologies:
            print(f"  - {ont}")
    print()

def visualize_ontology(ontology_name):
    """온톨로지 시각화 데이터 조회"""
    print(f"=== 온톨로지 시각화: {ontology_name} ===")
    
    response = requests.get(f'{API_BASE}/ontology/visualize/{ontology_name}')
    result = response.json()
    
    if result.get('success'):
        graph = result.get('graph', {})
        nodes = graph.get('nodes', [])
        edges = graph.get('edges', [])
        print(f"노드 수: {len(nodes)}")
        print(f"엣지 수: {len(edges)}")
        
        if nodes:
            print("\n처음 5개 노드:")
            for node in nodes[:5]:
                print(f"  - {node.get('label')} ({node.get('type')})")
        
        if edges:
            print("\n처음 5개 엣지:")
            for edge in edges[:5]:
                print(f"  - {edge.get('label')}")
    print()

def export_ontology(ontology_name):
    """온톨로지 내보내기"""
    print(f"=== 온톨로지 내보내기: {ontology_name} ===")
    
    response = requests.get(f'{API_BASE}/ontology/export/{ontology_name}')
    
    if response.status_code == 200:
        filename = f'{ontology_name}_exported.owl'
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"온톨로지가 '{filename}'로 저장되었습니다")
    else:
        print(f"내보내기 실패: {response.status_code}")
    print()

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("온톨로지 서비스 API 테스트")
    print("=" * 60)
    print()
    
    # 1. 헬스 체크
    test_health()
    
    # 2. 시계열 데이터 업로드
    ts_filepath = upload_timeseries()
    
    # 3. 온톨로지 생성
    ontology_name = f'test_ontology_{int(time.time())}'
    if create_ontology(ontology_name):
        
        # 4. 시계열 데이터를 온톨로지에 추가
        if ts_filepath:
            add_timeseries_to_ontology(
                ontology_name=ontology_name,
                filepath=ts_filepath,
                concept_name='WeatherSensor'
            )
        
        # 5. 온톨로지 쿼리
        query_ontology(ontology_name)
        query_timeseries_data(ontology_name)
        
        # 6. 시각화 데이터 조회
        visualize_ontology(ontology_name)
        
        # 7. 온톨로지 내보내기
        export_ontology(ontology_name)
    
    # 8. 온톨로지 목록 조회
    list_ontologies()
    
    print("=" * 60)
    print("테스트 완료!")
    print("=" * 60)

if __name__ == '__main__':
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("오류: 서버에 연결할 수 없습니다.")
        print("서버가 실행 중인지 확인하세요: python app.py")
    except Exception as e:
        print(f"오류 발생: {e}")
