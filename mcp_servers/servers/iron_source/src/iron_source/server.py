from datetime import date, timedelta
from mcp.server.fastmcp import FastMCP
from iron_source.iron_source_api import IronSourceAPI

mcp = FastMCP(name="Iron Source Report")
api = IronSourceAPI()

@mcp.tool()
def fetch_reports(start_date: date, end_date: date, campaign_ids: list[str]) -> list[dict]:
    """Fetch reports for specific campaign IDs."""
    return api.fetch_reports(
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        campaign_ids=campaign_ids
    )

@mcp.tool()
def fetch_reports_by_bundleids(start_date: date, end_date: date, bundle_ids: list[str]) -> list[dict]:
    """Fetch reports for specific bundle IDs."""
    return api.fetch_reports_by_bundleids(
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        bundle_ids=bundle_ids
    )

@mcp.tool()
def fetch_all_reports(start_date: date, end_date: date) -> list[dict]:
    """Fetch all reports without filtering."""
    return api.fetch_all_reports(
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
    )

async def main():
    """Run the Iron Source MCP server."""
    await mcp.run_stdio_async()
