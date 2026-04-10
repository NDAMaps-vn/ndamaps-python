"""NDAMaps SDK — Types and data structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Sequence, Union


# ── Primitives ────────────────────────────────

PlaceId = str
Forcode = str
StyleId = str  # 'ndamap', 'satellite', etc.
MapTileStyle = str  # 'day-v1', 'night-v1', 'satellite-v1'
VehicleType = Literal["car", "bike", "motor", "taxi", "truck", "walking"]
ResponseFormat = Literal["google", "osm"]
ImageFormat = Literal["png", "jpg", "webp"]


# ── Core Geometry ─────────────────────────────

@dataclass
class LatLng:
    """Coordinate pair."""
    lat: float
    lng: float


@dataclass
class TextValue:
    """Text + numeric value pair (used in route distance/duration)."""
    text: str
    value: float


# ── Autocomplete Params ───────────────────────

@dataclass
class AutocompleteGoogleParams:
    """Google format autocomplete parameters."""
    input: str
    location: Optional[str] = None
    origin: Optional[str] = None
    radius: Optional[float] = None
    size: Optional[int] = None
    sessiontoken: Optional[str] = None
    admin_v2: Optional[bool] = None


@dataclass
class AutocompleteOsmParams:
    """OSM format autocomplete parameters."""
    text: str
    boundary_circle_lat: Optional[float] = None
    boundary_circle_lon: Optional[float] = None
    boundary_circle_radius: Optional[float] = None
    size: Optional[int] = None
    sessiontoken: Optional[str] = None
    admin_v2: Optional[bool] = None


# ── Place Detail Params ───────────────────────

@dataclass
class PlaceDetailParams:
    """Place detail parameters."""
    ids: PlaceId
    format: Optional[ResponseFormat] = None
    sessiontoken: Optional[str] = None
    admin_v2: Optional[bool] = None


# ── Children Params ───────────────────────────

@dataclass
class PlaceChildrenParams:
    """Place children parameters."""
    parent_id: PlaceId
    admin_v2: Optional[bool] = None


# ── Nearby Params ─────────────────────────────

@dataclass
class NearbyParams:
    """Nearby search parameters."""
    categories: str
    point_lat: Optional[float] = None
    point_lon: Optional[float] = None
    size: Optional[int] = None
    boundary_circle_radius: Optional[float] = None
    admin_v2: Optional[bool] = None


# ── Geocoding Params ──────────────────────────

@dataclass
class ForwardGeocodeGoogleParams:
    """Forward geocode Google format."""
    address: str
    admin_v2: Optional[bool] = None


@dataclass
class ForwardGeocodeOsmParams:
    """Forward geocode OSM format."""
    text: str
    size: Optional[int] = None
    admin_v2: Optional[bool] = None


@dataclass
class ReverseGeocodeGoogleParams:
    """Reverse geocode Google format."""
    latlng: str
    admin_v2: Optional[bool] = None


@dataclass
class ReverseGeocodeOsmParams:
    """Reverse geocode OSM format."""
    point_lat: float
    point_lon: float
    boundary_circle_radius: Optional[float] = None
    size: Optional[int] = None
    admin_v2: Optional[bool] = None


# ── Navigation Params ─────────────────────────

@dataclass
class DirectionsParams:
    """Directions parameters."""
    origin: Union[str, LatLng]
    destination: Union[str, LatLng, Sequence[Union[str, LatLng]]]
    vehicle: Optional[VehicleType] = None
    alternatives: Optional[bool] = None
    language: Optional[Literal["en", "vi"]] = None
    admin_v2: Optional[bool] = None


@dataclass
class DistanceMatrixLocation:
    """A location for distance matrix."""
    lat: Union[str, float]
    lon: Union[str, float]


@dataclass
class DistanceMatrixParams:
    """Distance matrix parameters."""
    sources: List[DistanceMatrixLocation]
    targets: List[DistanceMatrixLocation]
    id: Optional[str] = None
    verbose: Optional[bool] = None
    shape_format: Optional[str] = None


@dataclass
class OptimizedRouteLocation:
    """A location for optimized route."""
    lat: Union[str, float]
    lon: Union[str, float]


@dataclass
class OptimizedRouteParams:
    """Optimized route parameters."""
    locations: List[OptimizedRouteLocation]
    costing: Optional[str] = None
    directions_options: Optional[Dict[str, Any]] = None
    admin_v2: Optional[bool] = None


# ── Static Map Params ─────────────────────────

@dataclass
class StaticMapCenterMode:
    """Center mode for static maps."""
    center: LatLng
    zoom: int
    bearing: Optional[float] = None
    pitch: Optional[float] = None


@dataclass
class StaticMapAreaMode:
    """Area mode for static maps (bounding box)."""
    bbox: tuple  # (min_lon, min_lat, max_lon, max_lat)


@dataclass
class StaticMapAutoMode:
    """Auto mode for static maps."""
    pass


StaticMapMode = Union[StaticMapCenterMode, StaticMapAreaMode, StaticMapAutoMode]


@dataclass
class StaticMapParams:
    """Static map parameters."""
    mode: StaticMapMode
    width: int
    height: int
    style_id: Optional[StyleId] = None
    format: Optional[ImageFormat] = None
    retina: bool = False
    marker: Optional[str] = None
    path: Optional[str] = None
    padding: Optional[float] = None


# ── NDAView Params ────────────────────────────

@dataclass
class NdaViewStaticParams:
    """NDAView static thumbnail parameters."""
    id: Optional[str] = None
    place_position: Optional[LatLng] = None
    yaw: Optional[float] = None
    pitch: Optional[float] = None


@dataclass
class NdaViewSearchParams:
    """NDAView search parameters."""
    place_position: Optional[LatLng] = None
    place_distance: Optional[str] = None
    place_fov_tolerance: Optional[float] = None
    bbox: Optional[str] = None
    datetime: Optional[str] = None
    limit: Optional[int] = None
    ids: Optional[str] = None
    collections: Optional[str] = None


# ── Forcodes Params ───────────────────────────

@dataclass
class ForcodeEncodeParams:
    """Forcode encode parameters."""
    lat: float
    lng: float
    resolution: Optional[int] = None


@dataclass
class ForcodeDecodeParams:
    """Forcode decode parameters."""
    forcodes: str


# ── SDK Config ────────────────────────────────

@dataclass
class NDAMapsClientOptions:
    """Configuration for NDAMapsClient."""
    api_key: str
    maps_api_base: Optional[str] = None
    tiles_base: Optional[str] = None
    ndaview_api_base: Optional[str] = None
    max_retries: int = 3
    base_delay_ms: int = 500
