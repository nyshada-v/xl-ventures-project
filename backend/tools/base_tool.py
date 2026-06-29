from abc import ABC, abstractmethod
from typing import Any
from backend.config.settings import settings

class BaseTool(ABC):
    """All tools inherit this. Automatically uses mock when key is missing."""

    def __init__(self):
        self.mock_mode = settings.MOCK_MODE or not self._has_key()

    def _has_key(self) -> bool:
        return True  # override in subclasses

    async def run(self, *args, **kwargs) -> Any:
        if self.mock_mode:
            return await self._mock(*args, **kwargs)
        return await self._real(*args, **kwargs)

    @abstractmethod
    async def _real(self, *args, **kwargs) -> Any:
        pass

    @abstractmethod
    async def _mock(self, *args, **kwargs) -> Any:
        pass