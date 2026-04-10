"""NDAMaps SDK — Navigation module."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Union

from ..core.client import HttpClient, MAPS_API_BASE
from ..core.types import LatLng


class NavigationModule:
    """Routing directions and distance matrix calculations."""

    def __init__(self, http_client: HttpClient) -> None:
        self._http = http_client

    def directions(self, **params) -> Dict[str, Any]:
        """Get turn-by-turn routing directions.

        Args:
            origin: Origin as "lat,lng" string or LatLng object
            destination: Single or multiple destinations
            vehicle: "car", "bike", "motor", "taxi", "truck", "walking"
            alternatives: Return alternative routes
            language: "en" or "vi"
            admin_v2: Return updated admin info

        Returns:
            {"geocoded_waypoints": [...], "routes": [...]}
        """
        origin = params.get("origin")
        destination = params.get("destination")

        query: Dict[str, Any] = {}

        # Convert origin
        if isinstance(origin, LatLng):
            query["origin"] = f"{origin.lat},{origin.lng}"
        elif origin is not None:
            query["origin"] = str(origin)

        # Convert destination(s)
        if isinstance(destination, (list, tuple)):
            parts = []
            for d in destination:
                if isinstance(d, LatLng):
                    parts.append(f"{d.lat},{d.lng}")
                else:
                    parts.append(str(d))
            query["destination"] = ";".join(parts)
        elif isinstance(destination, LatLng):
            query["destination"] = f"{destination.lat},{destination.lng}"
        elif destination is not None:
            query["destination"] = str(destination)

        # Optional params
        for key in ("vehicle", "alternatives", "language", "admin_v2"):
            if key in params and params[key] is not None:
                query[key] = params[key]

        return self._http.get(MAPS_API_BASE, "/direction", query)

    def distance_matrix(self, **params) -> Dict[str, Any]:
        """Calculate distance matrix between sources and targets.

        Args:
            sources: List of {"lat": ..., "lon": ...}
            targets: List of {"lat": ..., "lon": ...}
            id: Optional request identifier
            verbose: Return flat list with indices
            shape_format: Path geometry format

        Returns:
            {"sources_to_targets": [[...]], "locations": [...], "units": "km"}
        """
        sources = params.get("sources", [])
        targets = params.get("targets", [])

        # Format sources/targets as JSON array strings
        query: Dict[str, Any] = {}

        # Build JSON dictionary for sources and targets
        json_body = {
            "sources": [{"lat": str(s.get("lat", getattr(s, "lat", ""))), 
                         "lon": str(s.get("lon", getattr(s, "lon", "")))}
                        if isinstance(s, dict) else {"lat": str(s.lat), "lon": str(s.lon)} 
                        for s in sources],
            "targets": [{"lat": str(t.get("lat", getattr(t, "lat", ""))), 
                         "lon": str(t.get("lon", getattr(t, "lon", "")))}
                        if isinstance(t, dict) else {"lat": str(t.lat), "lon": str(t.lon)} 
                        for t in targets]
        }

        import json
        query["json"] = json.dumps(json_body)

        for key in ("id", "verbose", "shape_format"):
            if key in params and params[key] is not None:
                query[key] = params[key]

        return self._http.get(MAPS_API_BASE, "/distancematrix", query)

    def optimized_route(self, **params) -> Dict[str, Any]:
        """Calculate an optimized multi-stop route.

        Args:
            locations: List of locations {"lat": ..., "lon": ...}
            costing: Routing profile, default "auto"
            directions_options: Additional routing options (e.g. {"units": "km"})
            admin_v2: Return updated admin info

        Returns:
            {"trip": {"locations": [...], "legs": [...], "summary": {...}}}
        """
        locations = params.get("locations", [])
        
        json_body = {
            "locations": [
                {"lat": float(loc.get("lat", getattr(loc, "lat", 0))), 
                 "lon": float(loc.get("lon", getattr(loc, "lon", 0)))}
                if isinstance(loc, dict) else {"lat": float(loc.lat), "lon": float(loc.lon)} 
                for loc in locations
            ],
            "costing": params.get("costing", "auto")
        }

        if "directions_options" in params and params["directions_options"]:
            json_body["directions_options"] = params["directions_options"]

        import json
        query: Dict[str, Any] = {"json": json.dumps(json_body)}

        if "admin_v2" in params and params["admin_v2"] is not None:
            query["admin_v2"] = params["admin_v2"]

        return self._http.get(MAPS_API_BASE, "/optimized-route", query)
