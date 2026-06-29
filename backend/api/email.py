from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
import uuid

from backend.memory.db import get_db, SentEmail, SessionLocal
from backend.agents.email_outreach import EmailOutreachAgent

router = APIRouter()
_email_agent = EmailOutreachAgent()


class EmailRequest(BaseModel):
    summaries: list


class SingleEmailRequest(BaseModel):
    contact_name:  str
    contact_email: str
    company_name:  str
    trigger:       str
    tech_stack:    List[str] = []
    outreach_angle: str = ""


@router.post("/send-bulk")
async def send_bulk(payload: EmailRequest, db: Session = Depends(get_db)):
    """Send outreach emails to all contacts in approved summaries."""
    state  = {"summaries": payload.summaries}
    result = await _email_agent.run(state)
    emails = result.get("email_results", [])

    # Persist to DB
    for e in emails:
        db.add(SentEmail(
            id            = str(uuid.uuid4()),
            contact_email = e.get("contact_email"),
            contact_name  = e.get("contact_name"),
            subject       = e.get("subject"),
            body          = e.get("body"),
            status        = e.get("status"),
            error         = e.get("error"),
        ))
    db.commit()
    return {"status": "done", "results": emails}


@router.post("/send-single")
async def send_single(payload: SingleEmailRequest, db: Session = Depends(get_db)):
    """Send a single outreach email to one contact."""
    state = {
        "summaries": [{
            "company_name":  payload.company_name,
            "trigger":       payload.trigger,
            "tech_stack":    payload.tech_stack,
            "outreach_angle": payload.outreach_angle,
            "all_contacts":  [{
                "name":  payload.contact_name,
                "email": payload.contact_email,
            }],
        }]
    }
    result = await _email_agent.run(state)
    emails = result.get("email_results", [])

    if emails:
        e = emails[0]
        db.add(SentEmail(
            id            = str(uuid.uuid4()),
            contact_email = e.get("contact_email"),
            contact_name  = e.get("contact_name"),
            subject       = e.get("subject"),
            body          = e.get("body"),
            status        = e.get("status"),
            error         = e.get("error"),
        ))
        db.commit()
        return {"status": "done", "result": e}

    return {"status": "failed", "message": "No valid contacts"}


@router.get("/history")
async def email_history():
    """Return all sent emails."""
    db = SessionLocal()
    try:
        emails = db.query(SentEmail).order_by(SentEmail.created_at.desc()).limit(50).all()
        return [
            {
                "id":            e.id,
                "contact_name":  e.contact_name,
                "contact_email": e.contact_email,
                "subject":       e.subject,
                "body":          e.body,
                "status":        e.status,
                "error":         e.error,
                "sent_at":       e.created_at.isoformat() if e.created_at else None,
            }
            for e in emails
        ]
    finally:
        db.close()