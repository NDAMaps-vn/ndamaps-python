"""Unit tests for Forcodes module."""

from unittest.mock import MagicMock

import pytest

from ndamaps.core.client import HttpClient
from ndamaps.core.errors import NDAMapsError, NDAMapsErrorCode
from ndamaps.modules.forcodes import ForcodesModule


MOCK_ENCODE_RESPONSE = {
    "forcodes": "HN4TZUZBPKRN0F",
    "lat": 20.990396,
    "lng": 105.868825,
    "resolution": 13,
    "admin_code": "HN",
    "status": "OK",
}

MOCK_DECODE_RESPONSE = {
    "forcodes": "HN4TZUZBPKRN0F",
    "lat": 20.990396,
    "lng": 105.868825,
    "resolution": 13,
    "status": "OK",
}

MOCK_DECODE_INVALID = {
    "forcodes": "INVALID",
    "lat": None,
    "lng": None,
    "resolution": None,
    "status": "INVALID_FORCODES",
}


class TestForcodeEncode:
    def setup_method(self):
        self.http = MagicMock(spec=HttpClient)
        self.forcodes = ForcodesModule(self.http)

    def test_encode_returns_forcode(self):
        self.http.get.return_value = MOCK_ENCODE_RESPONSE
        result = self.forcodes.encode(lat=20.990396, lng=105.868825)
        assert result["forcodes"] == "HN4TZUZBPKRN0F"
        assert result["admin_code"] == "HN"
        assert result["status"] == "OK"

    def test_encode_with_resolution(self):
        self.http.get.return_value = MOCK_ENCODE_RESPONSE
        self.forcodes.encode(lat=20.990396, lng=105.868825, resolution=11)
        call_args = self.http.get.call_args
        query = call_args[0][2] if len(call_args[0]) > 2 else call_args[1].get("params", {})
        assert query.get("resolution") == 11

    def test_encode_calls_correct_endpoint(self):
        self.http.get.return_value = MOCK_ENCODE_RESPONSE
        self.forcodes.encode(lat=20.99, lng=105.87)
        call_args = self.http.get.call_args
        assert call_args[0][1] == "/forcodes/encode"


class TestForcodeDecode:
    def setup_method(self):
        self.http = MagicMock(spec=HttpClient)
        self.forcodes = ForcodesModule(self.http)

    def test_decode_returns_coordinates(self):
        self.http.get.return_value = MOCK_DECODE_RESPONSE
        result = self.forcodes.decode(forcodes="HN4TZUZBPKRN0F")
        assert result["lat"] == pytest.approx(20.990396)
        assert result["lng"] == pytest.approx(105.868825)
        assert result["status"] == "OK"

    def test_decode_invalid_throws_error(self):
        self.http.get.return_value = MOCK_DECODE_INVALID
        with pytest.raises(NDAMapsError) as exc_info:
            self.forcodes.decode(forcodes="INVALID")

        assert exc_info.value.code == NDAMapsErrorCode.INVALID_FORCODE
        assert "INVALID" in str(exc_info.value)

    def test_decode_calls_correct_endpoint(self):
        self.http.get.return_value = MOCK_DECODE_RESPONSE
        self.forcodes.decode(forcodes="HN4TZUZBPKRN0F")
        call_args = self.http.get.call_args
        assert call_args[0][1] == "/forcodes/decode"
