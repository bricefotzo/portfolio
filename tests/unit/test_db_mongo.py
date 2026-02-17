"""Tests unitaires — Connexion MongoDB.

Vérifier que le client Motor et la base sont créés correctement
à partir de la configuration (sans ouvrir de vraie connexion).

Commande :
    uv run pytest tests/unit/test_db_mongo.py -v

Fichier à implémenter :
    packages/backend/src/backend/db/mongo.py

À compléter :
    get_mongo_db() — créer le client Motor avec settings.mongo_url, retourner client[settings.mongo_db]
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.sprint1


@pytest.fixture(autouse=True)
def reset_mongo_singleton():
    """Réinitialise le singleton entre chaque test."""
    import backend.db.mongo as mongo_module

    old_client = mongo_module._client
    mongo_module._client = None
    yield
    mongo_module._client = old_client


class TestGetMongoDb:
    """mongo.get_mongo_db() — Client et base MongoDB."""

    def test_creates_client_with_url_and_returns_db(self, reset_mongo_singleton):
        """Doit créer le client avec mongo_url et retourner client[mongo_db]."""
        from backend.db import mongo

        mock_settings = MagicMock()
        mock_settings.mongo_url = "mongodb://localhost:27017"
        mock_settings.mongo_db = "smartcity"
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_client.__getitem__ = MagicMock(return_value=mock_db)

        with (
            patch("backend.db.mongo.get_settings", return_value=mock_settings),
            patch(
                "backend.db.mongo.AsyncIOMotorClient",
                return_value=mock_client,
            ) as client_mock,
        ):
            db = mongo.get_mongo_db()

        assert db is mock_db
        client_mock.assert_called_once_with("mongodb://localhost:27017")
        mock_client.__getitem__.assert_called_with("smartcity")

    def test_returns_same_db_on_second_call(self, reset_mongo_singleton):
        """Doit retourner la même base (singleton)."""
        from backend.db import mongo

        mock_db = MagicMock()
        mock_client = MagicMock()
        mock_client.__getitem__ = MagicMock(return_value=mock_db)

        with (
            patch("backend.db.mongo.get_settings") as settings_mock,
            patch("backend.db.mongo.AsyncIOMotorClient", return_value=mock_client),
        ):
            def get_settings_side_effect():
                s = MagicMock()
                s.mongo_url = "mongodb://localhost"
                s.mongo_db = "smartcity"
                return s

            settings_mock.side_effect = get_settings_side_effect
            first = mongo.get_mongo_db()
            second = mongo.get_mongo_db()

        assert first is second
