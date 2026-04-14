"""Unit tests for NDAMapsError and error mapping."""

import pytest

from ndamaps.core.errors import (
    NDAMapsError,
    NDAMapsErrorCode,
    map_http_status_to_error_code,
    map_response_status_to_error,
    RETRYABLE_STATUS_CODES,
)


class TestNDAMapsError:
    def test_error_has_code_and_message(self):
        err = NDAMapsError(NDAMapsErrorCode.INVALID_API_KEY, "Bad key")
        assert err.code == NDAMapsErrorCode.INVALID_API_KEY
        assert str(err) == "Bad key"
        assert err.status_code is None
        assert err.raw_body is None

    def test_error_with_status_code(self):
        err = NDAMapsError(NDAMapsErrorCode.NETWORK_ERROR, "fail", 500, {"detail": "err"})
        assert err.status_code == 500
        assert err.raw_body == {"detail": "err"}

    def test_error_is_exception(self):
        err = NDAMapsError(NDAMapsErrorCode.UNKNOWN, "oops")
        assert isinstance(err, Exception)

    def test_error_repr(self):
        err = NDAMapsError(NDAMapsErrorCode.INVALID_FORCODE, "bad code")
        assert "INVALID_FORCODE" in repr(err)


class TestMapHttpStatus:
    def test_400_is_invalid_params(self):
        assert map_http_status_to_error_code(400) == NDAMapsErrorCode.INVALID_PARAMS

    def test_401_is_invalid_api_key(self):
        assert map_http_status_to_error_code(401) == NDAMapsErrorCode.INVALID_API_KEY

    def test_403_is_invalid_api_key(self):
        assert map_http_status_to_error_code(403) == NDAMapsErrorCode.INVALID_API_KEY

    def test_404_is_place_not_found(self):
        assert map_http_status_to_error_code(404) == NDAMapsErrorCode.PLACE_NOT_FOUND

    def test_429_is_rate_limit(self):
        assert map_http_status_to_error_code(429) == NDAMapsErrorCode.RATE_LIMIT_EXCEEDED

    def test_500_is_network_error(self):
        assert map_http_status_to_error_code(500) == NDAMapsErrorCode.NETWORK_ERROR

    def test_502_is_network_error(self):
        assert map_http_status_to_error_code(502) == NDAMapsErrorCode.NETWORK_ERROR

    def test_unknown_status(self):
        assert map_http_status_to_error_code(418) == NDAMapsErrorCode.UNKNOWN


class TestMapResponseStatus:
    def test_ok_returns_none(self):
        assert map_response_status_to_error("OK") is None

    def test_invalid_forcodes(self):
        assert map_response_status_to_error("INVALID_FORCODES") == NDAMapsErrorCode.INVALID_FORCODE

    def test_not_found(self):
        assert map_response_status_to_error("NOT_FOUND") == NDAMapsErrorCode.PLACE_NOT_FOUND

    def test_zero_results(self):
        assert map_response_status_to_error("ZERO_RESULTS") == NDAMapsErrorCode.ZERO_RESULTS

    def test_invalid_request(self):
        assert map_response_status_to_error("INVALID_REQUEST") == NDAMapsErrorCode.INVALID_PARAMS


class TestRetryableStatusCodes:
    def test_contains_expected_codes(self):
        assert 429 in RETRYABLE_STATUS_CODES
        assert 500 in RETRYABLE_STATUS_CODES
        assert 502 in RETRYABLE_STATUS_CODES
        assert 503 in RETRYABLE_STATUS_CODES
        assert 504 in RETRYABLE_STATUS_CODES

    def test_does_not_contain_client_errors(self):
        assert 400 not in RETRYABLE_STATUS_CODES
        assert 401 not in RETRYABLE_STATUS_CODES
        assert 404 not in RETRYABLE_STATUS_CODES
