"""NDAMaps SDK — HTTP client wrapper with retry logic."""

from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, Optional, Type, TypeVar

import httpx

from .errors import (
    NDAMapsError,
    NDAMapsErrorCode,
    RETRYABLE_STATUS_CODES,
    map_http_status_to_error_code,
)

# ── Base URLs ─────────────────────────────────

MAPS_API_BASE = "https://mapapis.ndamaps.vn/v1"
TILES_BASE = "https://nda-tiles.openmap.vn"
NDAVIEW_API_BASE = "https://api-view.ndamaps.vn/v1"

T = TypeVar("T")


class HttpClient:
    """Low-level HTTP client with automatic API key injection and retry logic.

    Uses httpx for both sync and async HTTP requests.
    Modules receive this via dependency injection from NDAMapsClient.
    """

    def __init__(
        self,
        api_key: str,
        max_retries: int = 3,
        base_delay_ms: int = 500,
    ) -> None:
        self._api_key = api_key
        self._max_retries = max_retries
        self._base_delay_ms = base_delay_ms
        self._client = httpx.Client(timeout=30.0)

    @property
    def api_key(self) -> str:
        return self._api_key

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    # ── Public API ────────────────────────────

    def get(
        self,
        base_url: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Perform a GET request with auto retry."""
        query = self._build_params(params)
        url = f"{base_url}{path}"
        return self._execute_with_retry("GET", url, query)

    def post(
        self,
        base_url: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Perform a POST request with auto retry."""
        query = self._build_params(params)
        url = f"{base_url}{path}"
        return self._execute_with_retry("POST", url, query)

    def build_url(
        self,
        base_url: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build a full URL string (for URL-builder methods). No HTTP request."""
        query = self._build_params(params)
        url = httpx.URL(f"{base_url}{path}", params=query)
        return str(url)

    # ── Private ───────────────────────────────

    def _build_params(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Build query params dict with apikey injected."""
        result: Dict[str, str] = {"apikey": self._api_key}
        if params:
            for key, value in params.items():
                if value is not None:
                    result[key] = str(value)
        return result

    def _execute_with_retry(
        self,
        method: str,
        url: str,
        params: Dict[str, str],
        attempt: int = 0,
    ) -> Any:
        """Execute HTTP request with retry on transient failures."""
        try:
            response = self._client.request(method, url, params=params)
        except httpx.HTTPError as exc:
            if attempt < self._max_retries:
                self._sleep(self._get_backoff_delay(attempt))
                return self._execute_with_retry(method, url, params, attempt + 1)
            raise NDAMapsError(
                NDAMapsErrorCode.NETWORK_ERROR,
                f"Network error after {self._max_retries + 1} attempts: {exc}",
            ) from exc

        # Retryable status codes
        if response.status_code in RETRYABLE_STATUS_CODES and attempt < self._max_retries:
            self._sleep(self._get_backoff_delay(attempt))
            return self._execute_with_retry(method, url, params, attempt + 1)

        # Non-retryable errors
        if response.status_code >= 400:
            raw_body = None
            try:
                raw_body = response.json()
            except Exception:
                raw_body = response.text

            error_code = map_http_status_to_error_code(response.status_code)
            message = (
                raw_body.get("message", f"HTTP {response.status_code}")
                if isinstance(raw_body, dict)
                else f"HTTP {response.status_code}: {response.reason_phrase}"
            )
            raise NDAMapsError(error_code, message, response.status_code, raw_body)

        return response.json()

    def _get_backoff_delay(self, attempt: int) -> float:
        """Exponential backoff delay in seconds."""
        return (self._base_delay_ms / 1000.0) * (2 ** attempt)

    def _sleep(self, seconds: float) -> None:
        time.sleep(seconds)
