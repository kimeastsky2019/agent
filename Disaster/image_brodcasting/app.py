from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import random
import os
from threading import Thread
import time

app = Flask(__name__)
CORS(app)

# 데이터 저장 경로
DATA_DIR = '../data'
LOGS_DIR = '../logs'

# 이벤트 저장소
events = []
alerts = []
camera_feeds = []

# 시뮬레이션 상태
simulation_running = False

# AI 분석 시뮬레이터
class AIAnalysisEngine:
    def __init__(self):
        self.risk_threshold = 0.7
        self.detection_types = [
            'fire', 'smoke', 'abnormal_behavior', 
            'no_safety_gear', 'temperature_anomaly'
        ]
        
    def analyze_frame(self, camera_id, frame_data):
        """프레임 분석 시뮬레이션"""
        # 랜덤하게 위험 상황 생성
        risk_level = random.random()
        
        if risk_level > self.risk_threshold:
            detection_type = random.choice(self.detection_types)
            confidence = round(risk_level, 2)
            
            return {
                'detected': True,
                'type': detection_type,
                'confidence': confidence,
                'timestamp': datetime.now().isoformat(),
                'camera_id': camera_id,
                'location': self.get_location_name(camera_id),
                'description': self.get_description(detection_type)
            }
        
        return {'detected': False}
    
    def get_location_name(self, camera_id):
        locations = {
            'CAM001': '생산라인 A',
            'CAM002': '용접 구역',
            'CAM003': '적재 구역',
            'CAM004': '출입구',
            'DRONE01': '외부 순찰 드론'
        }
        return locations.get(camera_id, '알 수 없음')
    
    def get_description(self, detection_type):
        descriptions = {
            'fire': '화재 징후 감지',
            'smoke': '연기 발생 감지',
            'abnormal_behavior': '작업자 이상행동 감지',
            'no_safety_gear': '안전보호구 미착용',
            'temperature_anomaly': '이상 온도 감지'
        }
        return descriptions.get(detection_type, '알 수 없는 위험')

ai_engine = AIAnalysisEngine()

# 카메라 피드 초기화
def initialize_cameras():
    global camera_feeds
    camera_feeds = [
        {
            'id': 'CAM001',
            'name': '생산라인 A',
            'location': 'Building A - Floor 1',
            'status': 'active',
            'type': 'RGB+IR'
        },
        {
            'id': 'CAM002',
            'name': '용접 구역',
            'location': 'Building A - Floor 2',
            'status': 'active',
            'type': 'RGB+UV'
        },
        {
            'id': 'CAM003',
            'name': '적재 구역',
            'location': 'Building B - Floor 1',
            'status': 'active',
            'type': 'RGB'
        },
        {
            'id': 'CAM004',
            'name': '출입구',
            'location': 'Main Entrance',
            'status': 'active',
            'type': 'RGB'
        },
        {
            'id': 'DRONE01',
            'name': '외부 순찰 드론',
            'location': 'Outdoor Patrol',
            'status': 'active',
            'type': 'RGB+IR+UV'
        }
    ]

initialize_cameras()

# 실시간 모니터링 시뮬레이션
def monitoring_simulation():
    global simulation_running, events, alerts
    
    while simulation_running:
        # 각 카메라에서 프레임 분석
        for camera in camera_feeds:
            if camera['status'] == 'active':
                result = ai_engine.analyze_frame(camera['id'], None)
                
                if result['detected']:
                    # 이벤트 생성
                    event = {
                        'id': f"EVT{len(events)+1:05d}",
                        'timestamp': result['timestamp'],
                        'camera_id': result['camera_id'],
                        'location': result['location'],
                        'type': result['type'],
                        'confidence': result['confidence'],
                        'description': result['description'],
                        'status': 'pending',
                        'severity': 'high' if result['confidence'] > 0.85 else 'medium'
                    }
                    events.append(event)
                    
                    # 경보 생성
                    if result['confidence'] > 0.85:
                        alert = {
                            'id': f"ALT{len(alerts)+1:05d}",
                            'event_id': event['id'],
                            'timestamp': result['timestamp'],
                            'message': f"{result['location']}에서 {result['description']}",
                            'severity': 'critical',
                            'actions_taken': ['관리자 알림 전송', '경광등 작동', '현장 방송']
                        }
                        alerts.append(alert)
        
        # 5-15초마다 체크
        time.sleep(random.randint(5, 15))

# API 엔드포인트

@app.route('/')
def index():
    return jsonify({
        'system': 'PREACT Safety Monitoring System',
        'version': '1.0.0',
        'status': 'operational'
    })

@app.route('/api/cameras', methods=['GET'])
def get_cameras():
    """카메라 목록 조회"""
    return jsonify({
        'success': True,
        'data': camera_feeds
    })

