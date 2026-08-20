from src.agents.base import AgentDefinition, run_agent

ANALYST = AgentDefinition(
    agent_id="A01",
    name="Campaign Analyst",
    description="Answers questions about campaign performance and forecasts.",
    system_prompt="You are a concise loyalty-campaign analyst. "
                  "Use your tools to look up real data before answering.",
    tool_names=["list_campaigns", "get_campaign_stats", "forecast_participation"],
)

while True:
    q = input("\nyou> ")
    if q in ("q", "exit"):break
    print("bot>", run_agent(ANALYST, q))


# “Which campaigns are there?” — one tool call.
# “What's the participation of Winter Loyalty?” — watch it chain list_campaigns → get_campaign_stats, because you gave it a name, not an id. Nobody programmed that chain — that's the loop + good docstrings.
# “What would 4 more weeks do to it?” — note it fails to remember context! Each run_agent call starts fresh. Sessions come later — for now, ask it in one sentence.