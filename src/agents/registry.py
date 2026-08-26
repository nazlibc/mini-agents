from src.agents.base import BaseAgent
from src.agents.definitions import AGENT_DEFINITIONS

_cache: dict[str, BaseAgent] = {}

def get_agent(agent_id: str) -> BaseAgent:
    """Return a live agent by its id, creating it if necessary."""
    if agent_id not in _cache:
        defn = AGENT_DEFINITIONS[agent_id]
        _cache[agent_id] = BaseAgent(defn)
    return _cache[agent_id]