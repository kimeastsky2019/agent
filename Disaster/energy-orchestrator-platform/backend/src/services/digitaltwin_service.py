"""
Digital Twin Service for Smart Grid
실시간 스마트 그리드 디지털 트윈 시뮬레이션 서비스
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, AsyncGenerator
import logging

# 원본 파일을 import
import sys
import os

# 현재 디렉토리에서 smart_grid_digital_twin 모듈 찾기
current_dir = os.path.dirname(os.path.abspath(__file__))
twin_file = os.path.join(current_dir, 'smart_grid_digital_twin.py')

try:
    if os.path.exists(twin_file):
        # 파일이 존재하면 직접 import
        import importlib.util
        spec = importlib.util.spec_from_file_location("smart_grid_digital_twin", twin_file)
        smart_grid_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(smart_grid_module)
        SmartGridDigitalTwin = smart_grid_module.SmartGridDigitalTwin
        DIGITALTWIN_AVAILABLE = True
    else:
        DIGITALTWIN_AVAILABLE = False
        logging.warning(f"smart_grid_digital_twin.py not found at {twin_file}")
except Exception as e:
    DIGITALTWIN_AVAILABLE = False
    logging.warning(f"smart_grid_digital_twin not available: {e}. Using mock implementation.")

logger = logging.getLogger(__name__)

class DigitalTwinService:
    """디지털 트윈 서비스"""
    
    def __init__(self, asset_id: str):
        self.asset_id = asset_id
        self.twin: Optional[SmartGridDigitalTwin] = None
        self.is_running = False
        self.current_state: Dict[str, Any] = {}
        
    async def initialize(self) -> bool:
        """디지털 트윈 초기화"""
        try:
            if DIGITALTWIN_AVAILABLE:
                self.twin = SmartGridDigitalTwin()
                logger.info(f"Digital twin initialized for asset {self.asset_id}")
                return True
            else:
                logger.warning("SmartGridDigitalTwin not available, using mock")
                return False
        except Exception as e:
            logger.error(f"Error initializing digital twin: {e}")
            return False
    
    async def get_current_state(self) -> Dict[str, Any]:
        """현재 상태 조회"""
        if not self.twin:
            return self._get_mock_state()
        
        try:
            state = self.twin.get_system_state()
            return {
                'asset_id': self.asset_id,
                'timestamp': datetime.now().isoformat(),
                'environment': {
                    'temperature': self.twin.environment.temperature,
                    'solar_radiation': self.twin.environment.solar_radiation,
                    'wind_speed': self.twin.environment.wind_speed,
                    'occupancy': self.twin.environment.occupancy,
                    'humidity': self.twin.environment.humidity
                },
                'power': {
                    'total_demand': state['total_demand'],
                    'total_supply': state['total_supply'],
                    'balance': state['power_balance'],
                    'ess_soc': self.twin.ess.current_soc * 100
                },
                'devices': {
                    'total': len(self.twin.devices),
                    'active': sum(1 for d in self.twin.devices if d.is_active),
                    'consumption': sum(d.get_power_consumption() for d in self.twin.devices)
                },
                'supplies': [
                    {
                        'source_id': s.source_id,
                        'source_type': s.source_type.value,
                        'capacity': s.capacity,
                        'current_output': s.current_output,
                        'available': s.get_available_power()
                    }
                    for s in self.twin.supplies
                ],
                'ess': {
                    'capacity': self.twin.ess.capacity,
                    'current_soc': self.twin.ess.current_soc * 100,
                    'max_charge_rate': self.twin.ess.max_charge_rate,
                    'max_discharge_rate': self.twin.ess.max_discharge_rate
                }
            }
        except Exception as e:
            logger.error(f"Error getting current state: {e}")
            return self._get_mock_state()
    
    async def run_control_cycle(self) -> Dict[str, Any]:
        """제어 사이클 실행"""
        if not self.twin:
            return self._get_mock_cycle_result()
        
        try:
            # 현재 시간 업데이트
            self.twin.current_time = datetime.now()
            hour = self.twin.current_time.hour
            
            # 환경 업데이트
            self.twin.update_environment(hour)
            
            # 디바이스 사용 패턴 시뮬레이션
            self.twin.simulate_device_usage(hour)
            
            # 제어 사이클 실행
            result = self.twin.run_control_cycle()
            
            # 결과 변환
            return {
                'asset_id': self.asset_id,
                'timestamp': result['timestamp'].isoformat(),
                'environment': result['environment'],
                'power': result['power'],
                'supply_optimization': result['supply_optimization'],
                'demand_response': result['demand_response'],
                'pricing': result['pricing'],
                'performance_metrics': result['performance_metrics']
            }
        except Exception as e:
            logger.error(f"Error running control cycle: {e}")
            return self._get_mock_cycle_result()
    
    async def run_simulation_stream(
        self,
        duration_hours: int = 24,
        time_step_minutes: int = 15
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """실시간 시뮬레이션 스트림"""
        if not self.twin:
            # Mock 스트림
            for i in range(10):
                await asyncio.sleep(1)
                yield self._get_mock_cycle_result()
            return
        
        try:
            steps = int(duration_hours * 60 / time_step_minutes)
            time_step = timedelta(minutes=time_step_minutes)
            
            for step in range(steps):
                # 시간 업데이트
                self.twin.current_time += time_step
                hour = self.twin.current_time.hour
                
                # 환경 업데이트
                self.twin.update_environment(hour)
                
                # 디바이스 사용 패턴
                self.twin.simulate_device_usage(hour)
                
                # 제어 사이클 실행
                result = self.twin.run_control_cycle()
                
                # 결과 변환 및 전송
                yield {
                    'asset_id': self.asset_id,
                    'step': step,
                    'total_steps': steps,
                    'timestamp': result['timestamp'].isoformat(),
                    'environment': result['environment'],
                    'power': result['power'],
                    'supply_optimization': result['supply_optimization'],
                    'demand_response': result['demand_response'],
                    'pricing': result['pricing'],
                    'performance_metrics': result['performance_metrics']
                }
                
                # 실시간 업데이트를 위한 지연
                await asyncio.sleep(0.1)  # 100ms 간격
                
        except Exception as e:
            logger.error(f"Error in simulation stream: {e}")
            yield self._get_mock_cycle_result()
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """성능 지표 조회"""
        if not self.twin or not self.twin.simulation_log:
            return self._get_mock_metrics()
        
        try:
            if len(self.twin.simulation_log) == 0:
                return self._get_mock_metrics()
            
            # 최근 로그에서 메트릭 계산
            recent_logs = self.twin.simulation_log[-100:]  # 최근 100개
            
            metrics = {
                'renewable_ratio_avg': sum(
                    log['performance_metrics']['renewable_ratio'] 
                    for log in recent_logs
                ) / len(recent_logs),
                'stability_score_avg': sum(
                    log['performance_metrics']['stability_score'] 
                    for log in recent_logs
                ) / len(recent_logs),
                'cost_efficiency_avg': sum(
                    log['performance_metrics']['cost_efficiency'] 
                    for log in recent_logs
                ) / len(recent_logs),
                'ess_utilization_avg': sum(
                    log['performance_metrics']['ess_utilization'] 
                    for log in recent_logs
                ) / len(recent_logs),
                'overall_score_avg': sum(
                    log['performance_metrics']['overall_score'] 
                    for log in recent_logs
                ) / len(recent_logs),
                'total_records': len(recent_logs)
            }
            
            return metrics
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return self._get_mock_metrics()
    
    def _get_mock_state(self) -> Dict[str, Any]:
        """Mock 상태 데이터"""
        return {
            'asset_id': self.asset_id,
            'timestamp': datetime.now().isoformat(),
            'environment': {
                'temperature': 25.0,
                'solar_radiation': 500.0,
                'wind_speed': 5.0,
                'occupancy': 300,
                'humidity': 50.0
            },
            'power': {
                'total_demand': 50.0,
                'total_supply': 60.0,
                'balance': 10.0,
                'ess_soc': 60.0
            },
            'devices': {
                'total': 48,
                'active': 30,
                'consumption': 50.0
            },
            'supplies': [
                {'source_id': 'solar_1', 'source_type': '태양광', 'capacity': 100.0, 'current_output': 40.0, 'available': 38.0},
                {'source_id': 'wind_1', 'source_type': '풍력', 'capacity': 50.0, 'current_output': 20.0, 'available': 19.0},
                {'source_id': 'grid_1', 'source_type': '전력망', 'capacity': 500.0, 'current_output': 0.0, 'available': 500.0}
            ],
            'ess': {
                'capacity': 200.0,
                'current_soc': 60.0,
                'max_charge_rate': 50.0,
                'max_discharge_rate': 50.0
            }
        }
    
    def _get_mock_cycle_result(self) -> Dict[str, Any]:
        """Mock 사이클 결과"""
        return {
            'asset_id': self.asset_id,
            'timestamp': datetime.now().isoformat(),
            'environment': {
                'temperature': 25.0,
                'solar_radiation': 500.0,
                'wind_speed': 5.0,
                'occupancy': 300
            },
            'power': {
                'total_demand': 50.0,
                'total_supply': 60.0,
                'balance': 10.0,
                'ess_soc': 60.0
            },
            'supply_optimization': {
                'agent': '공급최적화 에이전트',
                'renewable_ratio': 0.8
            },
            'demand_response': {
                'agent': '수요반응 에이전트',
                'decisions': []
            },
            'pricing': {
                'agent': '가격 결정 에이전트',
                'price_kwh': 100.0
            },
            'performance_metrics': {
                'renewable_ratio': 80.0,
                'stability_score': 90.0,
                'cost_efficiency': 95.0,
                'ess_utilization': 85.0,
                'overall_score': 87.5
            }
        }
    
    def _get_mock_metrics(self) -> Dict[str, Any]:
        """Mock 메트릭"""
        return {
            'renewable_ratio_avg': 80.0,
            'stability_score_avg': 90.0,
            'cost_efficiency_avg': 95.0,
            'ess_utilization_avg': 85.0,
            'overall_score_avg': 87.5,
            'total_records': 100
        }
