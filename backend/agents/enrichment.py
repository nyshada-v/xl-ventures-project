from backend.agents.base import AgentNode
from backend.agents.registry import register
from backend.tools.company_data import CompanyDataTool
from backend.memory.working_memory import get_key, set_key

@register
class EnrichmentAgent(AgentNode):
    """Enriches company data and deduplicates via working memory."""
    name = "enrichment"

    def __init__(self):
        self.company_tool = CompanyDataTool()

    async def _execute(self, state: dict) -> dict:
        companies = state.get("qualified_companies", [])
        enriched = []

        for company in companies:
            domain = company.get("domain", "")

            # Check working memory — skip if already enriched this run
            cached = get_key(f"enriched:{domain}")
            if cached:
                enriched.append(cached)
                continue

            # Pull fresh data and merge
            fresh = await self.company_tool.run(domain)
            merged = {**fresh, **company}  # trigger data wins over fresh

            # Fill missing fields with defaults
            merged.setdefault("employees_growth", "unknown")
            merged.setdefault("founded_year", "unknown")

            set_key(f"enriched:{domain}", merged)
            enriched.append(merged)

        return {
            **state,
            "enriched_companies": enriched,
            "status": "enriched",
        }