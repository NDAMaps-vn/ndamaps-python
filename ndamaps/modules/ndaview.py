"""NDAMaps SDK — NDAView module (Street-level 360° imagery)."""

from __future__ import annotations

from typing import Any, Dict, Optional
from urllib.parse import urlencode

from ..core.client import HttpClient, NDAVIEW_API_BASE
from ..core.types import LatLng


class NdaViewModule:
    """Street-level 360° imagery — thumbnail URL builder and STAC search.

    Example::

        # Thumbnail URL (no HTTP request)
        url = client.ndaview.static_thumbnail_url(
            place_position=LatLng(21.033, 105.788), yaw=276
        )

        # Search nearby imagery
        results = client.ndaview.search(
            place_position=LatLng(21.033, 105.788), limit=5
        )
    """

    def __init__(self, http_client: HttpClient, ndaview_base: str = NDAVIEW_API_BASE) -> None:
        self._http = http_client
        self._base = ndaview_base

    def static_thumbnail_url(
        self,
        id: Optional[str] = None,
        place_position: Optional[LatLng] = None,
        yaw: Optional[float] = None,
        pitch: Optional[float] = None,
    ) -> str:
        """Build a static thumbnail URL for NDAView imagery.

        No HTTP request is made — returns a URL string.

        Args:
            id: NDAView item UUID
            place_position: Coordinates as LatLng
            yaw: Rotation angle in degrees (0-360)
            pitch: Tilt angle in degrees

        Returns:
            Thumbnail JPEG URL string
        """
        params: Dict[str, str] = {"apikey": self._http.api_key}

        if id:
            params["id"] = id
        if place_position:
            params["place_position"] = f"{place_position.lng},{place_position.lat}"
        if yaw is not None:
            params["yaw"] = str(yaw)
        if pitch is not None:
            params["pitch"] = str(pitch)

        return f"{self._base}/items/static/thumbnail.jpeg?{urlencode(params)}"

    def search(
        self,
        place_position: Optional[LatLng] = None,
        place_distance: Optional[str] = None,
        place_fov_tolerance: Optional[float] = None,
        bbox: Optional[str] = None,
        datetime: Optional[str] = None,
        limit: Optional[int] = None,
        ids: Optional[str] = None,
        collections: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search for NDAView 360° imagery.

        Args:
            place_position: Center coordinates as LatLng
            place_distance: Distance range in meters (e.g. "3-15")
            place_fov_tolerance: FOV tolerance in degrees
            bbox: Bounding box as "minLon,minLat,maxLon,maxLat"
            datetime: RFC 3339 datetime or interval
            limit: Max number of results (1-10000, default 10)
            ids: Comma-separated item UUIDs
            collections: Comma-separated collection UUIDs

        Returns:
            {"type": "FeatureCollection", "features": [...]}
        """
        query: Dict[str, Any] = {}

        if place_position:
            query["place_position"] = f"{place_position.lng},{place_position.lat}"
        if place_distance:
            query["place_distance"] = place_distance
        if place_fov_tolerance is not None:
            query["place_fov_tolerance"] = place_fov_tolerance
        if bbox:
            query["bbox"] = bbox
        if datetime:
            query["datetime"] = datetime
        if limit is not None:
            query["limit"] = limit
        if ids:
            query["ids"] = ids
        if collections:
            query["collections"] = collections

        return self._http.get(self._base, "/search", query)
