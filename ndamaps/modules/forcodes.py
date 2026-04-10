"""NDAMaps SDK — Forcodes module."""

from __future__ import annotations

from typing import Any, Dict, Optional

from ..core.client import HttpClient, MAPS_API_BASE
from ..core.errors import NDAMapsError, NDAMapsErrorCode


class ForcodesModule:
    """Encode/decode coordinates ↔ Forcode strings.

    Forcodes are compact location codes unique to NDAMaps, based on H3 hexagons.

    Example::

        # Encode
        result = client.forcodes.encode(lat=20.990396, lng=105.868825, resolution=13)
        print(result["forcodes"])  # "HNVTDXJEB2UBBO"

        # Decode
        result = client.forcodes.decode(forcodes="HNVTDXJEB2UBBO")
        print(result["lat"], result["lng"])
    """

    def __init__(self, http_client: HttpClient) -> None:
        self._http = http_client

    def encode(
        self,
        lat: float,
        lng: float,
        resolution: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Encode coordinates to a Forcode string.

        Args:
            lat: Latitude in decimal degrees
            lng: Longitude in decimal degrees
            resolution: Hexagon resolution (0-15, default 13 ≈ 3.5m)

        Returns:
            {"forcodes": "...", "lat": ..., "lng": ..., "resolution": ..., "admin_code": "...", "status": "OK"}
        """
        query: Dict[str, Any] = {"lat": lat, "lng": lng}
        if resolution is not None:
            query["resolution"] = resolution

        return self._http.get(MAPS_API_BASE, "/forcodes/encode", query)

    def decode(self, forcodes: str) -> Dict[str, Any]:
        """Decode a Forcode string to coordinates.

        Args:
            forcodes: Forcode string to decode

        Returns:
            {"forcodes": "...", "lat": ..., "lng": ..., "resolution": ..., "status": "OK"}

        Raises:
            NDAMapsError: With code INVALID_FORCODE if the Forcode is invalid
        """
        query: Dict[str, Any] = {"forcodes": forcodes}

        response = self._http.get(MAPS_API_BASE, "/forcodes/decode", query)

        # Check for INVALID_FORCODES in response body (API may return 200 OK)
        if isinstance(response, dict) and response.get("status") == "INVALID_FORCODES":
            raise NDAMapsError(
                NDAMapsErrorCode.INVALID_FORCODE,
                f"Invalid Forcode: {forcodes}",
                raw_body=response,
            )

        return response
