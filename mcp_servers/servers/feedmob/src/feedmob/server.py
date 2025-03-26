from datetime import date
from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Union, Any, Optional
from .db import (
    get_db_jampp_campaign_mappings,
    get_db_net_spends,
    get_db_client_infos,
    get_db_direct_spend_job_stats
)

mcp = FastMCP(
    name="Feedmob Report",
    version="0.1.0",
    description="MCP server for Feedmob reporting data"
)


@mcp.tool()
def get_client_infos(
    client_name: str,
) -> List[Dict[str, Any]]:
    """Get detailed information about a client.

    Args:
        client_name (str): Name of the client to search for (supports partial matches)

    Returns:
        List[Dict[str, Any]]: List of client records containing:
            - id: Client ID
            - name: Client name
            - created_at: Creation timestamp
            - updated_at: Last update timestamp
            - other client-specific fields

    Raises:
        ValueError: If client_name is empty
    """
    if not client_name.strip():
        raise ValueError("client_name cannot be empty")

    return get_db_client_infos(client_name)


@mcp.tool()
def get_jampp_campaign_mappings(
    client_name: str,
    vendor_name: str,
) -> List[Dict[str, Any]]:
    """Get Jampp campaign mappings for a specific client.

    Args:
        client_name (str): Name of the client
        vendor_name (str, optional): Vendor name, defaults to "Jampp"

    Returns:
        List[Dict[str, Any]]: List of Jampp campaign mappings containing:
            - client_name: Client name
            - vendor_name: Always "Jampp"
            - campaign_id: Campaign ID in net_spends table
            - jampp_campaign_id: Campaign ID in Jampp's system
            - client_id: Client ID
            - vendor_id: Vendor ID
            - other mapping fields from the database

    Raises:
        ValueError: If client_name is empty
    """
    if not client_name.strip():
        raise ValueError("client_name cannot be empty")
    if not vendor_name.strip():
        raise ValueError("vendor_name cannot be empty")

    return get_db_jampp_campaign_mappings(client_name, vendor_name)


@mcp.tool()
def get_client_vendor_direct_spend(
    client_name: str,
    vendor_name: str,
    start_date: date,
    end_date: date,
) -> List[Dict[str, Any]]:
    """Get client vendor direct spend between two dates.

    Args:
        client_name (str): Name of the client
        vendor_name (str): Name of the vendor
        start_date (date): Start date for the report (inclusive)
        end_date (date): End date for the report (inclusive)

    Returns:
        List[Dict[str, Union[str, int, float]]]: List of spend records with dates and amounts

    Raises:
        ValueError: If any parameter is None
        ValueError: If end_date is before start_date
        ValueError: If client_name or vendor_name is empty
    """
    if client_name is None:
        raise ValueError("client_name cannot be None")
    if vendor_name is None:
        raise ValueError("vendor_name cannot be None")
    if start_date is None:
        raise ValueError("start_date cannot be None")
    if end_date is None:
        raise ValueError("end_date cannot be None")

    if not client_name.strip():
        raise ValueError("client_name cannot be empty")
    if not vendor_name.strip():
        raise ValueError("vendor_name cannot be empty")
    if end_date < start_date:
        raise ValueError("end_date cannot be before start_date")


    # Get net spends for these campaigns
    spends = get_db_net_spends(
        client_name=client_name,
        vendor_name=vendor_name,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
    )

    # Format the response
    result = []
    for spend in spends:
        result.append({
            "client_name": spend["client_name"],
            "vendor_name": spend["vendor_name"],
            "campaign_id": spend["campaign_id"],
            "campaign_name": spend["campaign_name"],
            "click_url_id": spend["click_url_id"],
            "spend_date": spend["spend_date"],
            "gross_spend": float(spend["gross_spend"]),
            "net_spend": float(spend["net_spend"])
        })

    return result


@mcp.tool()
def get_direct_spend_job_stats(
    client_ids: Optional[List[int]] = None,
    vendor_ids: Optional[List[int]] = None,
    click_url_ids: Optional[List[int]] = None,
    job: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Get direct spend job stats information. This tool is commonly used to check spend data sources
    and understand how the net_spends table is populated.

    Args:
        client_ids (List[int], optional): List of client IDs to filter by
        vendor_ids (List[int], optional): List of vendor IDs to filter by
        click_url_ids (List[int], optional): List of click URL IDs to filter by
        job (str, optional): Job name to filter by

    Returns:
        List[Dict[str, Any]]: List of direct spend job stats records containing:
            - id: Record ID
            - click_url_ids: Array of click URL IDs
            - client_ids: Array of client IDs
            - vendor_ids: Array of vendor IDs
            - status: Job status (default: 1)
            - data_source: Data source
            - job: Job name
            - notes: Job notes
            - schedule: Job schedule
            - pm_users: Array of PM users
            - pa_users: Array of PA users
            - created_at: Creation timestamp
            - updated_at: Last update timestamp
            - deleted_at: Deletion timestamp (null if not deleted)
            - gross_spend_source: Source system that generates gross_spend data in net_spends table.
                                Maps to client's data source.
            - net_spend_source: Source system that generates net_spend data in net_spends table.
                               Maps to vendor's data source.
            - date_from: Start date (default: 1)
            - date_to: End date (default: 1)
            - risk: Risk flag (default: false)

    Raises:
        ValueError: If no filter parameters are provided
        ValueError: If array parameters are not lists of integers

    Note:
        - At least one filter parameter must be provided
        - The relationship between spend sources and net_spends table:
          * gross_spend_source indicates which system provides the gross spend data for a client
          * net_spend_source indicates which system provides the net spend data for a vendor
          * These sources populate the corresponding gross_spend and net_spend fields in the net_spends table
    """
    if not any([client_ids, vendor_ids, click_url_ids, job]):
        raise ValueError("At least one filter parameter must be provided")

    if client_ids is not None:
        if not isinstance(client_ids, list):
            raise ValueError("client_ids must be a list")
        if not all(isinstance(x, int) for x in client_ids):
            raise ValueError("client_ids must contain only integers")

    if vendor_ids is not None:
        if not isinstance(vendor_ids, list):
            raise ValueError("vendor_ids must be a list")
        if not all(isinstance(x, int) for x in vendor_ids):
            raise ValueError("vendor_ids must contain only integers")

    if click_url_ids is not None:
        if not isinstance(click_url_ids, list):
            raise ValueError("click_url_ids must be a list")
        if not all(isinstance(x, int) for x in click_url_ids):
            raise ValueError("click_url_ids must contain only integers")

    return get_db_direct_spend_job_stats(
        client_ids=client_ids,
        vendor_ids=vendor_ids,
        click_url_ids=click_url_ids,
        job=job
    )


async def main():
    await mcp.run_stdio_async()
