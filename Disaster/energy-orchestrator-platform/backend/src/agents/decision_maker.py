from src.agents.base_agent import BaseAgent
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class DecisionMakerAgent(BaseAgent):
    """의사결정 에이전트"""
    
    def __init__(self):
        super().__init__("DecisionMaker")
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """최적 에너지 재분배 시나리오 생성"""
        disaster_analysis = data.get("disaster_analysis", {})
        energy_analysis = data.get("energy_analysis", {})
        
        # 재난 영향권 내 자산 식별
        affected_assets = data.get("affected_assets", [])
        
        # 에너지 재분배 계획 수립
        scenario = {
            "priority": self._calculate_priority(disaster_analysis, energy_analysis),
            "actions": self._generate_actions(disaster_analysis, energy_analysis, affected_assets),
            "estimated_impact": self._estimate_impact(disaster_analysis, energy_analysis)
        }
        
        self.add_to_memory({
            "timestamp": data.get("timestamp"),
            "scenario": scenario
        })
        
        logger.info(f"Decision scenario created: {scenario}")
        return scenario
    
    def _calculate_priority(
        self,
        disaster_analysis: Dict[str, Any],
        energy_analysis: Dict[str, Any]
    ) -> str:
        """우선순위 계산"""
        risk_level = disaster_analysis.get("risk_level", "low")
        balance = energy_analysis.get("balance", 0)
        
        if risk_level == "high" or balance < -100:
            return "urgent"
        elif risk_level == "medium" or abs(balance) > 50:
            return "high"
        else:
            return "normal"
    
    def _generate_actions(
        self,
        disaster_analysis: Dict[str, Any],
        energy_analysis: Dict[str, Any],
        affected_assets: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """액션 생성"""
        actions = []
        
        surplus_assets = energy_analysis.get("surplus_assets", [])
        deficit_assets = energy_analysis.get("deficit_assets", [])
        
        # 에너지 재분배 액션
        if surplus_assets and deficit_assets:
            for surplus_id in surplus_assets[:3]:  # 최대 3개
                for deficit_id in deficit_assets[:3]:
                    actions.append({
                        "type": "energy_redistribution",
                        "source_asset_id": surplus_id,
                        "target_asset_id": deficit_id,
                        "amount_kw": 50.0,  # 예시 값
                        "priority": "high"
                    })
        
        # 비상 전력 공급 액션
        if affected_assets:
            actions.append({
                "type": "emergency_power",
                "target_assets": [a.get("id") for a in affected_assets],
                "priority": "urgent"
            })
        
        return actions
    
    def _estimate_impact(
        self,
        disaster_analysis: Dict[str, Any],
        energy_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """영향 추정"""
        return {
            "affected_energy_capacity": 1000.0,  # 예시 값
            "estimated_restoration_time": "2-4 hours",
            "energy_loss_estimate": energy_analysis.get("balance", 0)
        }




