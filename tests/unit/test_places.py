"""Unit tests for Places module."""

from unittest.mock import MagicMock, patch

import pytest

from ndamaps.core.client import HttpClient, MAPS_API_BASE
from ndamaps.core.session import SessionManager
from ndamaps.modules.places import PlacesModule


MOCK_AUTOCOMPLETE_GOOGLE = {
    "predictions": [
        {
            "description": "Lotte Mall Tây Hồ, Hà Nội",
            "place_id": "abc123",
            "structured_formatting": {
                "main_text": "Lotte Mall Tây Hồ",
                "secondary_text": "Hà Nội",
            },
            "types": ["establishment"],
            "distance_meters": 1200,
            "has_child": False,
        }
    ],
    "status": "OK",
}

MOCK_AUTOCOMPLETE_OSM = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [105.788, 21.033]},
            "properties": {"id": "osm123", "name": "Lotte Mall", "label": "Lotte Mall, Hà Nội"},
        }
    ],
}

MOCK_PLACE_DETAIL = {
    "result": {
        "place_id": "abc123",
        "name": "Lotte Mall Tây Hồ",
        "formatted_address": "Lotte Mall Tây Hồ, Hà Nội",
        "geometry": {"location": {"lat": 21.033, "lng": 105.788}},
    },
    "status": "OK",
}


class TestPlacesAutocomplete:
    def setup_method(self):
        self.http = MagicMock(spec=HttpClient)
        self.session = SessionManager()
        self.places = PlacesModule(self.http, self.session)

    def test_autocomplete_google_format(self):
        self.http.get.return_value = MOCK_AUTOCOMPLETE_GOOGLE
        result = self.places.autocomplete(input="Lotte Mall")
        assert result["status"] == "OK"
        assert len(result["predictions"]) == 1
        assert result["predictions"][0]["place_id"] == "abc123"

    def test_autocomplete_osm_format(self):
        self.http.get.return_value = MOCK_AUTOCOMPLETE_OSM
        result = self.places.autocomplete(text="Lotte Mall")
        assert result["type"] == "FeatureCollection"
        assert len(result["features"]) == 1

    def test_autocomplete_auto_generates_session_token(self):
        self.http.get.return_value = MOCK_AUTOCOMPLETE_GOOGLE
        self.places.autocomplete(input="Lotte")

        call_args = self.http.get.call_args
        query = call_args[0][2] if len(call_args[0]) > 2 else call_args[1].get("params", {})
        assert "sessiontoken" in query

    def test_autocomplete_uses_provided_session_token(self):
        self.http.get.return_value = MOCK_AUTOCOMPLETE_GOOGLE
        self.places.autocomplete(input="Lotte", sessiontoken="custom-token")

        call_args = self.http.get.call_args
        query = call_args[0][2] if len(call_args[0]) > 2 else call_args[1].get("params", {})
        assert query.get("sessiontoken") == "custom-token"


class TestPlaceDetail:
    def setup_method(self):
        self.http = MagicMock(spec=HttpClient)
        self.session = SessionManager()
        self.places = PlacesModule(self.http, self.session)

    def test_place_detail_returns_result(self):
        self.http.get.return_value = MOCK_PLACE_DETAIL
        result = self.places.place_detail(ids="abc123")
        assert result["result"]["name"] == "Lotte Mall Tây Hồ"

    def test_place_detail_reuses_session_from_autocomplete(self):
        # First call autocomplete to create a session
        self.http.get.return_value = MOCK_AUTOCOMPLETE_GOOGLE
        self.places.autocomplete(input="Lotte")

        autocomplete_token = self.session.get_current()
        assert autocomplete_token is not None

        # Then call place_detail — should reuse the same token
        self.http.get.return_value = MOCK_PLACE_DETAIL
        self.places.place_detail(ids="abc123")

        call_args = self.http.get.call_args
        query = call_args[0][2] if len(call_args[0]) > 2 else call_args[1].get("params", {})
        assert query.get("sessiontoken") == autocomplete_token


class TestPlacesChildren:
    def setup_method(self):
        self.http = MagicMock(spec=HttpClient)
        self.session = SessionManager()
        self.places = PlacesModule(self.http, self.session)

    def test_children_calls_correct_endpoint(self):
        self.http.get.return_value = {"predictions": [], "status": "OK"}
        self.places.children(parent_id="parent123")

        call_args = self.http.get.call_args
        assert call_args[0][1] == "/place/children"


class TestPlacesNearby:
    def setup_method(self):
        self.http = MagicMock(spec=HttpClient)
        self.session = SessionManager()
        self.places = PlacesModule(self.http, self.session)

    def test_nearby_returns_feature_collection(self):
        mock_response = {"type": "FeatureCollection", "features": []}
        self.http.get.return_value = mock_response
        result = self.places.nearby(categories="restaurant")
        assert result["type"] == "FeatureCollection"
