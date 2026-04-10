"""NDAMaps SDK — Maps module (Static map URL builder + Tile styles)."""

from __future__ import annotations

from typing import Any, Dict, Optional
from urllib.parse import urlencode

from ..core.client import TILES_BASE
from ..core.types import StaticMapCenterMode, StaticMapAreaMode, StaticMapAutoMode, StaticMapParams


# ── Map Tile Style Constants ──────────────────

MAP_TILE_STYLES = {
    "DAY": "day-v1",
    "NIGHT": "night-v1",
    "SATELLITE": "satellite-v1",
}


class MapsModule:
    """Maps module — static map image URL builder + tile style URLs.

    This module does NOT make HTTP requests.
    It builds URL strings for use in <img> tags or as MapLibre GL style URLs.

    Example::

        # Static map
        url = client.maps.static_map_url(
            mode=StaticMapCenterMode(center=LatLng(21.03, 105.79), zoom=15),
            width=600, height=400, retina=True,
        )

        # Tile style for MapLibre GL
        style_url = client.maps.style_url("day-v1")
    """

    def __init__(self, api_key: str, tiles_base: str = TILES_BASE) -> None:
        self._api_key = api_key
        self._tiles_base = tiles_base

    def style_url(self, style: str = "day-v1") -> str:
        """Get MapLibre GL style.json URL for a given map tile style.

        Available styles:
        - "day-v1" — Daytime map (bright, clear)
        - "night-v1" — Nighttime map (dark mode)
        - "satellite-v1" — Satellite imagery

        Args:
            style: Map tile style identifier (default: "day-v1")

        Returns:
            Style JSON URL string (no HTTP request made)
        """
        return f"{self._tiles_base}/styles/{style}/style.json?apikey={self._api_key}"

    def static_map_url(
        self,
        mode,
        width: int = 600,
        height: int = 400,
        style_id: str = "ndamap",
        format: str = "png",
        retina: bool = False,
        marker: Optional[str] = None,
        path: Optional[str] = None,
        padding: Optional[float] = None,
    ) -> str:
        """Build a static map image URL.

        Supports 3 modes:
        1. StaticMapCenterMode: center + zoom
        2. StaticMapAreaMode: bounding box
        3. StaticMapAutoMode: auto-fit to markers/path

        Args:
            mode: Map mode (center/area/auto)
            width: Image width in pixels
            height: Image height in pixels
            style_id: Map style (default "ndamap")
            format: Image format ("png", "jpg", "webp")
            retina: If True, generates @2x image
            marker: Marker as "lng,lat|iconUrl"
            path: Path as comma-separated coordinates
            padding: Padding fraction

        Returns:
            URL string (no HTTP request made)
        """
        size_str = f"{width}x{height}@2x" if retina else f"{width}x{height}"

        # Build center path
        if isinstance(mode, StaticMapCenterMode):
            center_path = f"{mode.center.lng},{mode.center.lat},{mode.zoom}"
            if mode.bearing is not None:
                center_path += f"@{mode.bearing}"
                if mode.pitch is not None:
                    center_path += f",{mode.pitch}"
        elif isinstance(mode, StaticMapAreaMode):
            center_path = ",".join(str(v) for v in mode.bbox)
        elif isinstance(mode, StaticMapAutoMode):
            center_path = "auto"
        else:
            raise ValueError(f"Unknown mode type: {type(mode)}")

        base = f"{self._tiles_base}/styles/{style_id}/static/{center_path}/{size_str}.{format}"

        params: Dict[str, str] = {"apikey": self._api_key}
        if marker:
            params["marker"] = marker
        if path:
            params["path"] = path
        if padding is not None:
            params["padding"] = str(padding)

        return f"{base}?{urlencode(params)}"
