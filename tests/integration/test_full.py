"""Integration tests — require a real NDAMaps API key.

Set NDAMAPS_API_KEY environment variable before running.
"""

import os
import pytest
import httpx

from ndamaps import NDAMapsClient, NDAMapsError, NDAMapsErrorCode
from ndamaps.core.types import LatLng, StaticMapCenterMode

API_KEY = os.environ.get("NDAMAPS_API_KEY")

pytestmark = pytest.mark.skipif(not API_KEY, reason="NDAMAPS_API_KEY is not set")


@pytest.fixture
def client():
    return NDAMapsClient(api_key=API_KEY)


# ── Places ────────────────────────────────────

def test_autocomplete_google(client: NDAMapsClient):
    res = client.places.autocomplete(input="Hồ Hoàn Kiếm")
    assert len(res["predictions"]) > 0
    assert res["status"] == "OK"
    print(f"  [OK] autocomplete: {res['predictions'][0]['description']}")

def test_autocomplete_osm(client: NDAMapsClient):
    res = client.places.autocomplete(text="Lotte Mall")
    assert res["type"] == "FeatureCollection"
    assert len(res["features"]) > 0
    print(f"  [OK] autocomplete OSM: {res['features'][0]['properties']['name']}")

def test_place_detail_session_reuse(client: NDAMapsClient):
    autocomplete_res = client.places.autocomplete(input="Lotte Mall")
    place_id = autocomplete_res["predictions"][0]["place_id"]
    detail = client.places.place_detail(ids=place_id)
    assert "features" in detail
    assert len(detail["features"]) > 0
    name = detail["features"][0].get("properties", {}).get("name", "N/A")
    print(f"  [OK] place_detail: {name}")

def test_nearby(client: NDAMapsClient):
    res = client.places.nearby(
        categories="restaurant",
        point_lat=21.0265,
        point_lon=105.8524,
        size=3,
    )
    assert res["type"] == "FeatureCollection"
    assert len(res["features"]) > 0
    print(f"  [OK] nearby: {len(res['features'])} found")

def test_forward_geocode(client: NDAMapsClient):
    res = client.geocoding.forward(address="12 Ngõ 1 Dịch Vọng Hậu, Cầu Giấy, Hà Nội")
    assert len(res["results"]) > 0
    loc = res["results"][0]["geometry"]["location"]
    assert loc["lat"] > 20
    assert loc["lng"] > 105
    print(f"  [OK] forward: lat={loc['lat']}, lng={loc['lng']}")

def test_reverse_geocode(client: NDAMapsClient):
    res = client.geocoding.reverse(latlng="21.075951,105.812662")
    assert len(res["results"]) > 0
    print(f"  [OK] reverse: {res['results'][0].get('formatted_address', '')}")

def test_directions(client: NDAMapsClient):
    res = client.navigation.directions(
        origin=LatLng(21.03, 105.79),
        destination=LatLng(21.05, 105.80),
        vehicle="car",
    )
    assert len(res["routes"]) > 0
    leg = res["routes"][0]["legs"][0]
    print(f"  [OK] directions: {leg['distance']['text']} {leg['duration']['text']}")

def test_distance_matrix(client: NDAMapsClient):
    res = client.navigation.distance_matrix(
        sources=[{"lat": "21.03", "lon": "105.79"}],
        targets=[{"lat": "21.05", "lon": "105.79"}, {"lat": "21.07", "lon": "105.80"}],
    )
    assert len(res["sources_to_targets"]) > 0
    assert len(res["sources_to_targets"][0]) == 2
    print("  [OK] distance matrix calculated")

def test_forcodes_roundtrip(client: NDAMapsClient):
    encoded = client.forcodes.encode(lat=20.990396, lng=105.868825, resolution=13)
    forcode = encoded["forcodes"]
    print(f"  [OK] encoded: {forcode}")

    decoded = client.forcodes.decode(forcodes=forcode)
    print(f"  [OK] decoded: lat={decoded['lat']}, lng={decoded['lng']}")

def test_forcodes_invalid(client: NDAMapsClient):
    with pytest.raises(NDAMapsError) as exc_info:
        client.forcodes.decode(forcodes="TOTALLYINVALID123")
    print(f"  [OK] invalid decode correctly threw: {exc_info.value.code}")

def test_static_map_url(client: NDAMapsClient):
    url = client.maps.static_map_url(
        mode=StaticMapCenterMode(center=LatLng(21.03, 105.79), zoom=15),
        width=300,
        height=200,
        style_id="day-v1"
    )
    res = httpx.get(url)
    assert res.status_code == 200
    print(f"  [OK] staticMap: received {len(res.content)} bytes")

def test_style_url_day(client: NDAMapsClient):
    url = client.maps.style_url("day-v1")
    res = httpx.get(url)
    assert res.status_code == 200
    json_data = res.json()
    print(f"  [OK] day-v1 style.json: version {json_data['version']}")

def test_ndaview_thumbnail_url(client: NDAMapsClient):
    url = client.ndaview.static_thumbnail_url(
        place_position=LatLng(21.033, 105.788),
        yaw=276
    )
    res = httpx.get(url)
    assert res.status_code == 200
    print(f"  [OK] thumbnail received: {len(res.content)} bytes")

def test_ndaview_search(client: NDAMapsClient):
    res = client.ndaview.search(
        place_position=LatLng(21.033, 105.788),
        limit=3
    )
    assert res["type"] == "FeatureCollection"
    print(f"  [OK] search: {len(res['features'])} features found")
