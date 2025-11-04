#!/usr/bin/env python3
"""
PREACT 안전 관제 시스템 API 테스트
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app, ai_engine, initialize_cameras
import json

def test_api():
    """API 엔드포인트 테스트"""
    
    print("🧪 PREACT 안전 관제 시스템 API 테스트")
    print("=" * 60)
    
    # Flask 테스트 클라이언트 생성
    with app.test_client() as client:
        
        # 1. 시스템 상태 확인
        print("\n[TEST 1] 시스템 상태 확인")
        print("-" * 60)
        response = client.get('/')
        data = json.loads(response.data)
        print(f"✓ 시스템: {data['system']}")
        print(f"✓ 버전: {data['version']}")
        print(f"✓ 상태: {data['status']}")
        
        # 2. 카메라 목록 조회
        print("\n[TEST 2] 카메라 목록 조회")
        print("-" * 60)
        response = client.get('/api/cameras')
        data = json.loads(response.data)
        print(f"✓ 카메라 수: {len(data['data'])}대")
        for cam in data['data']:
            print(f"  - {cam['name']}: {cam['status']}")
        
        # 3. 통계 조회
        print("\n[TEST 3] 시스템 통계 조회")
        print("-" * 60)
        response = client.get('/api/statistics')
        data = json.loads(response.data)
        stats = data['data']
        print(f"✓ 총 이벤트: {stats['total_events']}건")
        print(f"✓ 금일 이벤트: {stats['today_events']}건")
        print(f"✓ 활성 카메라: {stats['active_cameras']}대")
        print(f"✓ 긴급 경보: {stats['critical_alerts']}건")
        print(f"✓ 시스템 가동률: {stats['system_uptime']}")
        print(f"✓ 평균 응답 시간: {stats['average_response_time']}")
        
        # 4. 모니터링 시작
        print("\n[TEST 4] 모니터링 시작")
        print("-" * 60)
        response = client.post('/api/monitoring/start')
        data = json.loads(response.data)
        print(f"✓ {data['message']}")
        
        # 5. AI 분석 엔진 테스트
        print("\n[TEST 5] AI 분석 엔진 테스트")
        print("-" * 60)
        for i in range(3):
            result = ai_engine.analyze_frame('CAM001', None)
            if result['detected']:
                print(f"✓ 테스트 {i+1}: {result['type']} 감지 (신뢰도: {result['confidence']*100:.0f}%)")
            else:
                print(f"✓ 테스트 {i+1}: 이상 없음")
        
        # 6. 보고서 생성
        print("\n[TEST 6] 보고서 생성")
        print("-" * 60)
        response = client.post('/api/report/generate',
                               data=json.dumps({'type': 'daily'}),
                               content_type='application/json')
        data = json.loads(response.data)
        report = data['data']
        print(f"✓ 보고서 ID: {report['id']}")
        print(f"✓ 유형: {report['type']}")
        print(f"✓ 총 이벤트: {report['summary']['total_events']}건")
        
        # 7. sLLM 질의응답
        print("\n[TEST 7] sLLM 질의응답")
        print("-" * 60)
        queries = ['화재 통계', '안전모', '통계']
        for query in queries:
            response = client.post('/api/query',
                                  data=json.dumps({'query': query}),
                                  content_type='application/json')
            data = json.loads(response.data)
            print(f"✓ 질문: {data['data']['query']}")
            print(f"  답변: {data['data']['response'][:80]}...")
        
        # 8. 모니터링 중지
        print("\n[TEST 8] 모니터링 중지")
        print("-" * 60)
        response = client.post('/api/monitoring/stop')
        data = json.loads(response.data)
        print(f"✓ {data['message']}")
    
    print("\n" + "=" * 60)
    print("✅ 모든 테스트 완료!")
    print("=" * 60)

if __name__ == '__main__':
    test_api()
