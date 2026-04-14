"""NDAMaps SDK — Async client for Python (httpx async)."""

from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from .core.client import MAPS_API_BASE, TILES_BASE, NDAVIEW_API_BASE
from .core.errors import (
    NDAMapsError,
    NDAMapsErrorCode,
    RETRYABLE_STATUS_CODES,
    map_http_status_to_error_code,
)
from .core.session import SessionManager
from .modules.places import PlacesModule
from .modules.geocoding import GeocodingModule
from .modules.navigation import NavigationModule
from .modules.maps import MapsModule, MAP_TILE_STYLES
from .modules.ndaview import NdaViewModule
from .modules.forcodes import ForcodesModule


class AsyncHttpClient:
    """Async HTTP client with API key injection and retry logic.

    Uses httpx.AsyncClient for non-blocking HTTP requests.
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
        self._client = httpx.AsyncClient(timeout=30.0)

    @property
    def api_key(self) -> str:
        return self._api_key

    async def close(self) -> None:
        """Close the underlying async HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def get(
        self,
        base_url: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Perform an async GET request with auto retry."""
        query = self._build_params(params)
        url = f"{base_url}{path}"
        return await self._execute_with_retry("GET", url, query)

    async def post(
        self,
        base_url: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Perform an async POST request with auto retry."""
        query = self._build_params(params)
        url = f"{base_url}{path}"
        return await self._execute_with_retry("POST", url, query)

    def build_url(
        self,
        base_url: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build a full URL string. No HTTP request."""
        query = self._build_params(params)
        url = httpx.URL(f"{base_url}{path}", params=query)
        return str(url)

    def _build_params(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        result: Dict[str, str] = {"apikey": self._api_key}
        if params:
            for key, value in params.items():
                if value is not None:
                    result[key] = str(value)
        return result

    async def _execute_with_retry(
        self,
        method: str,
        url: str,
        params: Dict[str, str],
        attempt: int = 0,
    ) -> Any:
        import asyncio

        try:
            response = await self._client.request(method, url, params=params)
        except httpx.HTTPError as exc:
            if attempt < self._max_retries:
                await asyncio.sleep(self._get_backoff_delay(attempt))
                return await self._execute_with_retry(method, url, params, attempt + 1)
            raise NDAMapsError(
                NDAMapsErrorCode.NETWORK_ERROR,
                f"Network error after {self._max_retries + 1} attempts: {exc}",
            ) from exc

        if response.status_code in RETRYABLE_STATUS_CODES and attempt < self._max_retries:
            import asyncio
            await asyncio.sleep(self._get_backoff_delay(attempt))
            return await self._execute_with_retry(method, url, params, attempt + 1)

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
        return (self._base_delay_ms / 1000.0) * (2 ** attempt)


class AsyncNDAMapsClient:
    """Async entry point for the NDAMaps SDK.

    Provides the same API as NDAMapsClient but uses async/await for all
    HTTP operations. Ideal for asyncio-based applications (FastAPI, aiohttp, etc.).

    Usage::

        async with AsyncNDAMapsClient(api_key="YOUR_KEY") as client:
            results = await client.places.autocomplete(input="Lotte Mall")
            route = await client.navigation.directions(
                origin="21.03,105.79", destination="21.05,105.80"
            )
    """

    def __init__(
        self,
        api_key: str,
        maps_api_base: Optional[str] = None,
        tiles_base: Optional[str] = None,
        ndaview_api_base: Optional[str] = None,
        max_retries: int = 3,
        base_delay_ms: int = 500,
    ) -> None:
        if not api_key:
            raise ValueError("AsyncNDAMapsClient requires an api_key")

        self._http = AsyncHttpClient(
            api_key=api_key,
            max_retries=max_retries,
            base_delay_ms=base_delay_ms,
        )
        self._session = SessionManager()

        # Initialize modules — they accept the async http client via duck typing
        self.places = PlacesModule(self._http, self._session)
        self.geocoding = GeocodingModule(self._http)
        self.navigation = NavigationModule(self._http)
        self.maps = MapsModule(api_key, tiles_base or TILES_BASE)
        self.ndaview = NdaViewModule(self._http, ndaview_api_base or NDAVIEW_API_BASE)
        self.forcodes = ForcodesModule(self._http)

    async def close(self) -> None:
        """Close the underlying async HTTP client."""
        await self._http.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
