"""Unit tests for Maps module."""

from ndamaps.core.types import LatLng, StaticMapCenterMode, StaticMapAreaMode, StaticMapAutoMode
from ndamaps.modules.maps import MapsModule, MAP_TILE_STYLES


class TestStaticMapUrl:
    def setup_method(self):
        self.maps = MapsModule(api_key="TEST_KEY", tiles_base="https://tiles.example.com")

    def test_center_mode_basic(self):
        url = self.maps.static_map_url(
            mode=StaticMapCenterMode(center=LatLng(21.03, 105.79), zoom=15),
            width=600,
            height=400,
        )
        assert "105.79,21.03,15" in url
        assert "600x400" in url
        assert ".png" in url
        assert "apikey=TEST_KEY" in url

    def test_center_mode_retina(self):
        url = self.maps.static_map_url(
            mode=StaticMapCenterMode(center=LatLng(21.03, 105.79), zoom=15),
            width=600,
            height=400,
            retina=True,
        )
        assert "600x400@2x" in url

    def test_center_mode_with_bearing_pitch(self):
        url = self.maps.static_map_url(
            mode=StaticMapCenterMode(center=LatLng(21.03, 105.79), zoom=15, bearing=45.0, pitch=30.0),
            width=600,
            height=400,
        )
        assert "105.79,21.03,15@45.0,30.0" in url

    def test_area_mode(self):
        url = self.maps.static_map_url(
            mode=StaticMapAreaMode(bbox=(105.0, 20.0, 106.0, 22.0)),
            width=800,
            height=600,
        )
        assert "105.0,20.0,106.0,22.0" in url

    def test_auto_mode(self):
        url = self.maps.static_map_url(
            mode=StaticMapAutoMode(),
            width=600,
            height=400,
        )
        assert "/auto/" in url

    def test_with_marker(self):
        url = self.maps.static_map_url(
            mode=StaticMapCenterMode(center=LatLng(21.03, 105.79), zoom=15),
            width=600,
            height=400,
            marker="105.79,21.03|https://example.com/pin.svg",
        )
        assert "marker=" in url

    def test_with_path(self):
        url = self.maps.static_map_url(
            mode=StaticMapCenterMode(center=LatLng(21.03, 105.79), zoom=15),
            width=600,
            height=400,
            path="105.79,21.03,105.80,21.04",
        )
        assert "path=" in url

    def test_custom_format(self):
        url = self.maps.static_map_url(
            mode=StaticMapCenterMode(center=LatLng(21.03, 105.79), zoom=15),
            width=600,
            height=400,
            format="webp",
        )
        assert ".webp" in url


class TestStyleUrl:
    def setup_method(self):
        self.maps = MapsModule(api_key="TEST_KEY", tiles_base="https://tiles.example.com")

    def test_default_style(self):
        url = self.maps.style_url()
        assert "/styles/day-v1/style.json" in url
        assert "apikey=TEST_KEY" in url

    def test_night_style(self):
        url = self.maps.style_url("night-v1")
        assert "/styles/night-v1/style.json" in url

    def test_satellite_style(self):
        url = self.maps.style_url("satellite-v1")
        assert "/styles/satellite-v1/style.json" in url


class TestMapTileStyles:
    def test_style_constants(self):
        assert MAP_TILE_STYLES["DAY"] == "day-v1"
        assert MAP_TILE_STYLES["NIGHT"] == "night-v1"
        assert MAP_TILE_STYLES["SATELLITE"] == "satellite-v1"
