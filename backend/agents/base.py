from abc import ABC, abstractmethod
from typing import Any
import logging

logger = logging.getLogger(__name__)

class AgentNode(ABC):
    """
    Every agent inherits this.
    Input and output are plain dicts — passed through LangGraph state.
    """
    name: str = "base_agent"

    async def run(self, state: dict) -> dict:
        logger.info(f"[{self.name}] starting")
        try:
            result = await self._execute(state)
            logger.info(f"[{self.name}] done")
            return result
        except Exception as e:
            logger.error(f"[{self.name}] failed: {e}")
            return {**state, "error": str(e), "failed_agent": self.name}

    @abstractmethod
    async def _execute(self, state: dict) -> dict:
        pass