@app.route('/api/events', methods=['GET'])
def get_events():
    """이벤트 목록 조회"""
    limit = request.args.get('limit', 50, type=int)
    event_type = request.args.get('type', None)
    
    filtered_events = events
    if event_type:
        filtered_events = [e for e in events if e['type'] == event_type]
    
    return jsonify({
        'success': True,
        'data': filtered_events[-limit:],
        'total': len(filtered_events)
    })

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """경보 목록 조회"""
    limit = request.args.get('limit', 20, type=int)
    
    return jsonify({
        'success': True,
        'data': alerts[-limit:],
        'total': len(alerts)
    })

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """통계 데이터 조회"""
    today = datetime.now().date()
    
    # 오늘 이벤트 필터링
    today_events = [e for e in events if datetime.fromisoformat(e['timestamp']).date() == today]
    
    # 유형별 카운트
    type_counts = {}
    for event in today_events:
        event_type = event['type']
        type_counts[event_type] = type_counts.get(event_type, 0) + 1
    
    return jsonify({
        'success': True,
        'data': {
            'total_events': len(events),
            'today_events': len(today_events),
            'active_cameras': len([c for c in camera_feeds if c['status'] == 'active']),
            'critical_alerts': len([a for a in alerts if a['severity'] == 'critical']),
            'type_distribution': type_counts,
            'system_uptime': '99.8%',
            'average_response_time': '2.3s'
        }
    })

@app.route('/api/monitoring/start', methods=['POST'])
def start_monitoring():
    """모니터링 시작"""
    global simulation_running
    
    if not simulation_running:
        simulation_running = True
        thread = Thread(target=monitoring_simulation)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': '모니터링이 시작되었습니다.'
        })
    
    return jsonify({
        'success': False,
        'message': '모니터링이 이미 실행 중입니다.'
    })

@app.route('/api/monitoring/stop', methods=['POST'])
def stop_monitoring():
    """모니터링 중지"""
    global simulation_running
    
    simulation_running = False
    
    return jsonify({
        'success': True,
        'message': '모니터링이 중지되었습니다.'
    })

@app.route('/api/report/generate', methods=['POST'])
def generate_report():
    """보고서 생성"""
    data = request.json
    report_type = data.get('type', 'daily')
    
    # 날짜 범위 설정
    end_date = datetime.now()
    if report_type == 'daily':
        start_date = end_date - timedelta(days=1)
    elif report_type == 'weekly':
        start_date = end_date - timedelta(days=7)
    else:  # monthly
        start_date = end_date - timedelta(days=30)
    
    # 해당 기간 이벤트 필터링
    period_events = [
        e for e in events 
        if start_date <= datetime.fromisoformat(e['timestamp']) <= end_date
    ]
    
    # 통계 계산
    type_counts = {}
    severity_counts = {'high': 0, 'medium': 0, 'low': 0}
    
    for event in period_events:
        event_type = event['type']
        type_counts[event_type] = type_counts.get(event_type, 0) + 1
        severity_counts[event.get('severity', 'medium')] += 1
    
    report = {
        'id': f"RPT{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'type': report_type,
        'period': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        },
        'summary': {
            'total_events': len(period_events),
            'type_distribution': type_counts,
            'severity_distribution': severity_counts,
            'cameras_monitored': len(camera_feeds)
        },
        'top_incidents': period_events[-5:],
        'recommendations': [
            '용접 구역의 화재 감지 빈도가 높습니다. 소화 장비 점검을 권장합니다.',
            '안전보호구 미착용 사례가 증가하고 있습니다. 안전 교육 강화가 필요합니다.',
            '야간 시간대 이상행동 감지가 증가했습니다. 순찰 강화를 권장합니다.'
        ],
        'generated_at': datetime.now().isoformat()
    }
    
    return jsonify({
        'success': True,
        'data': report
    })

@app.route('/api/query', methods=['POST'])
def sllm_query():
    """sLLM 기반 질의응답"""
    data = request.json
    query = data.get('query', '')
    
    # 간단한 규칙 기반 응답 (실제로는 sLLM 사용)
    responses = {
        '화재': '화재 관련 이벤트는 총 {}건이 감지되었습니다. 주로 용접 구역에서 발생하고 있으며, RGB+IR 센서를 통해 조기 감지되고 있습니다.',
        '안전모': '안전보호구 미착용 사례는 {}건 입니다. 주로 적재 구역에서 발생하고 있습니다.',
        '통계': '현재까지 총 {}개의 이벤트가 감지되었으며, {}개의 카메라가 정상 작동 중입니다.',
        '보고서': '일일/주간/월간 보고서를 자동으로 생성할 수 있습니다. 보고서 생성 기능을 사용해주세요.'
    }
    
    response_text = '질의하신 내용에 대한 정보를 찾을 수 없습니다. 다시 질문해주세요.'
    
    for keyword, template in responses.items():
        if keyword in query:
            if '{}' in template:
                if keyword == '화재':
                    count = len([e for e in events if e['type'] == 'fire'])
                    response_text = template.format(count)
                elif keyword == '안전모':
                    count = len([e for e in events if e['type'] == 'no_safety_gear'])
                    response_text = template.format(count)
                elif keyword == '통계':
                    response_text = template.format(len(events), len(camera_feeds))
            else:
                response_text = template
            break
    
    return jsonify({
        'success': True,
        'data': {
            'query': query,
            'response': response_text,
            'timestamp': datetime.now().isoformat()
        }
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5001))
    print("🛡️ PREACT Safety Monitoring System Backend")
    print("=" * 50)
    print(f"Server starting on http://localhost:{port}")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=port)
