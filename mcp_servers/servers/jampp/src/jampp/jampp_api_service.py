from typing import Dict

import httpx
from httpx import Timeout


class JamppAPIService:
    # https://developers.jampp.com/docs/reporting-api/
    BASE_URL = "https://reporting-api.jampp.com/v1"

    def __init__(self, access_config: Dict[str, str]):
        self.api_client_id = access_config.get("api_client_id")
        self.api_client_secret = access_config.get("api_client_secret")
        self._token = None

    def get_access_token(self) -> str:
        """Retrieve access token from Jampp auth endpoint"""
        try:
            response = httpx.post(
                "https://auth.jampp.com/v1/oauth/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.api_client_id,
                    "client_secret": self.api_client_secret,
                },
                timeout=Timeout(30, connect=10, read=20, write=10),
            )
            response.raise_for_status()
            return response.json().get("access_token")
        except httpx.HTTPError as e:
            raise Exception(f"Failed to get access token: {e}")

    def access_token(self) -> str:
        """Get cached access token or retrieve a new one"""
        if not self._token:
            self._token = self.get_access_token()
        return self._token

    def load(self, start_date: str, end_date: str) -> list[dict]:
        """
        Load campaign spend data from Jampp

        Args:
            start_date: Start date in ISO format
            end_date: End date in ISO format

        Returns:
            Dictionary containing the report data
        """
        query = """
            query spendPerCampaign($from: DateTime!, $to: DateTime!) {
                pivot(from: $from, to: $to) {
                    results {
                      date(granularity: DAILY)
                      campaignId
                      campaign
                      impressions
                      clicks
                      installs
                      spend
                      firstorder: events(eventId: 50)
                    }
                }
            }
        """

        try:
            response = httpx.post(
                f"{self.BASE_URL}/graphql",
                json={
                    "query": query,
                    "variables": {"from": start_date, "to": end_date},
                },
                headers={"Authorization": f"Bearer {self.access_token()}"},
                timeout=Timeout(120, connect=60, read=60, write=60),
            )
            response.raise_for_status()
            return response.json().get("data", {}).get("pivot", {}).get("results", [])
        except httpx.HTTPError as e:
            raise Exception(f"Failed to load report: {e}")
