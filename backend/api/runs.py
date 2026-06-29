import uuid
import asyncio
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import AsyncGenerator
import json

from backend.memory.db import get_db, AgentRun
from backend.memory.working_memory import set_key, get_key
from backend.agents.trigger_monitor import TriggerMonitorAgent
from backend.agents.icp_matcher import ICPMatcherAgent
from backend.agents.enrichment import EnrichmentAgent
from backend.agents.persona import PersonaAgent
from backend.agents.contact_enrichment import ContactEnrichmentAgent
from backend.config.business_config import DEFAULT_CONFIG

router = APIRouter()

# Agent instances
_trigger  = TriggerMonitorAgent()
_icp      = ICPMatcherAgent()
_enrich   = EnrichmentAgent()
_persona  = PersonaAgent()
_contacts = ContactEnrichmentAgent()

# SSE queues keyed by run_id
_sse_queues: dict = {}

async def _stream_events(run_id: str) -> AsyncGenerator[str, None]:
    queue = asyncio.Queue()
    _sse_queues[run_id] = queue
    try:
        while True:
            event = await asyncio.wait_for(queue.get(), timeout=120.0)
            if event == "__done__":
                break
            yield f"data: {json.dumps(event)}\n\n"
    except asyncio.TimeoutError:
        yield f"data: {json.dumps({'type': 'timeout'})}\n\n"
    finally:
        _sse_queues.pop(run_id, None)

async def _emit(run_id: str, event: dict):
    q = _sse_queues.get(run_id)
    if q:
        await q.put(event)

async def _execute_run(run_id: str, db: Session):
    try:
        # Mark running
        run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
        run.status = "running"
        db.commit()

        await _emit(run_id, {"type": "status", "message": "Pipeline started"})

        state = {
            "run_id": run_id,
            "business_config": DEFAULT_CONFIG,
            "hitl_decisions": {},
        }

        # Step 1 — Trigger Monitor
        await _emit(run_id, {"type": "agent", "agent": "trigger_monitor",
                              "message": "Scanning web for trigger signals..."})
        state = await _trigger.run(state)
        triggers = state.get("trigger_events", [])
        await _emit(run_id, {"type": "agent", "agent": "trigger_monitor",
                              "message": f"Found {len(triggers)} trigger events"})

        # Step 2 — ICP Matcher
        await _emit(run_id, {"type": "agent", "agent": "icp_matcher",
                              "message": "Scoring companies against ICP..."})
        state = await _icp.run(state)
        qualified = state.get("qualified_companies", [])
        await _emit(run_id, {"type": "agent", "agent": "icp_matcher",
                              "message": f"{len(qualified)} companies qualified"})

        if not qualified:
            run.status = "done"
            run.results = {"summaries": [], "message": "No companies matched ICP"}
            db.commit()
            await _emit(run_id, {"type": "done", "message": "No matches found"})
            await _sse_queues[run_id].put("__done__")
            return

        # Step 3 — Enrichment
        await _emit(run_id, {"type": "agent", "agent": "enrichment",
                              "message": "Enriching company data..."})
        state = await _enrich.run(state)

        # Step 4 — Persona
        await _emit(run_id, {"type": "agent", "agent": "persona",
                              "message": "Finding decision makers..."})
        state = await _persona.run(state)

        # Step 5 — Contact Enrichment
        await _emit(run_id, {"type": "agent", "agent": "contact_enrichment",
                              "message": "Enriching contact details..."})
        state = await _contacts.run(state)

        # Save state for HITL resume
        final_companies = state.get("final_companies", [])
        set_key(f"run_state:{run_id}", {"final_companies": final_companies})

        run.status = "hitl_wait"
        run.results = {"final_companies": final_companies}
        db.commit()

        await _emit(run_id, {
            "type": "hitl",
            "message": "Awaiting your approval",
            "companies": [
                {
                    "domain":    c.get("domain"),
                    "name":      c.get("name"),
                    "icp_score": c.get("icp_score"),
                    "trigger":   c.get("trigger"),
                    "headcount": c.get("headcount"),
                    "industry":  c.get("industry"),
                    "contacts":  c.get("decision_makers", []),
                }
                for c in final_companies
            ],
        })

    except Exception as e:
        run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
        run.status = "failed"
        run.error = str(e)
        db.commit()
        await _emit(run_id, {"type": "error", "message": str(e)})

    finally:
        q = _sse_queues.get(run_id)
        if q:
            await q.put("__done__")


@router.post("/start")
async def start_run(db: Session = Depends(get_db)):
    run_id = str(uuid.uuid4())
    run = AgentRun(id=run_id, status="pending")
    db.add(run)
    db.commit()
    asyncio.create_task(_execute_run(run_id, db))
    return {"run_id": run_id, "status": "started"}


@router.get("/stream/{run_id}")
async def stream_run(run_id: str):
    return StreamingResponse(
        _stream_events(run_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control":    "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/")
async def list_runs(db: Session = Depends(get_db)):
    runs = db.query(AgentRun).order_by(AgentRun.created_at.desc()).limit(20).all()
    return [
        {
            "id":         r.id,
            "status":     r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "error":      r.error,
        }
        for r in runs
    ]


@router.get("/{run_id}")
async def get_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        return {"error": "Run not found"}
    return {
        "id":         run.id,
        "status":     run.status,
        "results":    run.results,
        "error":      run.error,
        "created_at": run.created_at.isoformat() if run.created_at else None,
    }