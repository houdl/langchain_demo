import os
from typing import Optional

from fastapi import FastAPI
from langchain_mcp_adapters.client import MultiServerMCPClient
from mcp.client.stdio import get_default_environment

_app: Optional[FastAPI] = None


def initialize_app_reference(app: FastAPI):
    """
    Initialize the FastAPI app reference for MCP tools.
    """
    global _app
    _app = app


def get_mcp_tools():
    """
    Get MCP tools for the application.
    """
    if _app is None:
        raise ValueError("FastAPI App reference not initialized")
    return _app.state.mcp_tools


def create_mcp_client():
    """
    Create an MCP client for the application.
    """

    default_env = get_default_environment()
    current_dir = os.path.abspath(os.path.dirname(__file__))

    return MultiServerMCPClient(
        {
            "everything": {
                "command": "npx",
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-everything",
                ],
                "transport": "stdio",
            },
            # "postgres": {
            #     "command": "npx",
            #     "args": [
            #         "-y",
            #         "@modelcontextprotocol/server-postgres",
            #         os.environ.get("POSTGRES_DATABASE", ""),
            #     ],
            #     "transport": "stdio",
            # },
            "jampp": {
                "command": "uv",
                "args": [
                    "--directory",
                    os.path.join(current_dir, "mcp_servers", "servers", "jampp"),
                    "run",
                    "jampp",
                ],
                "transport": "stdio",
                "env": {
                    **default_env,
                    "TEXTNOW_JAMPP_API_CLIENT_SECRET": os.environ.get("TEXTNOW_JAMPP_API_CLIENT_SECRET", ""),
                },
            },
            "iron_source": {
                "command": "uv",
                "args": [
                    "--directory",
                    os.path.join(current_dir, "mcp_servers", "servers", "iron_source"),
                    "run",
                    "iron_source",
                ],
                "transport": "stdio",
                "env": {
                    **default_env,
                    "IRON_SOURCE_SECRET_KEY": os.environ.get("IRON_SOURCE_SECRET_KEY", ""),
                    "IRON_SOURCE_REFRESH_KEY": os.environ.get("IRON_SOURCE_REFRESH_KEY", ""),
                },
            },
            "feedmob": {
                "command": "uv",
                "args": [
                    "--directory",
                    os.path.join(current_dir, "mcp_servers", "servers", "feedmob"),
                    "run",
                    "feedmob",
                ],
                "transport": "stdio",
                "env": {
                    **default_env,
                    "DATABASE_URL": os.environ.get("POSTGRES_DATABASE", ""),
                },
            },
            "math": {
                "command": "python",
                "args": [os.path.join(current_dir, "mcp_servers", "math_server.py")],
                "transport": "stdio",
            },
            # "sequential-thinking": {
            #     "command": "bun",
            #     "args": ["x", "@modelcontextprotocol/server-sequential-thinking"],
            #     "transport": "stdio",
            # },
        }
    )
