"""Unit tests for Geocoding module."""

from unittest.mock import MagicMock

from ndamaps.core.client import HttpClient, MAPS_API_BASE
from ndamaps.modules.geocoding import GeocodingModule


MOCK_FORWARD_GOOGLE = {
    "results": [
        {
            "formatted_address": "12 Ngõ 1 Dịch Vọng Hậu, Cầu Giấy, Hà Nội",
            "geometry": {"location": {"lat": 21.037, "lng": 105.782}},
            "place_id": "forward123",
        }
    ],
    "status": "OK",
}

MOCK_FORWARD_OSM = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [105.782, 21.037]},
            "properties": {"label": "12 Ngõ 1 Dịch Vọng Hậu, Cầu Giấy, Hà Nội"},
        }
    ],
}

MOCK_REVERSE_GOOGLE = {
    "results": [
        {
            "formatted_address": "Lotte Mall Tây Hồ, Hà Nội",
            "geometry": {"location": {"lat": 21.076, "lng": 105.813}},
        }
    ],
    "status": "OK",
}


class TestForwardGeocode:
    def setup_method(self):
        self.http = MagicMock(spec=HttpClient)
        self.geocoding = GeocodingModule(self.http)

    def test_forward_google_format(self):
        self.http.get.return_value = MOCK_FORWARD_GOOGLE
        result = self.geocoding.forward(address="12 Ngõ 1 Dịch Vọng Hậu")
        assert result["status"] == "OK"
        assert len(result["results"]) == 1

    def test_forward_osm_format(self):
        self.http.get.return_value = MOCK_FORWARD_OSM
        result = self.geocoding.forward(text="12 Ngõ 1 Dịch Vọng Hậu")
        assert result["type"] == "FeatureCollection"

    def test_forward_calls_correct_endpoint(self):
        self.http.get.return_value = MOCK_FORWARD_GOOGLE
        self.geocoding.forward(address="test")
        call_args = self.http.get.call_args
        assert call_args[0][1] == "/geocode/forward"


class TestReverseGeocode:
    def setup_method(self):
        self.http = MagicMock(spec=HttpClient)
        self.geocoding = GeocodingModule(self.http)

    def test_reverse_google_format(self):
        self.http.get.return_value = MOCK_REVERSE_GOOGLE
        result = self.geocoding.reverse(latlng="21.076,105.813")
        assert result["status"] == "OK"
        assert len(result["results"]) == 1

    def test_reverse_calls_correct_endpoint(self):
        self.http.get.return_value = MOCK_REVERSE_GOOGLE
        self.geocoding.reverse(latlng="21.076,105.813")
        call_args = self.http.get.call_args
        assert call_args[0][1] == "/geocode/reverse"
