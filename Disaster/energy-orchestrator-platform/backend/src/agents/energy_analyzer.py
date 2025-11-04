from src.agents.base_agent import BaseAgent
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class EnergyAnalyzerAgent(BaseAgent):
    """에너지 분석 에이전트"""
    
    def __init__(self):
        super().__init__("EnergyAnalyzer")
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """에너지 수급 현황 분석"""
        assets = data.get("assets", [])
        current_readings = data.get("readings", {})
        
        total_production = sum(
            asset.get("production", 0) for asset in assets
            if asset.get("type") in ["solar", "wind"]
        )
        
        total_consumption = sum(
            asset.get("consumption", 0) for asset in assets
            if asset.get("type") == "consumer"
        )
        
        balance = total_production - total_consumption
        
        # 잉여/부족 지역 식별
        surplus_assets = [
            asset for asset in assets
            if asset.get("production", 0) > asset.get("consumption", 0)
        ]
        
        deficit_assets = [
            asset for asset in assets
            if asset.get("consumption", 0) > asset.get("production", 0)
        ]
        
        analysis = {
            "total_production": total_production,
            "total_consumption": total_consumption,
            "balance": balance,
            "surplus_assets": [a.get("id") for a in surplus_assets],
            "deficit_assets": [a.get("id") for a in deficit_assets],
            "recommendations": self._generate_recommendations(balance, surplus_assets, deficit_assets)
        }
        
        self.add_to_memory({
            "timestamp": data.get("timestamp"),
            "analysis": analysis
        })
        
        logger.info(f"Energy analysis completed: balance={balance}")
        return analysis
    
    def _generate_recommendations(
        self,
        balance: float,
        surplus_assets: list,
        deficit_assets: list
    ) -> list:
        """추천 사항 생성"""
        recommendations = []
        
        if balance > 0:
            recommendations.append(f"잉여 에너지 {balance:.2f} kW 사용 가능")
            if surplus_assets and deficit_assets:
                recommendations.append("P2P 에너지 거래 검토")
        elif balance < 0:
            recommendations.append(f"에너지 부족 {abs(balance):.2f} kW")
            recommendations.append("배터리 저장소 활용 검토")
        
        return recommendations




