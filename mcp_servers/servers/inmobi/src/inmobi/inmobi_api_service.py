from typing import Dict, List

import httpx
from httpx import Timeout
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


class InmobiAPIService:
    """Service for interacting with the InMobi API."""

    BASE_URL = "https://api.cdr.inmobi.com/api/v3"

    def __init__(self, access_config: Dict[str, str]):
        """Initialize with API credentials.

        Args:
            access_config: Dictionary containing API credentials
        """
        self.client_id = access_config.get("client_id")
        self.client_secret = access_config.get("client_secret")
        self._token = None
        self._skan_report_id = None
        self._non_skan_report_id = None

    @retry(
        retry=retry_if_exception_type(httpx.HTTPError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def get_access_token(self) -> str:
        """Retrieve access token from InMobi auth endpoint."""
        response = httpx.post(
            f"{self.BASE_URL}/auth/token",
            json={"clientId": self.client_id, "clientSecret": self.client_secret},
            headers={"Content-Type": "application/json;charset=utf-8"},
            timeout=Timeout(30, connect=10, read=20, write=10),
        )
        response.raise_for_status()
        return response.json().get("data", {}).get("token")

    def access_token(self) -> str:
        """Get cached access token or retrieve a new one."""
        if not self._token:
            self._token = self.get_access_token()
        return self._token

    def get_report_ids(self, start_date: str, end_date: str) -> List[str]:
        """Get report IDs for SKAN and non-SKAN data.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            List containing [skan_report_id, non_skan_report_id]
        """
        # Ensure we have a token
        self.access_token()

        # Get SKAN report ID for iOS
        skan_report_id = self._get_skan_report_id(start_date, end_date)

        # Get non-SKAN report ID for Android
        non_skan_report_id = self._get_non_skan_report_id(start_date, end_date)

        return [skan_report_id, non_skan_report_id]

    @retry(
        retry=retry_if_exception_type(httpx.HTTPError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def _get_skan_report_id(self, start_date: str, end_date: str) -> str:
        """Request SKAN report generation and get report ID."""
        if self._skan_report_id:
            return self._skan_report_id

        payload = self._create_report_payload(start_date, end_date, "iOS")

        response = httpx.post(
            f"{self.BASE_URL}/reports/skan",
            json=payload,
            headers={
                "Authorization": self.access_token(),
                "Content-Type": "application/json;charset=utf-8",
            },
            timeout=Timeout(30, connect=10, read=20, write=10),
        )
        response.raise_for_status()
        self._skan_report_id = response.json().get("data", {}).get("reportId")
        return self._skan_report_id

    @retry(
        retry=retry_if_exception_type(httpx.HTTPError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def _get_non_skan_report_id(self, start_date: str, end_date: str) -> str:
        """Request non-SKAN report generation and get report ID."""
        if self._non_skan_report_id:
            return self._non_skan_report_id

        payload = self._create_report_payload(start_date, end_date, "Android")

        response = httpx.post(
            f"{self.BASE_URL}/reports/programmatic",
            json=payload,
            headers={
                "Authorization": self.access_token(),
                "Content-Type": "application/json;charset=utf-8",
            },
            timeout=Timeout(30, connect=10, read=20, write=10),
        )
        response.raise_for_status()
        self._non_skan_report_id = response.json().get("data", {}).get("reportId")
        return self._non_skan_report_id

    def _create_report_payload(self, start_date: str, end_date: str, os: str) -> Dict:
        """Create payload for report generation requests."""
        return {
            "startDate": start_date,
            "endDate": end_date,
            "filters": {"os": [os]},
            "dimensions": ["date", "campaign_id", "campaign_name", "os"],
        }

    @retry(
        retry=retry_if_exception_type(httpx.HTTPError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def check_report_status_once(self, report_id: str) -> str:
        """Check the status of a report once.

        Args:
            report_id: The ID of the report to check

        Returns:
            The status of the report
        """
        response = httpx.get(
            f"{self.BASE_URL}/reports/{report_id}/status",
            headers={"Authorization": self.access_token()},
            timeout=Timeout(30, connect=10, read=20, write=10),
        )
        response.raise_for_status()
        return response.json().get("data", {}).get("reportStatus")

    @retry(
        stop=stop_after_attempt(24), wait=wait_exponential(multiplier=1, min=5, max=60)
    )
    def _check_report_status(self, report_id: str) -> bool:
        """Check if a report is available for download with retries.

        Args:
            report_id: The ID of the report to check

        Returns:
            True if the report is available, False otherwise

        Raises:
            RetryError: If the report is not available after max retries
        """
        status = self.check_report_status_once(report_id)
        if status == "report.status.available":
            return True
        # This will trigger a retry if the status is not "available"
        raise ValueError(f"Report not available yet, status: {status}")

    @retry(
        retry=retry_if_exception_type(httpx.HTTPError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def _fetch_report_data(self, report_id: str) -> str:
        """Download report data and convert to list of dictionaries.

        Args:
            report_id: The ID of the report to download

        Returns:
            Report data in CSV format
        """
        response = httpx.get(
            f"{self.BASE_URL}/reports/{report_id}/download",
            headers={"Authorization": self.access_token()},
            timeout=Timeout(120, connect=60, read=60, write=60),
        )
        response.raise_for_status()

        return response.text

    def load(self, report_id: str) -> str:
        """
        Load campaign data from InMobi.

        Args:
            report_id: The ID of the report to load from InMobi

        Returns:
            Report data in CSV format
        """
        if self._check_report_status(report_id):
            return self._fetch_report_data(report_id)
        else:
            raise Exception("Report not available yet")
