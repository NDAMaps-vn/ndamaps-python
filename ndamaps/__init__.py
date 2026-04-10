"""NDAMaps SDK — Official Python SDK for Vietnam's national digital map platform.

Usage::

    from ndamaps import NDAMapsClient

    client = NDAMapsClient(api_key="YOUR_API_KEY")

    # Autocomplete
    results = client.places.autocomplete(input="Hồ Hoàn Kiếm")

    # Directions
    route = client.navigation.directions(
        origin="21.03,105.79", destination="21.05,105.80"
    )

    # Forcodes
    forcode = client.forcodes.encode(lat=20.99, lng=105.87)
"""

from __future__ import annotations

from typing import Optional

from .core.client import HttpClient, MAPS_API_BASE, TILES_BASE, NDAVIEW_API_BASE
from .core.errors import NDAMapsError, NDAMapsErrorCode
from .core.session import SessionManager
from .modules.places import PlacesModule
from .modules.geocoding import GeocodingModule
from .modules.navigation import NavigationModule
from .modules.maps import MapsModule, MAP_TILE_STYLES
from .modules.ndaview import NdaViewModule
from .modules.forcodes import ForcodesModule


class NDAMapsClient:
    """Main entry point for the NDAMaps SDK.

    Creates a single client instance with access to all API modules:
    - places — Autocomplete, place detail, children, nearby
    - geocoding — Forward and reverse geocoding
    - navigation — Routing and distance matrix
    - maps — Static map + tile style URL builder
    - ndaview — Street-level 360° imagery
    - forcodes — Encode/decode Forcode strings

    Args:
        api_key: Your NDAMaps API key
        maps_api_base: Override Maps API base URL
        tiles_base: Override Tiles base URL
        ndaview_api_base: Override NDAView API base URL
        max_retries: Max retry attempts (default 3)
        base_delay_ms: Base delay for exponential backoff (default 500ms)
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
            raise ValueError("NDAMapsClient requires an api_key")

        self._http = HttpClient(
            api_key=api_key,
            max_retries=max_retries,
            base_delay_ms=base_delay_ms,
        )
        self._session = SessionManager()

        # Initialize modules
        self.places = PlacesModule(self._http, self._session)
        self.geocoding = GeocodingModule(self._http)
        self.navigation = NavigationModule(self._http)
        self.maps = MapsModule(api_key, tiles_base or TILES_BASE)
        self.ndaview = NdaViewModule(self._http, ndaview_api_base or NDAVIEW_API_BASE)
        self.forcodes = ForcodesModule(self._http)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


__all__ = [
    "NDAMapsClient",
    "NDAMapsError",
    "NDAMapsErrorCode",
    "MAP_TILE_STYLES",
    "MAPS_API_BASE",
    "TILES_BASE",
    "NDAVIEW_API_BASE",
    "SessionManager",
    "PlacesModule",
    "GeocodingModule",
    "NavigationModule",
    "MapsModule",
    "NdaViewModule",
    "ForcodesModule",
]
