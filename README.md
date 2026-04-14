<p align="center">
  <img src="https://ndamaps.vn/logo.png" width="200" alt="NDAMaps Logo" />
</p>

# NDAMaps SDK for Python

Official Python SDK for **NDAMaps** — Vietnam's national digital map platform API.

Typed with `typing` / PEP 484. HTTP via **`httpx`** (sync only). Automatic retries with exponential backoff on transient failures.

## Features

- **Places** — Autocomplete, place detail, children, nearby search
- **Geocoding** — Forward and reverse geocoding (address ↔ coordinates)
- **Navigation** — Turn-by-turn routing, distance matrix, optimized multi-stop route
- **Maps** — Static map image URL builder and MapLibre style URLs
- **NDAView** — Street-level 360° imagery (thumbnail URLs + search)
- **Forcodes** — Encode/decode coordinates to compact location codes
- **Session management** — Automatic billing optimization for autocomplete → place detail

## Requirements

- Python **3.9+**

## Install

```bash
pip install ndamaps
```

For development (tests):

```bash
pip install ndamaps[dev]
```

## Quick start

```python
from ndamaps import NDAMapsClient

with NDAMapsClient(api_key="YOUR_API_KEY") as client:
    results = client.places.autocomplete(input="Lotte Mall Tây Hồ")
    print(results["predictions"][0]["description"])
```

`NDAMapsClient` supports the context manager protocol and has a `close()` method to release the underlying HTTP client.

## API Reference

Parameter names use **snake_case**. Several modules map Python names to query keys (for example `point_lat` / `point_lon` → `point.lat` / `point.lon`).

Shared geometry type:

```python
from ndamaps.core.types import LatLng
```

### Places

```python
# Autocomplete (Google format)
res = client.places.autocomplete(input="Hồ Hoàn Kiếm")
print(res["predictions"][0]["place_id"])

# Autocomplete (OSM / GeoJSON format)
res = client.places.autocomplete(text="Hồ Hoàn Kiếm")
print(res["features"][0]["properties"]["id"])

# Place detail (session token from autocomplete is reused automatically)
detail = client.places.place_detail(ids="PLACE_ID", format="google")
print(detail["result"]["name"], detail["result"]["geometry"]["location"])

# Children (sub-locations)
children = client.places.children(parent_id="PARENT_ID")

# Nearby search
nearby = client.places.nearby(
    categories="restaurant",
    point_lat=21.0265,
    point_lon=105.8524,
    size=10,
)
```

### Geocoding

```python
# Forward: address → coordinates (Google format)
res = client.geocoding.forward(address="12 Ngõ 1 Dịch Vọng Hậu, Hà Nội")
print(res["results"][0]["geometry"]["location"])

# Forward (OSM format)
res = client.geocoding.forward(text="12 Ngõ 1 Dịch Vọng Hậu", size=3)

# Reverse: coordinates → address (Google format)
res = client.geocoding.reverse(latlng="21.076,105.813")
print(res["results"][0]["formatted_address"])

# Reverse (OSM format)
res = client.geocoding.reverse(point_lat=21.076, point_lon=105.813)
```

### Navigation

```python
from ndamaps.core.types import LatLng

# Directions (single destination)
route = client.navigation.directions(
    origin=LatLng(lat=21.03, lng=105.79),
    destination=LatLng(lat=21.05, lng=105.80),
    vehicle="car",  # car | bike | motor | taxi | truck | walking
    language="vi",
)
leg = route["routes"][0]["legs"][0]
print(leg["distance"]["text"], leg["duration"]["text"])

# Directions (multiple destinations as list → joined with ";")
route = client.navigation.directions(
    origin="10.787,106.698",
    destination=["10.791,106.702", LatLng(lat=10.795, lng=106.710)],
)

# Distance matrix
matrix = client.navigation.distance_matrix(
    sources=[{"lat": "21.03", "lon": "105.79"}],
    targets=[
        {"lat": "21.05", "lon": "105.79"},
        {"lat": "21.07", "lon": "105.80"},
    ],
)

# Optimized multi-stop route
trip = client.navigation.optimized_route(
    locations=[
        {"lat": 21.03, "lon": 105.79},
        {"lat": 21.05, "lon": 105.80},
    ],
    costing="auto",
)
```

### Maps (static URL builder — no HTTP request)

