from datetime import date

from mcp.server.fastmcp import FastMCP

from inmobi.inmobi_api_service import InmobiAPIService
from inmobi.integration_configs import get_access_config

mcp = FastMCP(name="Inmobi Partner Report")


@mcp.prompt()
def inmobi_partner_report():
    """Run the Inmobi Partner Report tool."""
    return """
# Inmobi Partner Report Assistant

I'm your dedicated assistant for retrieving and analyzing Inmobi Partner Reports. I'll guide you through the process step-by-step to ensure you get the data you need.

## How I Can Help You:
- Generate Inmobi report IDs for any date range you specify
- Check the status of your requested reports
- Retrieve and present campaign data once reports are available

## Working Process:
1. First, I'll ask you for your desired date range (start date and end date)
2. I'll generate the necessary report IDs using the `generate_inmobi_report_ids` tool
3. I'll check the report status using the `check_inmobi_report_status` tool
4. When reports are ready (status: "report.status.available"), I'll load the data using `load_inmobi_campaign_reports`

## Important Notes:
- Report generation typically takes at least 5 minutes
- I'll provide status updates while your report is being processed
- Both SKAN and non-SKAN data will be included in your report
- You can ask me questions about the report data once it's loaded

How would you like to proceed? Please provide your desired date range in YYYY-MM-DD format.
"""


@mcp.tool()
def generate_inmobi_report_ids(start_date: date, end_date: date) -> list[str]:
    """
    Generate Inmobi report IDs for both SKAN and non-SKAN data within the specified date range.

    This initiates the report generation process on Inmobi's servers. The returned IDs should be
    saved as they'll be needed to check status and retrieve the reports later.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        List containing two report IDs: [skan_report_id, non_skan_report_id]
    """
    return InmobiAPIService(get_access_config()).get_report_ids(
        start_date=start_date.isoformat(), end_date=end_date.isoformat()
    )


@mcp.tool()
def check_inmobi_report_status(report_id: str) -> str:
    """
    Check the current processing status of an Inmobi report.

    Reports typically take at least 5 minutes to generate. Possible statuses include:
    - "report.status.available": The report ran successfully and is available to download
    - "report.status.running": The report generation is in process
    - "report.status.submitted": Query successfully submitted by the user
    - "report.status.failed": Query failed

    If status is not "report.status.available", wait at least 5 minutes before checking again.
    Both SKAN and non-SKAN report statuses must be checked separately using their respective IDs.

    Args:
        report_id: The ID of the report to check

    Returns:
        The status of the report
    """
    return InmobiAPIService(get_access_config()).check_report_status_once(report_id)


@mcp.tool()
def load_inmobi_campaign_reports(
    report_id: str,
) -> str:
    """
    Download and process campaign data from InMobi when report is ready.

    IMPORTANT: Only call this function when report status is "report.status.available".
    The result is in CSV format.
    """
    return InmobiAPIService(get_access_config()).load(
        report_id=report_id,
    )


async def main():
    await mcp.run_stdio_async()
