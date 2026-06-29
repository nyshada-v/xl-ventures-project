import httpx
from backend.tools.base_tool import BaseTool
from backend.tools.mock_data import MOCK_COMPANY_DATA, MOCK_ICP_SCORES
from backend.config.settings import settings

class CompanyDataTool(BaseTool):

    def _has_key(self) -> bool:
        return bool(settings.APOLLO_API_KEY)

    async def _real(self, domain: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.apollo.io/v1/organizations/enrich",
                headers={"Content-Type": "application/json"},
                json={"api_key": settings.APOLLO_API_KEY, "domain": domain},
                timeout=10,
            )
            org = resp.json().get("organization", {})
            return {
                "name": org.get("name"),
                "industry": org.get("industry"),
                "headcount": org.get("estimated_num_employees"),
                "funding_stage": org.get("latest_funding_stage"),
                "country": org.get("country"),
                "description": org.get("short_description"),
                "tech_stack": [t.get("name") for t in org.get("technologies", [])],
                "linkedin_url": org.get("linkedin_url"),
            }

    async def _mock(self, domain: str) -> dict:
        return MOCK_COMPANY_DATA.get(domain, {
            "name": domain.split(".")[0].title(),
            "industry": "SaaS",
            "headcount": 150,
            "funding_stage": "Series B",
            "country": "US",
            "description": "A fast-growing B2B software company.",
            "tech_stack": ["ADP"],
            "linkedin_url": f"https://linkedin.com/company/{domain.split('.')[0]}",
        })