from datetime import date, timedelta
from mcp.server.fastmcp import FastMCP
import jampp.integration_configs as integration
from jampp.jampp_api_service import JamppAPIService

mcp = FastMCP(name="Jampp Report")


@mcp.tool()
def get_jampp_all_supported_clients() -> list[str]:
    """Get all supported clients for loading Jampp reports."""
    return integration.get_all_supported_clients()


@mcp.tool()
def get_jampp_reports(
    client: integration.Client,
    start_date: date,
    end_date: date,
) -> list[dict]:
    """Get Jampp reports for the client."""
    credentials = integration.get_credentials(client)
    service = JamppAPIService(credentials)
    end_date += timedelta(days=1)
    return service.load(
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
    )


async def main():
    await mcp.run_stdio_async()
