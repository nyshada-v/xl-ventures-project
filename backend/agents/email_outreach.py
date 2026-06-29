from backend.agents.base import AgentNode
from backend.agents.registry import register
from backend.tools.email_sender import EmailSenderTool


@register
class EmailOutreachAgent(AgentNode):
    """Sends personalised outreach emails to approved decision makers."""
    name = "email_outreach"

    def __init__(self):
        self.sender = EmailSenderTool()

    def _generate_email(self, contact: dict, company: dict, outreach_angle: str) -> dict:
        name       = contact.get("name", "there")
        first_name = name.split()[0] if name else "there"
        title      = contact.get("title", "")
        co_name    = company.get("company_name") or company.get("name", "your company")
        trigger    = company.get("trigger", "")
        stack      = ", ".join(company.get("tech_stack", []) or ["your current tools"])

        subject = f"Modernising HR & Payroll at {co_name}"

        body = f"""Hi {first_name},

I noticed {trigger.lower() if trigger else f'{co_name} is going through an exciting growth phase'} — congratulations!

Fast-growing companies at this stage often find that legacy tools like {stack} start to slow them down. We help companies like {co_name} replace them with a modern, unified HR and payroll platform that scales with you.

I'd love to show you what we've built in a quick 20-minute call — would any time this week work for you?

Best,
AgentIQ Sales Team

P.S. Companies similar to {co_name} typically cut payroll processing time by 60% in the first 90 days.
"""
        return {"subject": subject, "body": body}

    async def _execute(self, state: dict) -> dict:
        # Works on summaries (post-HITL) or final_companies
        targets = state.get("summaries") or state.get("email_targets", [])
        results = []

        for item in targets:
            contacts   = item.get("all_contacts") or item.get("decision_makers", [])
            angle      = item.get("outreach_angle", "")
            company    = item

            for contact in contacts:
                to_email = contact.get("email", "")
                if not to_email or "@" not in to_email:
                    continue

                email_content = self._generate_email(contact, company, angle)
                result        = self.sender.send(
                    to_email = to_email,
                    subject  = email_content["subject"],
                    body     = email_content["body"],
                )
                results.append({
                    "contact_name":  contact.get("name"),
                    "contact_email": to_email,
                    "company":       item.get("company_name") or item.get("name"),
                    "subject":       email_content["subject"],
                    "body":          email_content["body"],
                    "status":        result.get("status"),
                    "error":         result.get("error"),
                })

        return {
            **state,
            "email_results": results,
            "status": "emails_sent",
        }