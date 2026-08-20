import json
from pathlib import Path
from langchain_core.tools import tool

def _load_campaigns():
    return json.loads(Path("data/campaigns.json").read_text())

@tool
def list_campaigns() -> str:
    """List all campaigns with their ids and names."""
    campaigns = _load_campaigns()
    return [f"{campaign['id']}: {campaign['name']}" for campaign in campaigns]

@tool
def get_campaign_stats(campaign_id: str) -> str:
    """Get statistics for a specific campaign."""
    campaigns = _load_campaigns()
    campaign = next((c for c in campaigns if c['id'] == campaign_id), None)
    if not campaign:
        return f"Campaign with id {campaign_id} not found. Use list_campaigns to see valid ids."
    
    stats = campaign.get('stats', {})
    return f"Stats for campaign '{campaign['name']}' (ID: {campaign_id}): {stats}"

@tool
def forecast_participation(campaign_id: str, extra_weeks: int) -> str:
    """Forecast the participation rate if a campaign ran extra_weeks longer."""
    campaigns = _load_campaigns()
    campaign = next((c for c in campaigns if c['id'] == campaign_id), None)
    if not campaign:
        return f"Campaign with id {campaign_id} not found. Use list_campaigns to see valid ids."
    
    # Placeholder for actual forecasting logic
    forecasted_participation = 1000  # Example static value
    return f"Forecasted participation for campaign '{campaign['name']}' (ID: {campaign_id}) is {forecasted_participation} participants."

TOOL_REGISTRY = {
    "list_campaigns": list_campaigns,
    "get_campaign_stats": get_campaign_stats,
    "forecast_participation": forecast_participation,
}

def get_tool_by_names(names: list[str]) -> list:
    return [TOOL_REGISTRY[n] for n in names]