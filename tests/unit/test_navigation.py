"""Unit tests for Navigation module."""

from unittest.mock import MagicMock

from ndamaps.core.client import HttpClient
from ndamaps.core.types import LatLng
from ndamaps.modules.navigation import NavigationModule


MOCK_DIRECTIONS = {
    "geocoded_waypoints": [
        {"geocoder_status": "OK", "place_id": "orig123"},
        {"geocoder_status": "OK", "place_id": "dest123"},
    ],
    "routes": [
        {
            "legs": [
                {
                    "distance": {"text": "3.2 km", "value": 3200},
                    "duration": {"text": "8 mins", "value": 480},
                    "start_address": "Origin",
                    "end_address": "Destination",
                }
            ],
            "overview_polyline": {"points": "abc123"},
        }
    ],
}

MOCK_DISTANCE_MATRIX = {
    "sources_to_targets": [
        [{"distance": 2.5, "time": 300, "from_index": 0, "to_index": 0}]
    ],
    "locations": [{"lat": "21.03", "lon": "105.79"}],
    "units": "km",
}


class TestDirections:
    def setup_method(self):
        self.http = MagicMock(spec=HttpClient)
        self.nav = NavigationModule(self.http)

    def test_directions_single_destination(self):
        self.http.get.return_value = MOCK_DIRECTIONS
        result = self.nav.directions(
            origin="10.787,106.698", destination="10.791,106.702"
        )
        assert len(result["routes"]) == 1
        assert result["routes"][0]["legs"][0]["distance"]["text"] == "3.2 km"

    def test_directions_with_latlng_objects(self):
        self.http.get.return_value = MOCK_DIRECTIONS
        result = self.nav.directions(
            origin=LatLng(lat=10.787, lng=106.698),
            destination=LatLng(lat=10.791, lng=106.702),
        )

        call_args = self.http.get.call_args
        query = call_args[0][2] if len(call_args[0]) > 2 else call_args[1].get("params", {})
        assert query.get("origin") == "10.787,106.698"
        assert query.get("destination") == "10.791,106.702"

    def test_directions_multiple_destinations(self):
        self.http.get.return_value = MOCK_DIRECTIONS
        self.nav.directions(
            origin="10.787,106.698",
            destination=["10.791,106.702", "10.795,106.710"],
        )

        call_args = self.http.get.call_args
        query = call_args[0][2] if len(call_args[0]) > 2 else call_args[1].get("params", {})
        assert query.get("destination") == "10.791,106.702;10.795,106.710"

    def test_directions_calls_correct_endpoint(self):
        self.http.get.return_value = MOCK_DIRECTIONS
        self.nav.directions(origin="10.787,106.698", destination="10.791,106.702")
        call_args = self.http.get.call_args
        assert call_args[0][1] == "/direction"


class TestDistanceMatrix:
    def setup_method(self):
        self.http = MagicMock(spec=HttpClient)
        self.nav = NavigationModule(self.http)

    def test_distance_matrix_returns_result(self):
        self.http.get.return_value = MOCK_DISTANCE_MATRIX
        result = self.nav.distance_matrix(
            sources=[{"lat": "21.03", "lon": "105.79"}],
            targets=[{"lat": "21.05", "lon": "105.79"}],
        )
        assert result["units"] == "km"
        assert len(result["sources_to_targets"]) == 1

    def test_distance_matrix_calls_correct_endpoint(self):
        self.http.get.return_value = MOCK_DISTANCE_MATRIX
        self.nav.distance_matrix(
            sources=[{"lat": "21.03", "lon": "105.79"}],
            targets=[{"lat": "21.05", "lon": "105.79"}],
        )
        call_args = self.http.get.call_args
        assert call_args[0][1] == "/distancematrix"
