from langgraph.graph import StateGraph, END
from typing import TypedDict, Any, Optional
from backend.agents.trigger_monitor import TriggerMonitorAgent
from backend.agents.icp_matcher import ICPMatcherAgent
from backend.agents.enrichment import EnrichmentAgent
from backend.agents.persona import PersonaAgent
from backend.agents.contact_enrichment import ContactEnrichmentAgent
from backend.agents.summary import SummaryAgent
from backend.memory.working_memory import set_key, get_key

# ── State schema ──────────────────────────────────────────────────────────────
class PlanState(TypedDict, total=False):
    run_id:                 str
    business_config:        Any
    trigger_events:         list
    qualified_companies:    list
    enriched_companies:     list
    companies_with_personas: list
    final_companies:        list
    summaries:              list
    hitl_decisions:         dict
    status:                 str
    error:                  Optional[str]
    failed_agent:           Optional[str]

# ── Agent instances (singletons) ──────────────────────────────────────────────
_trigger  = TriggerMonitorAgent()
_icp      = ICPMatcherAgent()
_enrich   = EnrichmentAgent()
_persona  = PersonaAgent()
_contacts = ContactEnrichmentAgent()
_summary  = SummaryAgent()

# ── Node wrappers ─────────────────────────────────────────────────────────────
async def run_trigger(state):  return await _trigger.run(state)
async def run_icp(state):      return await _icp.run(state)
async def run_enrich(state):   return await _enrich.run(state)
async def run_persona(state):  return await _persona.run(state)
async def run_contacts(state): return await _contacts.run(state)
async def run_summary(state):  return await _summary.run(state)

# HITL node — pauses and saves state, API resumes it
async def hitl_checkpoint(state):
    run_id = state.get("run_id", "unknown")
    set_key(f"hitl_pending:{run_id}", state)
    return {**state, "status": "hitl_wait"}

# ── Routing logic ─────────────────────────────────────────────────────────────
def route_after_icp(state):
    """Skip rest of pipeline if no companies qualified."""
    if not state.get("qualified_companies"):
        return "no_results"
    return "continue"

def route_after_hitl(state):
    """Check if user approved at least one company."""
    decisions = state.get("hitl_decisions", {})
    approved = [k for k, v in decisions.items() if v == "approved"]
    return "approved" if approved else "rejected"

# ── Build the graph ───────────────────────────────────────────────────────────
def build_graph():
    g = StateGraph(PlanState)

    g.add_node("trigger_monitor",    run_trigger)
    g.add_node("icp_matcher",        run_icp)
    g.add_node("enrichment",         run_enrich)
    g.add_node("persona",            run_persona)
    g.add_node("contact_enrichment", run_contacts)
    g.add_node("hitl",               hitl_checkpoint)
    g.add_node("summary",            run_summary)

    g.set_entry_point("trigger_monitor")
    g.add_edge("trigger_monitor", "icp_matcher")

    g.add_conditional_edges(
        "icp_matcher",
        route_after_icp,
        {"continue": "enrichment", "no_results": END}
    )

    g.add_edge("enrichment",         "persona")
    g.add_edge("persona",            "contact_enrichment")
    g.add_edge("contact_enrichment", "hitl")

    g.add_conditional_edges(
        "hitl",
        route_after_hitl,
        {"approved": "summary", "rejected": END}
    )

    g.add_edge("summary", END)

    return g.compile()

# Single compiled graph instance
agent_graph = build_graph()