from src.agents.base import AgentDefinition

ANALYST = AgentDefinition(
    agent_id="A01",
    name="Campaign Analyst",
    description="Answers questions about campaign performance and forecasts.",
    system_prompt="You are a concise loyalty-campaign analyst. "
                "Use your tools to look up real data before answering.",
    tool_names=["list_campaigns", "get_campaign_stats", ],
)

FORECASTER = AgentDefinition(
    agent_id="A02",
    name="Campaign Forecaster",
    description="Forecasts the participation rate of campaigns.",
    system_prompt="You are a concise loyalty-campaign forecaster. "
                "Use your tools to look up real data before answering."
                "Always ground forecasts in tool output",
    tool_names=["list_campaigns", "forecast_participation"],
)

GENERAL = AgentDefinition(
    agent_id="A99",
    name="General Assistant",
    description="General questions and anything not covered by the other agents.",
    system_prompt="You are a friendly, concise assistant.",
    tool_names=[],
)

AGENT_DEFINITIONS = {
    d.agent_id: d for d in [ANALYST, FORECASTER, GENERAL]
}

"Note the tool subsets: the analyst can't forecast, the forecaster can't fetch stats. "
"That's deliberate — it makes routing mistakes visible (the wrong agent will say it can't help), "
"which is how you'll debug your descriptions."

# go The registry — definitions become live agents, in src/agents/registry.py, 
# which is imported by the router. The router doesn't care about the definitions themselves, 
# just the agent_id and name.