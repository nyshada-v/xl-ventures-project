from backend.agents.base import AgentNode
from backend.agents.registry import register
from backend.config.settings import settings

@register
class SummaryAgent(AgentNode):
    """Generates actionable outreach briefs and next actions."""
    name = "summary"

    async def _execute(self, state: dict) -> dict:
        companies = state.get("final_companies", [])
        config = state.get("business_config")
        vp = config.value_proposition if config else "Modern HR/Payroll platform"

        summaries = []
        for company in companies:
            contacts = company.get("decision_makers", [])
            primary = contacts[0] if contacts else {}

            summary = {
                "company_name":     company.get("name"),
                "domain":           company.get("domain"),
                "icp_score":        company.get("icp_score"),
                "trigger":          company.get("trigger"),
                "industry":         company.get("industry"),
                "headcount":        company.get("headcount"),
                "funding_stage":    company.get("funding_stage"),
                "tech_stack":       company.get("tech_stack", []),
                "primary_contact":  primary,
                "all_contacts":     contacts,
                "outreach_angle":   self._outreach_angle(company, primary, vp),
                "next_actions":     self._next_actions(primary),
                "recommendation":   "approve",  # default — HITL can override
            }
            summaries.append(summary)

        return {
            **state,
            "summaries": summaries,
            "status": "summarized",
        }

    def _outreach_angle(self, company: dict, contact: dict, vp: str) -> str:
        trigger = company.get("trigger", "")
        name = contact.get("name", "their team")
        stack = ", ".join(company.get("tech_stack", []) or ["legacy tools"])
        return (
            f"Reach out to {name} referencing: '{trigger}'. "
            f"Position {vp} as the modern alternative to {stack}, "
            f"timed perfectly with their current growth phase."
        )

    def _next_actions(self, contact: dict) -> list:
        name = contact.get("name", "the contact")
        email = contact.get("email", "")
        linkedin = contact.get("linkedin", "")
        return [
            f"Send personalised intro email to {email}" if email else "Find verified email",
            f"Connect on LinkedIn: {linkedin}" if linkedin else "Find LinkedIn profile",
            f"Schedule discovery call with {name}",
            "Add to CRM and set 3-day follow-up reminder",
        ]