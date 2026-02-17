"""Tests unitaires — Connexion PostgreSQL.

Vérifier que l'engine et la session factory sont créés correctement
à partir de la configuration (sans ouvrir de vraie connexion).

Commande :
    uv run pytest tests/unit/test_db_postgres.py -v

Fichier à implémenter :
    packages/backend/src/backend/db/postgres.py

À compléter :
    get_engine() — créer l'engine async avec settings.postgres_url
    get_session_factory() — créer la session factory avec get_engine()
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.sprint1


@pytest.fixture(autouse=True)
def reset_postgres_singletons():
    """Réinitialise les singletons entre chaque test pour isoler les mocks."""
    import backend.db.postgres as postgres_module

    old_engine = postgres_module._engine
    old_factory = postgres_module._session_factory
    postgres_module._engine = None
    postgres_module._session_factory = None
    yield
    postgres_module._engine = old_engine
    postgres_module._session_factory = old_factory


class TestGetEngine:
    """postgres.get_engine() — Création du moteur SQLAlchemy async."""

    def test_returns_engine_from_settings(self, reset_postgres_singletons):
        """Doit créer un engine avec l'URL fournie par get_settings()."""
        from backend.db import postgres

        mock_settings = MagicMock()
        mock_settings.postgres_url = "postgresql+asyncpg://user:pass@localhost/db"
        mock_settings.debug = False
        mock_engine = MagicMock()

        with (
            patch("backend.db.postgres.get_settings", return_value=mock_settings),
            patch(
                "backend.db.postgres.create_async_engine",
                return_value=mock_engine,
            ) as create_mock,
        ):
            engine = postgres.get_engine()

        assert engine is mock_engine
        create_mock.assert_called_once_with(
            "postgresql+asyncpg://user:pass@localhost/db",
            echo=False,
        )

    def test_returns_same_engine_on_second_call(self, reset_postgres_singletons):
        """Doit retourner le même engine (singleton)."""
        from backend.db import postgres

        mock_settings = MagicMock()
        mock_settings.postgres_url = "postgresql+asyncpg://localhost/db"
        mock_settings.debug = False
        mock_engine = MagicMock()

        with (
            patch("backend.db.postgres.get_settings", return_value=mock_settings),
            patch("backend.db.postgres.create_async_engine", return_value=mock_engine),
        ):
            first = postgres.get_engine()
            second = postgres.get_engine()

        assert first is second


class TestGetSessionFactory:
    """postgres.get_session_factory() — Factory de sessions."""

    def test_returns_factory_using_engine(self, reset_postgres_singletons):
        """Doit créer une session factory à partir de get_engine()."""
        from backend.db import postgres

        mock_engine = MagicMock()
        mock_factory = MagicMock()

        with (
            patch("backend.db.postgres.get_engine", return_value=mock_engine),
            patch(
                "backend.db.postgres.async_sessionmaker",
                return_value=mock_factory,
            ) as sessionmaker_mock,
        ):
            factory = postgres.get_session_factory()

        assert factory is mock_factory
        sessionmaker_mock.assert_called_once_with(
            mock_engine,
            expire_on_commit=False,
        )

    def test_returns_same_factory_on_second_call(self, reset_postgres_singletons):
        """Doit retourner la même factory (singleton)."""
        from backend.db import postgres

        mock_factory = MagicMock()
        with (
            patch("backend.db.postgres.get_engine", return_value=MagicMock()),
            patch("backend.db.postgres.async_sessionmaker", return_value=mock_factory),
        ):
            first = postgres.get_session_factory()
            second = postgres.get_session_factory()

        assert first is second
