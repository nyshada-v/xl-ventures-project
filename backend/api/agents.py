from fastapi import APIRouter

# Import all agent modules so @register decorators fire
from backend.agents import trigger_monitor  # noqa
from backend.agents import icp_matcher      # noqa
from backend.agents import enrichment       # noqa
from backend.agents import persona          # noqa
from backend.agents import contact_enrichment  # noqa
from backend.agents import summary          # noqa

from backend.agents.registry import list_agents

router = APIRouter()

@router.get("/")
async def get_agents():
    """Returns all registered agents."""
    agents = list_agents()
    return agents