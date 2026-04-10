"""NDAMaps SDK — Error handling."""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional


class NDAMapsErrorCode(str, Enum):
    """Error codes for NDAMaps API errors."""
    INVALID_API_KEY = "INVALID_API_KEY"
    INVALID_FORCODE = "INVALID_FORCODE"
    PLACE_NOT_FOUND = "PLACE_NOT_FOUND"
    ZERO_RESULTS = "ZERO_RESULTS"
    INVALID_PARAMS = "INVALID_PARAMS"
    NETWORK_ERROR = "NETWORK_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    UNKNOWN = "UNKNOWN"


class NDAMapsError(Exception):
    """Custom exception for NDAMaps API errors."""

    def __init__(
        self,
        code: NDAMapsErrorCode,
        message: str,
        status_code: Optional[int] = None,
        raw_body: Any = None,
    ):
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.raw_body = raw_body

    def __repr__(self) -> str:
        return f"NDAMapsError(code={self.code.value!r}, message={str(self)!r}, status_code={self.status_code})"


# ── HTTP Status → Error Code ──────────────────

_HTTP_STATUS_MAP = {
    400: NDAMapsErrorCode.INVALID_PARAMS,
    401: NDAMapsErrorCode.INVALID_API_KEY,
    403: NDAMapsErrorCode.INVALID_API_KEY,
    404: NDAMapsErrorCode.PLACE_NOT_FOUND,
    429: NDAMapsErrorCode.RATE_LIMIT_EXCEEDED,
}


def map_http_status_to_error_code(status: int) -> NDAMapsErrorCode:
    """Map HTTP status code to NDAMapsErrorCode."""
    if status in _HTTP_STATUS_MAP:
        return _HTTP_STATUS_MAP[status]
    if status >= 500:
        return NDAMapsErrorCode.NETWORK_ERROR
    return NDAMapsErrorCode.UNKNOWN


# ── Response Status → Error Code ──────────────

_RESPONSE_STATUS_MAP = {
    "INVALID_FORCODES": NDAMapsErrorCode.INVALID_FORCODE,
    "NOT_FOUND": NDAMapsErrorCode.PLACE_NOT_FOUND,
    "ZERO_RESULTS": NDAMapsErrorCode.ZERO_RESULTS,
    "INVALID_REQUEST": NDAMapsErrorCode.INVALID_PARAMS,
    "REQUEST_DENIED": NDAMapsErrorCode.INVALID_API_KEY,
    "OVER_QUERY_LIMIT": NDAMapsErrorCode.RATE_LIMIT_EXCEEDED,
}


def map_response_status_to_error(status: str) -> Optional[NDAMapsErrorCode]:
    """Map API response status string to NDAMapsErrorCode, or None if OK."""
    if status == "OK":
        return None
    return _RESPONSE_STATUS_MAP.get(status)


# ── Retryable status codes ────────────────────

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
