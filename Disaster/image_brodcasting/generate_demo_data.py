#!/usr/bin/env python3
"""데모 데이터 생성 스크립트"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app, events, alerts, camera_feeds
from datetime import datetime, timedelta
import random

def generate_demo_data():
    print("🎬 PREACT 안전 관제 시스템 - 데모 데이터 생성")
    print("=" * 60)
    
    sample_events = [
        {'type': 'fire', 'camera_id': 'CAM002', 'location': '용접 구역', 
         'description': '화재 징후 감지', 'confidence': 0.92, 'severity': 'high'},
        {'type': 'smoke', 'camera_id': 'CAM002', 'location': '용접 구역',
         'description': '연기 발생 감지', 'confidence': 0.88, 'severity': 'high'},
        {'type': 'no_safety_gear', 'camera_id': 'CAM003', 'location': '적재 구역',
         'description': '안전보호구 미착용', 'confidence': 0.95, 'severity': 'medium'},
        {'type': 'abnormal_behavior', 'camera_id': 'CAM001', 'location': '생산라인 A',
         'description': '작업자 이상행동 감지', 'confidence': 0.78, 'severity': 'medium'},
        {'type': 'temperature_anomaly', 'camera_id': 'CAM002', 'location': '용접 구역',
         'description': '이상 온도 감지', 'confidence': 0.85, 'severity': 'high'},
        {'type': 'no_safety_gear', 'camera_id': 'CAM004', 'location': '출입구',
         'description': '안전보호구 미착용', 'confidence': 0.91, 'severity': 'medium'},
        {'type': 'fire', 'camera_id': 'DRONE01', 'location': '외부 순찰 드론',
         'description': '화재 징후 감지', 'confidence': 0.96, 'severity': 'high'}
    ]
    
    print("\n📝 이벤트 생성 중...")
    
    now = datetime.now()
    for i, sample in enumerate(sample_events):
        hours_ago = random.randint(0, 24)
        timestamp = now - timedelta(hours=hours_ago, minutes=random.randint(0, 59))
        
        event = {
            'id': f"EVT{i+1:05d}",
            'timestamp': timestamp.isoformat(),
            'camera_id': sample['camera_id'],
            'location': sample['location'],
            'type': sample['type'],
            'confidence': sample['confidence'],
            'description': sample['description'],
            'status': 'resolved' if random.random() > 0.3 else 'pending',
            'severity': sample['severity']
        }
        events.append(event)
        print(f"  ✓ {event['id']}: {event['description']} ({event['location']})")
        
        if sample['severity'] == 'high':
            alert = {
                'id': f"ALT{len(alerts)+1:05d}",
                'event_id': event['id'],
                'timestamp': timestamp.isoformat(),
                'message': f"{sample['location']}에서 {sample['description']}",
                'severity': 'critical',
                'actions_taken': ['관리자 알림 전송', '경광등 작동', '현장 방송']
            }
            alerts.append(alert)
    
    print(f"\n✅ 총 {len(events)}개의 이벤트 생성 완료")
    print(f"✅ 총 {len(alerts)}개의 경보 생성 완료")
    
    # 통계
    type_counts = {}
    for event in events:
        event_type = event['type']
        type_counts[event_type] = type_counts.get(event_type, 0) + 1
    
    print("\n" + "=" * 60)
    print("📊 생성된 데이터 통계")
    print("=" * 60)
    print("\n[유형별 분포]")
    for event_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {event_type}: {count}건")
    
    severity_counts = {'high': 0, 'medium': 0, 'low': 0}
    for event in events:
        severity_counts[event.get('severity', 'medium')] += 1
    
    print("\n[심각도별 분포]")
    print(f"  - 높음: {severity_counts['high']}건")
    print(f"  - 중간: {severity_counts['medium']}건")
    print(f"  - 낮음: {severity_counts['low']}건")
    
    camera_counts = {}
    for event in events:
        camera_id = event['camera_id']
        camera_counts[camera_id] = camera_counts.get(camera_id, 0) + 1
    
    print("\n[카메라별 감지]")
    for camera_id, count in sorted(camera_counts.items(), key=lambda x: x[1], reverse=True):
        cam_name = next((c['name'] for c in camera_feeds if c['id'] == camera_id), camera_id)
        print(f"  - {cam_name} ({camera_id}): {count}건")
    
    print("\n" + "=" * 60)
    print("✅ 데모 데이터 생성 완료!")
    print("=" * 60)
    print("\n💡 이제 대시보드를 열어 데이터를 확인하세요!")

if __name__ == '__main__':
    generate_demo_data()
