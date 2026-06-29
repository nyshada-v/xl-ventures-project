from backend.agents.base import AgentNode
from backend.agents.registry import register
from backend.tools.company_data import CompanyDataTool
from backend.tools.mock_data import MOCK_ICP_SCORES
from backend.config.business_config import DEFAULT_CONFIG, ICPConfig

@register
class ICPMatcherAgent(AgentNode):
    """Scores companies against ICP rules and filters below threshold."""
    name = "icp_matcher"

    def __init__(self):
        self.company_tool = CompanyDataTool()

    def _score(self, company: dict, icp: ICPConfig) -> float:
        score = 0.0
        weights = {
            "industry":      0.25,
            "headcount":     0.25,
            "funding_stage": 0.25,
            "tech_stack":    0.15,
            "country":       0.10,
        }

        # Industry match
        industry = company.get("industry", "")
        if any(i.lower() in industry.lower() for i in icp.industries):
            score += weights["industry"]

        # Headcount in range
        hc = company.get("headcount") or 0
        if icp.min_headcount <= hc <= icp.max_headcount:
            score += weights["headcount"]

        # Funding stage
        stage = company.get("funding_stage", "")
        if stage in icp.funding_stages:
            score += weights["funding_stage"]

        # Tech stack signals (using legacy tools = opportunity)
        stack = company.get("tech_stack", [])
        if any(t in stack for t in icp.tech_stack_signals):
            score += weights["tech_stack"]

        # Country
        country = company.get("country", "")
        if country in icp.countries:
            score += weights["country"]

        return round(score, 2)

    async def _execute(self, state: dict) -> dict:
        config = state.get("business_config", DEFAULT_CONFIG)
        events = state.get("trigger_events", [])
        threshold = config.icp.score_threshold

        qualified = []
        for event in events:
            domain = event.get("domain", "")
            company = await self.company_tool.run(domain)
            company["domain"] = domain
            company["trigger"] = event.get("signal", "")

            # Score — use mock scores if available, else compute
            score = MOCK_ICP_SCORES.get(domain) or self._score(company, config.icp)
            company["icp_score"] = score

            if score >= threshold:
                qualified.append(company)

        # Sort by score descending
        qualified.sort(key=lambda x: x["icp_score"], reverse=True)

        return {
            **state,
            "qualified_companies": qualified,
            "status": "icp_matched",
        }