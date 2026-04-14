"""Unit tests for SessionManager."""

import time
from unittest.mock import patch

from ndamaps.core.session import SessionManager


class TestSessionManager:
    def test_get_or_create_returns_uuid(self):
        sm = SessionManager()
        token = sm.get_or_create()
        assert token is not None
        assert len(token) == 36  # UUID v4 format
        assert token.count("-") == 4

    def test_get_or_create_reuses_token(self):
        sm = SessionManager()
        t1 = sm.get_or_create()
        t2 = sm.get_or_create()
        assert t1 == t2

    def test_get_current_returns_none_initially(self):
        sm = SessionManager()
        assert sm.get_current() is None

    def test_get_current_returns_token_after_create(self):
        sm = SessionManager()
        created = sm.get_or_create()
        current = sm.get_current()
        assert created == current

    def test_reset_clears_token(self):
        sm = SessionManager()
        sm.get_or_create()
        sm.reset()
        assert sm.get_current() is None

    def test_expired_token_generates_new(self):
        sm = SessionManager()
        t1 = sm.get_or_create()

        # Simulate token created 6 minutes ago
        sm._created_at = time.time() - 360

        t2 = sm.get_or_create()
        assert t1 != t2

    def test_expired_get_current_returns_none(self):
        sm = SessionManager()
        sm.get_or_create()

        # Simulate expired
        sm._created_at = time.time() - 360

        assert sm.get_current() is None
