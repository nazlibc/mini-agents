import json
from pathlib import Path
from langchain_core.tools import tool

def _load_campaigns():
    return json.loads(Path("data/campaigns.json").read_text())

@tool
def list_campaigns() -> str:
    """List all campaigns with their ids and names."""
    campaigns = _load_campaigns()
    return "\n".join(f"{campaign['id']}: {campaign['name']}" for campaign in campaigns)

@tool
def get_campaign_stats(campaign_id: str) -> str:
    """Get weeks, participation rate and average weekly spend for one campaign by its id."""
    for c in _load_campaigns():
        if c["id"] == campaign_id:
            return (f'{c["name"]}: {c["weeks"]} weeks, '
                    f'{c["participation_rate"]:.0%} participation, '
                    f'€{c["avg_weekly_spend"]:.2f} avg weekly spend')
    return f"No campaign with id {campaign_id}. Use list_campaigns to see valid ids."

@tool
def forecast_participation(campaign_id: str, extra_weeks: int) -> str:
    """Forecast the participation rate if a campaign ran extra_weeks longer."""
    for c in _load_campaigns():
        if c["id"] == campaign_id:
            rate = min(1.0, c["participation_rate"] * (1 + 0.02 * extra_weeks))
            return f'Forecast for {c["name"]} +{extra_weeks} weeks: {rate:.0%} participation'
    return f"No campaign with id {campaign_id}."

TOOL_REGISTRY = {
    "list_campaigns": list_campaigns,
    "get_campaign_stats": get_campaign_stats,
    "forecast_participation": forecast_participation,
}

def get_tools_by_name(names: list[str]) -> list:
    return [TOOL_REGISTRY[n] for n in names]