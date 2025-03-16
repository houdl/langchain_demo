import os
from enum import Enum


class Client(str, Enum):
    textnow = "TextNow"
    uber = "Uber"


# Credential Configs: https://assistant.feedmob.ai/partner_integrations/5
CREDENTIALS = {
    Client.textnow: {
        "api_client_id": "3f0076f0ac22ab0f61d6494bdde9f4eb6ee97f4f",
        "api_client_secret": os.environ.get("TEXTNOW_JAMPP_API_CLIENT_SECRET", ""),
    },
    Client.uber: {
        "api_client_id": "3f0076f0ac22ab0f61d6494bdde9f4eb6ee97f4f",
        "api_client_secret": os.environ.get("TEXTNOW_JAMPP_API_CLIENT_SECRET", ""),
    }
}


def get_all_supported_clients() -> list[str]:
    """Get all supported clients."""
    return [client.value for client in CREDENTIALS.keys()]


def get_credentials(client: Client) -> dict:
    """Get credentials for the client."""
    return CREDENTIALS[client]
