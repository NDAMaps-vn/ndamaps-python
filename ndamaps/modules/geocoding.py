"""NDAMaps SDK — Geocoding module."""

from __future__ import annotations

from typing import Any, Dict

from ..core.client import HttpClient, MAPS_API_BASE


class GeocodingModule:
    """Forward and reverse geocoding (address ↔ coordinates).

    Supports both Google and OSM response formats.
    """

    def __init__(self, http_client: HttpClient) -> None:
        self._http = http_client

    def forward(self, **params) -> Dict[str, Any]:
        """Convert address to coordinates.

        Google format: pass `address="..."`
        OSM format: pass `text="..."`

        Args:
            address: Address string (Google format)
            text: Address string (OSM format)
            size: Number of results (OSM only)
            admin_v2: Return updated admin info

        Returns:
            Google: {"results": [...], "status": "OK"}
            OSM: {"type": "FeatureCollection", "features": [...]}
        """
        return self._http.get(MAPS_API_BASE, "/geocode/forward", self._build_query(params))

    def reverse(self, **params) -> Dict[str, Any]:
        """Convert coordinates to address.

        Google format: pass `latlng="lat,lng"`
        OSM format: pass `point_lat=..., point_lon=...`

        Args:
            latlng: Coordinates as "lat,lng" (Google format)
            point_lat: Latitude (OSM format)
            point_lon: Longitude (OSM format)
            boundary_circle_radius: Search radius in km
            size: Number of results
            admin_v2: Return updated admin info

        Returns:
            Google: {"results": [...], "status": "OK"}
            OSM: {"type": "FeatureCollection", "features": [...]}
        """
        return self._http.get(MAPS_API_BASE, "/geocode/reverse", self._build_query(params))

    @staticmethod
    def _build_query(params: Dict[str, Any]) -> Dict[str, Any]:
        mapping = {
            "point_lat": "point.lat",
            "point_lon": "point.lon",
            "boundary_circle_radius": "boundary.circle.radius",
        }
        result = {}
        for key, value in params.items():
            if value is not None:
                api_key = mapping.get(key, key)
                result[api_key] = value
        return result
