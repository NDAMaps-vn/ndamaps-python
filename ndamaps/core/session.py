"""NDAMaps SDK — Session token management for billing optimization."""

from __future__ import annotations

import time
import uuid
from typing import Optional


class SessionManager:
    """Manages session tokens for autocomplete → placeDetail billing groups.

    Tokens are UUID v4 strings with a 5-minute TTL.
    After expiry, a new token is generated automatically.
    """

    SESSION_TTL_SECONDS = 300  # 5 minutes

    def __init__(self) -> None:
        self._token: Optional[str] = None
        self._created_at: float = 0.0

    def get_or_create(self) -> str:
        """Get current valid token or create a new one."""
        now = time.time()
        if self._token is None or (now - self._created_at) > self.SESSION_TTL_SECONDS:
            self._token = str(uuid.uuid4())
            self._created_at = now
        return self._token

    def get_current(self) -> Optional[str]:
        """Get current token if still valid, or None."""
        if self._token is None:
            return None
        if (time.time() - self._created_at) > self.SESSION_TTL_SECONDS:
            self._token = None
            return None
        return self._token

    def reset(self) -> None:
        """Clear the current session token."""
        self._token = None
        self._created_at = 0.0
