import os
import time
import requests
from datetime import datetime, timedelta
from cachetools import TTLCache
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class IronSourceAPI:
    def __init__(self):
        self.base_url = "https://api.ironsrc.com/advertisers/v2"
        self.auth_url = "https://platform.ironsrc.com/partners/publisher/auth"
        self._token_cache = TTLCache(maxsize=1, ttl=3600)  # 1 hour cache

    def _get_access_token(self) -> str:
        """Get access token with caching, similar to Rails.cache implementation"""
        if "access_token" in self._token_cache:
            return self._token_cache["access_token"]

        try:
            response = self._make_request(
                "GET",
                self.auth_url,
                headers={
                    "secretkey": os.getenv("IRON_SOURCE_SECRET_KEY", ""),
                    "refreshToken": os.getenv("IRON_SOURCE_REFRESH_KEY", "")
                }
            )

            if response.status_code != 200:
                logger.error(f"IronSource API Token error: {response.text}")
                return ""

            token = response.text.strip('"')
            self._token_cache["access_token"] = token
            return token

        except Exception as e:
            logger.error(f"Error getting IronSource access token: {str(e)}")
            return ""

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with retry logic"""
        max_retries = 3
        base_interval = 3

        for attempt in range(max_retries):
            try:
                response = requests.request(method, url, **kwargs)
                return response
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = base_interval * (attempt + 1)
                logger.warning(f"Request failed, retrying in {wait_time}s: {str(e)}")
                time.sleep(wait_time)

    def fetch_reports(self, start_date: str, end_date: str, campaign_ids: List[str]) -> List[Dict[str, Any]]:
        """Fetch reports for specific campaign IDs"""
        return self._fetch_reports(start_date, end_date, campaign_id=",".join(campaign_ids))

    def fetch_reports_by_bundleids(self, start_date: str, end_date: str, bundle_ids: List[str]) -> List[Dict[str, Any]]:
        """Fetch reports for specific bundle IDs"""
        return self._fetch_reports(start_date, end_date, bundle_id=",".join(bundle_ids))

    def fetch_all_reports(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch all reports without filtering"""
        return self._fetch_reports(start_date, end_date)

    def _fetch_reports(self, start_date: str, end_date: str, **extra_params) -> List[Dict[str, Any]]:
        """Common method for fetching reports with different filters"""
        token = self._get_access_token()
        if not token:
            return []

        params = {
            "startDate": start_date,
            "endDate": end_date,
            "metrics": "impressions,clicks,completions,installs,spend",
            "breakdowns": "day,campaign",
            "format": "json",
            **extra_params
        }

        try:
            response = self._make_request(
                "GET",
                f"{self.base_url}/reports",
                headers={"Authorization": f"Bearer {token}"},
                params=params
            )

            if response.status_code != 200:
                logger.error(f"Error fetching reports: {response.text}")
                return []

            return response.json().get("data")

        except Exception as e:
            logger.error(f"Error fetching reports: {str(e)}")
            return []
