from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """AI 에이전트 기본 클래스"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.memory = []
        logger.info(f"Initialized agent: {agent_name}")
    
    @abstractmethod
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터 분석 (각 에이전트가 구현)"""
        pass
    
    def add_to_memory(self, item: Dict[str, Any]):
        """메모리에 추가"""
        self.memory.append(item)
        # 메모리 크기 제한 (최근 50개만 유지)
        if len(self.memory) > 50:
            self.memory = self.memory[-50:]
    
    def get_context(self) -> str:
        """컨텍스트 반환"""
        return "\n".join([str(m) for m in self.memory[-10:]])




