from fastapi import APIRouter
from backend.config.business_config import BusinessConfig, DEFAULT_CONFIG
from backend.memory.working_memory import set_key, get_key
from backend.memory.db import SessionLocal, Company, Contact, AgentRun

router = APIRouter()

@router.get("/")
async def get_config():
    """Return current business config."""
    saved = get_key("business_config")
    if saved:
        return saved
    return DEFAULT_CONFIG.model_dump()

@router.post("/")
async def update_config(config: BusinessConfig):
    """Update ICP, persona, and trigger config."""
    set_key("business_config", config.model_dump())
    return {"status": "updated", "config": config.model_dump()}

@router.get("/leads")
async def get_leads():
    """Return all saved leads from DB."""
    from backend.memory.db import SessionLocal, Company, Contact
    db = SessionLocal()
    try:
        companies = db.query(Company).order_by(Company.icp_score.desc()).all()
        result = []
        for c in companies:
            contacts = db.query(Contact).filter(Contact.company_id == c.id).all()
            result.append({
                "id":           c.id,
                "name":         c.name,
                "domain":       c.domain,
                "industry":     c.industry,
                "headcount":    c.headcount,
                "funding_stage": c.funding_stage,
                "icp_score":    c.icp_score,
                "trigger":      c.trigger,
                "contacts": [
                    {
                        "name":     ct.name,
                        "title":    ct.title,
                        "email":    ct.email,
                        "phone":    ct.phone,
                        "linkedin": ct.linkedin,
                    }
                    for ct in contacts
                ],
            })
        return result
    finally:
        db.close()
@router.get("/stats")
async def get_stats():
    db = SessionLocal()
    try:
        from sqlalchemy import func
        total_runs     = db.query(AgentRun).count()
        completed_runs = db.query(AgentRun).filter(AgentRun.status == "done").count()
        total_leads    = db.query(Company).count()
        total_contacts = db.query(Contact).count()
        companies      = db.query(Company).all()
        scores         = [c.icp_score for c in companies if c.icp_score is not None]
        avg_score      = round(sum(scores) / len(scores), 2) if scores else 0
        active_domain  = get_key("active_domain") or "hr_saas"
        return {
            "total_runs":     total_runs,
            "completed_runs": completed_runs,
            "total_leads":    total_leads,
            "total_contacts": total_contacts,
            "avg_icp_score":  avg_score,
            "active_domain":  active_domain,
        }
    except Exception as e:
        return {
            "total_runs": 0, "completed_runs": 0,
            "total_leads": 0, "total_contacts": 0,
            "avg_icp_score": 0, "active_domain": "hr_saas",
            "error": str(e)
        }
    finally:
        db.close()