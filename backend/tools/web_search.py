import httpx
from backend.tools.base_tool import BaseTool
from backend.tools.mock_data import MOCK_TRIGGER_EVENTS
from backend.config.settings import settings

class WebSearchTool(BaseTool):

    def _has_key(self) -> bool:
        return bool(settings.SERPER_API_KEY)

    async def _real(self, query: str) -> list:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://google.serper.dev/news",
                headers={"X-API-KEY": settings.SERPER_API_KEY},
                json={"q": query, "num": 10},
                timeout=10,
            )
            data = resp.json()
            return [
                {
                    "title": item.get("title"),
                    "snippet": item.get("snippet"),
                    "source": item.get("source"),
                    "published_at": item.get("date"),
                }
                for item in data.get("news", [])
            ]

    async def _mock(self, query: str) -> list:
        # Filter mock events that loosely match the query
        results = []
        for event in MOCK_TRIGGER_EVENTS:
            if any(kw.lower() in event["signal"].lower() for kw in query.split()):
                results.append(event)
        return results or MOCK_TRIGGER_EVENTS  # always return something