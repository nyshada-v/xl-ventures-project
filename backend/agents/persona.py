from backend.agents.base import AgentNode
from backend.agents.registry import register
from backend.tools.contact_enrichment import ContactEnrichmentTool
from backend.config.business_config import DEFAULT_CONFIG

@register
class PersonaAgent(AgentNode):
    """Identifies decision makers matching configured persona rules."""
    name = "persona"
    def __init__(self):
        self.contact_tool = ContactEnrichmentTool()

    async def _execute(self, state: dict) -> dict:
        config = state.get("business_config", DEFAULT_CONFIG)
        companies = state.get("enriched_companies", [])
        target_titles = config.personas.target_titles

        companies_with_personas = []
        for company in companies:
            domain = company.get("domain", "")
            contacts = await self.contact_tool.run(domain, target_titles)

            # Filter by seniority rank
            seniority_rank = {"c-suite": 3, "vp": 2, "director": 1}
            min_rank = seniority_rank.get(config.personas.min_seniority, 1)

            filtered = [
                c for c in contacts
                if seniority_rank.get(c.get("seniority", "director"), 1) >= min_rank
            ]

            companies_with_personas.append({
                **company,
                "decision_makers": filtered,
            })

        return {
            **state,
            "companies_with_personas": companies_with_personas,
            "status": "personas_found",
        }