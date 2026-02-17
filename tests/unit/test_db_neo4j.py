"""Tests unitaires — Connexion Neo4j.

Vérifier que le driver Neo4j est créé correctement
à partir de la configuration (sans ouvrir de vraie connexion).

Commande :
    uv run pytest tests/unit/test_db_neo4j.py -v

Fichier à implémenter :
    packages/backend/src/backend/db/neo4j.py

À compléter :
    get_neo4j_driver() — créer le driver avec AsyncGraphDatabase.driver(uri, auth=(user, password))
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.sprint1


@pytest.fixture(autouse=True)
def reset_neo4j_singleton():
    """Réinitialise le singleton entre chaque test."""
    import backend.db.neo4j as neo4j_module

    old_driver = neo4j_module._driver
    neo4j_module._driver = None
    yield
    neo4j_module._driver = old_driver


class TestGetNeo4jDriver:
    """neo4j.get_neo4j_driver() — Driver Neo4j async."""

    def test_creates_driver_with_uri_and_auth(self, reset_neo4j_singleton):
        """Doit créer le driver avec l'URI et les identifiants de get_settings()."""
        from backend.db import neo4j

        mock_settings = MagicMock()
        mock_settings.neo4j_uri = "bolt://localhost:7687"
        mock_settings.neo4j_user = "neo4j"
        mock_settings.neo4j_password = "secret"
        mock_driver = MagicMock()

        with (
            patch("backend.db.neo4j.get_settings", return_value=mock_settings),
            patch(
                "backend.db.neo4j.AsyncGraphDatabase",
            ) as graph_mock,
        ):
            graph_mock.driver = MagicMock(return_value=mock_driver)
            driver = neo4j.get_neo4j_driver()

        assert driver is mock_driver
        graph_mock.driver.assert_called_once_with(
            "bolt://localhost:7687",
            auth=("neo4j", "secret"),
        )

    def test_returns_same_driver_on_second_call(self, reset_neo4j_singleton):
        """Doit retourner le même driver (singleton)."""
        from backend.db import neo4j

        mock_driver = MagicMock()
        mock_settings = MagicMock()
        mock_settings.neo4j_uri = "bolt://localhost:7687"
        mock_settings.neo4j_user = "neo4j"
        mock_settings.neo4j_password = "pass"

        with (
            patch("backend.db.neo4j.get_settings", return_value=mock_settings),
            patch("backend.db.neo4j.AsyncGraphDatabase") as graph_mock,
        ):
            graph_mock.driver = MagicMock(return_value=mock_driver)
            first = neo4j.get_neo4j_driver()
            second = neo4j.get_neo4j_driver()

        assert first is second
