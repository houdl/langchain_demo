"""Database connection and query functionality."""
import os
from typing import Any, Dict, List
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

load_dotenv()

def get_db_engine() -> Engine:
    """Create and return a database engine."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set")

    return create_engine(db_url)

def get_db_client_infos(client_name: str) -> List[Dict[str, Any]]:
    """Get client information from the database.

    Args:
        client_name (str): Name of the client to search for

    Returns:
        List[Dict[str, Any]]: List of client records containing:
            - id: Client ID
            - name: Client name
            - created_at: Creation timestamp
            - updated_at: Last update timestamp
            - other client-specific fields
    """
    engine = get_db_engine()
    query = text("""
        SELECT clients.*
        FROM clients
        WHERE name ilike :client_name
    """)

    with engine.connect() as conn:
        result = conn.execute(
            query,
            {"client_name": client_name}
        )
        return [row._mapping for row in result]

def get_db_jampp_campaign_mappings(client_name: str, vendor_name: str) -> List[Dict[str, Any]]:
    """Get campaign mappings for a specific client and vendor.

    Args:
        client_name (str): Name of the client
        vendor_name (str): Name of the vendor

    Returns:
        List[Dict[str, Any]]: List of campaign mappings
    """
    engine = get_db_engine()

    query = text("""
        SELECT jcm.*, campaigns.name as campaign_name, c.name as client_name, v.vendor_name as vendor_name
        FROM jampp_campaign_mappings jcm
        JOIN campaigns  ON campaigns.id = jcm.campaign_id
        JOIN clients c ON campaigns.client_id = c.id
        JOIN vendors v ON jcm.vendor_id = v.id
        WHERE c.name ilike :client_name
        AND v.vendor_name = :vendor_name
    """)

    with engine.connect() as conn:
        result = conn.execute(
            query,
            {"client_name": client_name, "vendor_name": vendor_name}
        )
        return [row._mapping for row in result]

def get_db_direct_spend_job_stats(
    client_ids: List[int] = None,
    vendor_ids: List[int] = None,
    click_url_ids: List[int] = None,
    job: str = None
) -> List[Dict[str, Any]]:
    """Get direct spend job stats from the database.

    Args:
        client_ids (List[int], optional): List of client IDs to filter by
        vendor_ids (List[int], optional): List of vendor IDs to filter by
        click_url_ids (List[int], optional): List of click URL IDs to filter by
        job (str, optional): Job name to filter by

    Returns:
        List[Dict[str, Any]]: List of direct spend job stats records
    """
    engine = get_db_engine()
    conditions = []
    params: Dict[str, Any] = {}

    query = text("""
        SELECT dsjs.*,
               array_to_string(dsjs.pm_users, ',') as pm_users_str,
               array_to_string(dsjs.pa_users, ',') as pa_users_str,
               array_to_string(dsjs.click_url_ids, ',') as click_url_ids_str,
               array_to_string(dsjs.client_ids, ',') as client_ids_str,
               array_to_string(dsjs.vendor_ids, ',') as vendor_ids_str
        FROM direct_spend_job_stats dsjs
        WHERE deleted_at IS NULL
    """)

    if client_ids:
        conditions.append("dsjs.client_ids && :client_ids")
        params["client_ids"] = client_ids

    if vendor_ids:
        conditions.append("dsjs.vendor_ids && :vendor_ids")
        params["vendor_ids"] = vendor_ids

    if click_url_ids:
        conditions.append("dsjs.click_url_ids && :click_url_ids")
        params["click_url_ids"] = click_url_ids

    if job:
        conditions.append("dsjs.job = :job")
        params["job"] = job

    if conditions:
        query = text(str(query) + " AND " + " AND ".join(conditions))

    with engine.connect() as conn:
        result = conn.execute(query, params)
        return [dict(row._mapping) for row in result.fetchall()]


def get_db_net_spends(client_name: str, vendor_name: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """Get net spends for a client and vendor between dates.

    Args:
        client_name (str): Name of the client
        vendor_name (str): Name of the vendor
        start_date (str): Start date in ISO format
        end_date (str): End date in ISO format

    Returns:
        List[Dict[str, Any]]: List of net spend records
    """
    engine = get_db_engine()

    query = text("""
        SELECT ns.gross_spend_cents/100.0 as gross_spend, ns.net_spend_cents/100.0 as net_spend,
        ns.spend_date, ns.click_url_id as click_url_id, ns.campaign_id as campaign_id, camp.name as campaign_name,
        c.name as client_name, v.vendor_name as vendor_name
        FROM net_spends ns
        JOIN campaigns camp ON ns.campaign_id = camp.id
        JOIN clients c ON camp.client_id = c.id
        JOIN vendors v ON ns.vendor_id = v.id
        WHERE c.name ilike :client_name
        AND v.vendor_name = :vendor_name
        AND ns.spend_date BETWEEN :start_date AND :end_date
        ORDER BY ns.spend_date
    """)

    with engine.connect() as conn:
        result = conn.execute(
            query,
            {
                "client_name": client_name,
                "vendor_name": vendor_name,
                "start_date": start_date,
                "end_date": end_date
            }
        )
        return [dict(row._mapping) for row in result.fetchall()]
