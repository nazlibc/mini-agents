import re
from src.config import create_llm
from src.agents.definitions import AGENT_DEFINITIONS

ROUTER_PROMPT = """You are an agent router. Pick the best agent for the user's message.

Agents:
{agent_list}

Reply with ONLY the agent id (e.g. A01).

User message: {message}"""

def classify_agent(message: str, previous_agent_id: str|None = None) -> str:
    fallback = previous_agent_id or "A01"
    try:
        agent_list = "\n".join(f"{d.agent_id}: {d.description}" for d in AGENT_DEFINITIONS.values())
        prompt = ROUTER_PROMPT.format(agent_list=agent_list, message=message)
        llm = create_llm("gpt-4o-mini")
        reply = llm.invoke(prompt)
        match = re.search(r"A\d\d", reply.content)
        if match and match.group() in AGENT_DEFINITIONS:
            return match.group()
    except Exception:
        pass
    return fallback