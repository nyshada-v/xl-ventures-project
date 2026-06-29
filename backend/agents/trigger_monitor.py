from backend.agents.base import AgentNode
from backend.agents.registry import register
from backend.tools.web_search import WebSearchTool
from backend.config.business_config import DEFAULT_CONFIG

@register
class TriggerMonitorAgent(AgentNode):
    """Scans web and news sources for configurable business trigger signals."""
    name = "trigger_monitor"

    def __init__(self):
        self.search = WebSearchTool()

    async def _execute(self, state: dict) -> dict:
        config = state.get("business_config", DEFAULT_CONFIG)
        keywords = config.triggers.keywords

        all_events = []
        # Search for each keyword — dedup by domain
        seen_domains = set()
        for kw in keywords[:3]:  # limit to 3 searches to save API calls
            results = await self.search.run(kw)
            for r in results:
                domain = r.get("domain", r.get("company_name", "unknown").lower().replace(" ", "") + ".com")
                if domain not in seen_domains:
                    seen_domains.add(domain)
                    all_events.append(r)

        return {
            **state,
            "trigger_events": all_events,
            "status": "triggers_found",
        }