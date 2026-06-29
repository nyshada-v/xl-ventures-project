from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict

from backend.memory.db import get_db, AgentRun, HitlDecision, Company, Contact
from backend.memory.working_memory import get_key, set_key
from backend.agents.summary import SummaryAgent
from backend.config.business_config import DEFAULT_CONFIG
import uuid

router = APIRouter()

class HitlPayload(BaseModel):
    decisions: Dict[str, str]  # {domain: "approved"/"rejected"}
    notes: Dict[str, str] = {}  # {domain: "optional note"}

_summary_agent = SummaryAgent()

@router.post("/{run_id}/decide")
async def submit_decision(
    run_id: str,
    payload: HitlPayload,
    db: Session = Depends(get_db),
):
    """User submits approve/reject decisions. Resumes pipeline."""
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        return {"error": "Run not found"}
    if run.status != "hitl_wait":
        return {"error": f"Run is not awaiting HITL. Status: {run.status}"}

    # Save decisions
    for domain, decision in payload.decisions.items():
        db.add(HitlDecision(
            id=str(uuid.uuid4()),
            run_id=run_id,
            company_id=domain,
            decision=decision,
            notes=payload.notes.get(domain, ""),
        ))
    db.commit()

    # Load saved state and filter to approved only
    saved = get_key(f"run_state:{run_id}") or {}
    all_companies = saved.get("final_companies", run.results.get("final_companies", []))
    approved = [
        c for c in all_companies
        if payload.decisions.get(c.get("domain")) == "approved"
    ]

    if not approved:
        run.status = "done"
        run.results = {**run.results, "summaries": [], "message": "All leads rejected"}
        db.commit()
        return {"status": "done", "summaries": []}

    # Run summary agent on approved companies
    state = {
        "final_companies": approved,
        "business_config": DEFAULT_CONFIG,
        "hitl_decisions": payload.decisions,
    }
    result = await _summary_agent.run(state)
    summaries = result.get("summaries", [])

    # Persist to DB
    for s in summaries:
        domain = s.get("domain")
        existing = db.query(Company).filter(Company.domain == domain).first()
        if not existing:
            company = Company(
                id=str(uuid.uuid4()),
                name=s.get("company_name"),
                domain=domain,
                industry=s.get("industry"),
                headcount=s.get("headcount"),
                funding_stage=s.get("funding_stage"),
                icp_score=s.get("icp_score"),
                trigger=s.get("trigger"),
                raw_data=s,
            )
            db.add(company)
            db.flush()
            company_id = company.id
        else:
            company_id = existing.id

        for contact in s.get("all_contacts", []):
            db.add(Contact(
                id=str(uuid.uuid4()),
                company_id=company_id,
                name=contact.get("name"),
                title=contact.get("title"),
                email=contact.get("email"),
                phone=contact.get("phone"),
                linkedin=contact.get("linkedin"),
                seniority=contact.get("seniority"),
                raw_data=contact,
            ))

    run.status = "done"
    run.results = {**run.results, "summaries": summaries}
    db.commit()

    return {"status": "done", "summaries": summaries}