```python
from ndamaps import MAP_TILE_STYLES
from ndamaps.core.types import LatLng, StaticMapCenterMode, StaticMapAreaMode, StaticMapAutoMode

# MapLibre GL style URL
style_url = client.maps.style_url(MAP_TILE_STYLES["DAY"])  # "day-v1"

# Center + zoom
url = client.maps.static_map_url(
    mode=StaticMapCenterMode(center=LatLng(lat=21.03, lng=105.79), zoom=15),
    width=600,
    height=400,
    retina=True,
    marker="105.79,21.03|https://example.com/icon.svg",
)

# Bounding box
url = client.maps.static_map_url(
    mode=StaticMapAreaMode(bbox=(105.7, 21.0, 105.9, 21.1)),
    width=800,
    height=600,
)

# Auto fit (markers / path)
url = client.maps.static_map_url(
    mode=StaticMapAutoMode(),
    width=600,
    height=400,
    path="105.78,21.03,105.80,21.05",
)
```

### NDAView (360° imagery)

```python
# Static thumbnail URL (no HTTP request)
thumb_url = client.ndaview.static_thumbnail_url(
    place_position=LatLng(lat=21.033, lng=105.788),
    yaw=276,
    pitch=20,
)

# Search for nearby imagery
results = client.ndaview.search(
    place_position=LatLng(lat=21.033, lng=105.788),
    place_distance="3-15",
    limit=10,
)
feature = results["features"][0]
hd_href = feature["assets"]["hd"]["href"]
```

### Forcodes

```python
encoded = client.forcodes.encode(lat=20.990396, lng=105.868825, resolution=13)
print(encoded["forcodes"])    # e.g. "HNVTDXJEB2UBBO"
print(encoded["admin_code"])  # e.g. "HNVT"

decoded = client.forcodes.decode(forcodes="HNVTDXJEB2UBBO")
print(decoded["lat"], decoded["lng"])
```

**Resolution guide** (approximate):

| Resolution | Precision   |
|-----------:|---------------|
| 15         | ~0.5 m        |
| 13         | ~3.5 m (default) |
| 11         | ~25 m         |
| 8          | ~461 m        |
| 5          | ~8.5 km       |

## Session tokens (billing)

For Google-format flows, the SDK ties **autocomplete** and **place_detail** to one session:

1. Calling `autocomplete(input=...)` without `sessiontoken` generates a UUID v4 token.
2. `place_detail` reuses that token when you omit `sessiontoken`, then clears it.
3. Tokens expire after **5 minutes** and are regenerated when needed.

```python
results = client.places.autocomplete(input="Lotte")
detail = client.places.place_detail(ids=results["predictions"][0]["place_id"])
# Same session token is used for both calls when you do not pass sessiontoken manually.
```

Manual control:

```python
import uuid

token = str(uuid.uuid4())
client.places.autocomplete(input="Lotte", sessiontoken=token)
client.places.place_detail(ids="...", sessiontoken=token)
```

## Error handling

```python
from ndamaps import NDAMapsClient, NDAMapsError, NDAMapsErrorCode

client = NDAMapsClient(api_key="YOUR_KEY")
try:
    client.forcodes.decode(forcodes="INVALID")
except NDAMapsError as err:
    print(err.code)         # NDAMapsErrorCode enum value
    print(err.message)
    print(err.status_code)  # HTTP status when applicable
    print(err.raw_body)     # Parsed JSON or text when available
```

Common codes: `INVALID_API_KEY`, `INVALID_FORCODE`, `PLACE_NOT_FOUND`, `ZERO_RESULTS`, `INVALID_PARAMS`, `NETWORK_ERROR`, `RATE_LIMIT_EXCEEDED`, `UNKNOWN`.

**Retries**: GET/POST requests are retried automatically on **429** and **5xx** responses (default **3** attempts, exponential backoff from `base_delay_ms`).

## Configuration

```python
client = NDAMapsClient(
    api_key="YOUR_KEY",           # required
    max_retries=3,                # default 3
    base_delay_ms=500,            # default 500
    maps_api_base="...",          # override Maps API base URL
    tiles_base="...",             # override tiles base URL
    ndaview_api_base="...",       # override NDAView API base URL
)
```

Module-level defaults (for reference): `MAPS_API_BASE`, `TILES_BASE`, `NDAVIEW_API_BASE` on `ndamaps` / `ndamaps.core.client`.

## Links

- [NDAMaps documentation](https://docs.ndamaps.vn)
- [NDAMaps platform](https://ndamaps.vn)

## License

MIT
