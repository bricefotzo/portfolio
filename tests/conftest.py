"""Configuration pytest — fixtures partagées."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture(scope="session")
def client():
    """Client de test FastAPI (synchrone)."""
    with TestClient(app) as c:
        yield c
