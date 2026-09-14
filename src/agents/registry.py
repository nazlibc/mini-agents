from src.agents.base import BaseAgent
from src.agents.definitions import AGENT_DEFINITIONS

_cache: dict[str, BaseAgent] = {}

def get_agent(agent_id: str) -> BaseAgent:
    """Return a live agent by its id, creating it if necessary."""
    if agent_id not in AGENT_DEFINITIONS:
        valid = ", ".join(AGENT_DEFINITIONS)
        raise ValueError(f"Unknown agent '{agent_id}'. Valid agents: {valid}")
    if agent_id not in _cache:
        defn = AGENT_DEFINITIONS[agent_id]
        _cache[agent_id] = BaseAgent(defn)
    return _cache[agent_id]