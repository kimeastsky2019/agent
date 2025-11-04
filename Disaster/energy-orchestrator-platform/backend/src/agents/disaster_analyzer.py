from src.agents.base_agent import BaseAgent
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class DisasterAnalyzerAgent(BaseAgent):
    """재난 분석 에이전트"""
    
    def __init__(self):
        super().__init__("DisasterAnalyzer")
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """재난 상황 분석"""
        disaster_info = data.get("disaster", {})
        
        # 재난 수준 평가
        severity = disaster_info.get("severity", 0)
        event_type = disaster_info.get("event_type", "unknown")
        
        # 영향 범위 분석
        affected_radius = disaster_info.get("affected_radius_km", 0)
        
        analysis = {
            "severity": severity,
            "event_type": event_type,
            "affected_radius_km": affected_radius,
            "risk_level": self._calculate_risk_level(severity, affected_radius),
            "recommendations": self._generate_recommendations(severity, event_type)
        }
        
        self.add_to_memory({
            "timestamp": data.get("timestamp"),
            "analysis": analysis
        })
        
        logger.info(f"Disaster analysis completed: {analysis}")
        return analysis
    
    def _calculate_risk_level(self, severity: int, radius: float) -> str:
        """위험 수준 계산"""
        if severity >= 4 or radius >= 50:
            return "high"
        elif severity >= 3 or radius >= 20:
            return "medium"
        else:
            return "low"
    
    def _generate_recommendations(self, severity: int, event_type: str) -> List[str]:
        """추천 사항 생성"""
        recommendations = []
        
        if severity >= 4:
            recommendations.append("즉시 에너지 재분배 계획 수립")
            recommendations.append("비상 전력 공급 경로 확인")
        
        if event_type in ["earthquake", "tsunami"]:
            recommendations.append("전력망 연결 상태 확인")
            recommendations.append("아일랜딩 모드 전환 검토")
        
        return recommendations




