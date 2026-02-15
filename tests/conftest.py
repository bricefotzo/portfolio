"""Configuration pytest — fixtures partagées."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture(scope="session")
def client():
    """Client de test FastAPI (synchrone).

    raise_server_exceptions=False : les erreurs serveur (ex. DB indisponible)
    sont retournées comme des réponses HTTP 500 au lieu de lever une exception
    dans le test. Cela permet aux tests de passer même sans bases de données.
    """
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
