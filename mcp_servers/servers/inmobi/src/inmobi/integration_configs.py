import os


def get_access_config() -> dict:
    return {
        "client_id": os.environ["INMOBI_CLIENT_ID"],
        "client_secret": os.environ["INMOBI_CLIENT_SECRET"],
    }
