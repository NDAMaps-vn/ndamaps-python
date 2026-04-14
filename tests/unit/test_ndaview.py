"""Unit tests for NDAView module."""

from unittest.mock import MagicMock

from ndamaps.core.client import HttpClient
from ndamaps.core.types import LatLng
from ndamaps.modules.ndaview import NdaViewModule


MOCK_SEARCH_RESULT = {
    "type": "FeatureCollection",
    "features": [
        {
            "id": "e213daed-3ae2-4259-940b-444a4056c101",
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [105.788, 21.033]},
            "assets": {
                "thumb": {"href": "https://example.com/thumb.jpg"},
                "sd": {"href": "https://example.com/sd.jpg"},
                "hd": {"href": "https://example.com/hd.jpg"},
            },
            "properties": {"datetime": "2024-01-15T10:30:00Z"},
        }
    ],
}


class TestNdaViewStaticThumbnail:
    def setup_method(self):
        self.http = MagicMock(spec=HttpClient)
        self.http.api_key = "TEST_KEY"
        self.ndaview = NdaViewModule(self.http, "https://api-view.example.com/v1")

    def test_thumbnail_url_with_id(self):
        url = self.ndaview.static_thumbnail_url(id="e213daed-3ae2-4259-940b-444a4056c101")
        assert "thumbnail.jpeg" in url
        assert "id=e213daed" in url
        assert "apikey=TEST_KEY" in url

    def test_thumbnail_url_with_coordinates(self):
        url = self.ndaview.static_thumbnail_url(
            place_position=LatLng(21.033, 105.788)
        )
        assert "place_position=105.788" in url
        assert "thumbnail.jpeg" in url

    def test_thumbnail_url_with_yaw_pitch(self):
        url = self.ndaview.static_thumbnail_url(
            id="test-uuid", yaw=276.0, pitch=20.0
        )
        assert "yaw=276" in url
        assert "pitch=20" in url


class TestNdaViewSearch:
    def setup_method(self):
        self.http = MagicMock(spec=HttpClient)
        self.http.api_key = "TEST_KEY"
        self.ndaview = NdaViewModule(self.http, "https://api-view.example.com/v1")

    def test_search_returns_feature_collection(self):
        self.http.get.return_value = MOCK_SEARCH_RESULT
        result = self.ndaview.search(
            place_position=LatLng(21.033, 105.788), limit=5
        )
        assert result["type"] == "FeatureCollection"
        assert len(result["features"]) == 1

    def test_search_calls_correct_endpoint(self):
        self.http.get.return_value = MOCK_SEARCH_RESULT
        self.ndaview.search(place_position=LatLng(21.033, 105.788))
        call_args = self.http.get.call_args
        assert call_args[0][1] == "/search"

    def test_search_with_bbox(self):
        self.http.get.return_value = MOCK_SEARCH_RESULT
        self.ndaview.search(bbox="105.0,20.0,106.0,22.0")
        call_args = self.http.get.call_args
        query = call_args[0][2] if len(call_args[0]) > 2 else call_args[1].get("params", {})
        assert query.get("bbox") == "105.0,20.0,106.0,22.0"
