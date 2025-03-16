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
