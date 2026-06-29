import httpx
from backend.tools.base_tool import BaseTool
from backend.tools.mock_data import MOCK_CONTACTS
from backend.config.settings import settings

class ContactEnrichmentTool(BaseTool):

    def _has_key(self) -> bool:
        return bool(settings.HUNTER_API_KEY)

    async def _real(self, domain: str, titles: list) -> list:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.hunter.io/v2/domain-search",
                params={
                    "domain": domain,
                    "api_key": settings.HUNTER_API_KEY,
                    "limit": 10,
                },
                timeout=10,
            )
            data = resp.json().get("data", {})
            contacts = []
            for person in data.get("emails", []):
                title = person.get("position", "")
                if any(t.lower() in title.lower() for t in titles):
                    contacts.append({
                        "name": f"{person.get('first_name', '')} {person.get('last_name', '')}".strip(),
                        "title": title,
                        "email": person.get("value"),
                        "phone": None,
                        "linkedin": person.get("linkedin"),
                        "seniority": person.get("seniority"),
                    })
            return contacts

    async def _mock(self, domain: str, titles: list) -> list:
        return MOCK_CONTACTS.get(domain, [
            {
                "name": "Alex Rivera",
                "title": "Head of HR",
                "email": f"a.rivera@{domain}",
                "phone": "+1-555-000-0000",
                "linkedin": f"linkedin.com/in/alexrivera",
                "seniority": "director",
            }
        ])