
from src.agents.registry import get_agent
from src.agents.router import classify_agent

current = None

while True:
    q = input("\nyou> ")
    if q in ("q", "exit"): break

    current = classify_agent(q, previous_agent_id=  current)
    print(f"→ routing to {current}")
    for kind, data in get_agent(current).stream_chat(q):
        if kind == "tool_call":
            print(f"  → {data['name']}({data['args']})")
        elif kind == "response":
            print("bot>", data)