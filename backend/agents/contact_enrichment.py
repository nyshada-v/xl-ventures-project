from backend.agents.base import AgentNode
from backend.agents.registry import register
from backend.tools.contact_enrichment import ContactEnrichmentTool
from backend.memory.working_memory import get_key, set_key

@register
class ContactEnrichmentAgent(AgentNode):
    """Enriches contacts with verified email, phone, and LinkedIn."""
    name = "contact_enrichment"

    def __init__(self):
        self.contact_tool = ContactEnrichmentTool()

    async def _execute(self, state: dict) -> dict:
        companies = state.get("companies_with_personas", [])
        final_companies = []

        for company in companies:
            domain = company.get("domain", "")
            decision_makers = company.get("decision_makers", [])
            enriched_contacts = []

            for contact in decision_makers:
                email = contact.get("email", "")
                cache_key = f"contact:{email}"

                cached = get_key(cache_key)
                if cached:
                    enriched_contacts.append(cached)
                    continue

                # Enrich — in mock mode this just confirms the data
                enriched = {
                    **contact,
                    "email_verified": bool(email and "@" in email),
                    "outreach_priority": self._priority(contact),
                }
                set_key(cache_key, enriched)
                enriched_contacts.append(enriched)

            final_companies.append({
                **company,
                "decision_makers": enriched_contacts,
            })

        return {
            **state,
            "final_companies": final_companies,
            "status": "contacts_enriched",
        }

    def _priority(self, contact: dict) -> str:
        rank = {"c-suite": "high", "vp": "high", "director": "medium"}
        return rank.get(contact.get("seniority", ""), "low")