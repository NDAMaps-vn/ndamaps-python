"""NDAMaps SDK — Places module."""

from __future__ import annotations

from typing import Any, Dict, Optional

from ..core.client import HttpClient, MAPS_API_BASE
from ..core.session import SessionManager


class PlacesModule:
    """Place search, autocomplete, detail, children, and nearby.

    Session tokens are automatically managed for billing optimization:
    autocomplete() generates a token, placeDetail() reuses it.
    """

    def __init__(self, http_client: HttpClient, session: SessionManager) -> None:
        self._http = http_client
        self._session = session

    def autocomplete(self, **params) -> Dict[str, Any]:
        """Search for places with autocomplete.

        Google format: pass `input="query"`
        OSM format: pass `text="query"`

        Args:
            input: Search keyword (Google format)
            text: Search keyword (OSM format)
            location: Location bias as "lat,lng"
            origin: Origin for distance_meters
            radius: Search radius in km
            size: Number of results
            sessiontoken: UUID v4 session token (auto-generated if omitted)
            admin_v2: Return updated admin info

        Returns:
            Google: {"predictions": [...], "status": "OK"}
            OSM: {"type": "FeatureCollection", "features": [...]}
        """
        query = self._build_query(params)

        # Auto session token for Google format
        if "input" in params and "sessiontoken" not in params:
            query["sessiontoken"] = self._session.get_or_create()
        elif "sessiontoken" in params:
            pass  # User provided their own

        return self._http.get(MAPS_API_BASE, "/autocomplete", query)

    def place_detail(self, **params) -> Dict[str, Any]:
        """Get detailed information about a place.

        Args:
            ids: Place ID string (required)
            format: "google" or "osm" (default: "google")
            sessiontoken: Session token (reused from autocomplete if available)
            admin_v2: Return updated admin info

        Returns:
            Google: {"result": {...}, "status": "OK"}
            OSM: {"type": "FeatureCollection", "features": [...]}
        """
        query = self._build_query(params)

        # Reuse session token from autocomplete
        if "sessiontoken" not in params:
            token = self._session.get_current()
            if token:
                query["sessiontoken"] = token
                self._session.reset()

        return self._http.get(MAPS_API_BASE, "/place", query)

    def children(self, **params) -> Dict[str, Any]:
        """Get child places of a parent place.

        Args:
            parent_id: Parent place ID (required)
            admin_v2: Return updated admin info

        Returns:
            {"predictions": [...], "status": "OK"}
        """
        return self._http.get(MAPS_API_BASE, "/place/children", self._build_query(params))

    def nearby(self, **params) -> Dict[str, Any]:
        """Search for nearby places.

        Args:
            categories: Place category filter (required)
            point_lat: Center latitude
            point_lon: Center longitude
            size: Max results (default 5)
            boundary_circle_radius: Search radius in km
            admin_v2: Return updated admin info

        Returns:
            {"type": "FeatureCollection", "features": [...]}
        """
        return self._http.get(MAPS_API_BASE, "/nearby", self._build_query(params))

    @staticmethod
    def _build_query(params: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Python param names to API query params."""
        mapping = {
            "point_lat": "point.lat",
            "point_lon": "point.lon",
            "boundary_circle_lat": "boundary.circle.lat",
            "boundary_circle_lon": "boundary.circle.lon",
            "boundary_circle_radius": "boundary.circle.radius",
        }
        result = {}
        for key, value in params.items():
            if value is not None:
                api_key = mapping.get(key, key)
                result[api_key] = value
        return result
