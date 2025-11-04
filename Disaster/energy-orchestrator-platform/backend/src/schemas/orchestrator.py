from pydantic import BaseModel
from typing import Dict, Any, List

class OrchestratorResponse(BaseModel):
    analysis: Dict[str, Any]
    recommendations: List[Dict[str, Any]]

class ScenarioResponse(BaseModel):
    scenario: Dict[str, Any]
    actions: List[Dict[str, Any]]




