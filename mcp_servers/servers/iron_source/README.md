# Iron Source MCP Server

This MCP server provides tools to interact with the Iron Source API for fetching advertising reports.

## Tools

### fetch_reports
Fetch reports for specific campaign IDs.
- Parameters:
  - start_date: Start date in YYYY-MM-DD format
  - end_date: End date in YYYY-MM-DD format
  - campaign_ids: List of campaign IDs

### fetch_reports_by_bundleids
Fetch reports for specific bundle IDs.
- Parameters:
  - start_date: Start date in YYYY-MM-DD format
  - end_date: End date in YYYY-MM-DD format
  - bundle_ids: List of bundle IDs

### fetch_all_reports
Fetch all reports without filtering.
- Parameters:
  - start_date: Start date in YYYY-MM-DD format
  - end_date: End date in YYYY-MM-DD format

## Configuration

The server requires the following environment variables:
- IRON_SOURCE_SECRET_KEY: Your Iron Source secret key
- IRON_SOURCE_REFRESH_KEY: Your Iron Source refresh key

## Installation

```bash
pip install .
```

## Usage

The server can be run directly after installation:

```bash
iron_source
```

Or imported and used in Python code:

```python
from iron_source import main

main()
```
