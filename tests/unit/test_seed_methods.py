"""Tests unitaires — Seed methods (Sprint 2).

Vérifie le comportement de chaque fonction seed avec des mocks DB.

Commande :
    uv run pytest tests/unit/test_seed_methods.py -v
    uv run pytest -m sprint2 -v
"""

from __future__ import annotations

from datetime import datetime
from io import StringIO
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = pytest.mark.sprint2

# ── Helpers ──────────────────────────────────────────────────────

CITIES_CSV = (
    "id,name,department,region,population,description,latitude,longitude,overall_score\n"
    "1,Paris,Paris,Île-de-France,2161000,Capitale,48.8566,2.3522,6.8\n"
    "2,Lyon,Rhône,Auvergne-Rhône-Alpes,516092,Métropole,45.764,4.835,7.5\n"
)

SCORES_CSV = (
    "city_id,category,label,score\n"
    "1,sante,Santé,7.8\n"
    "1,transport,Transports,9.0\n"
    "2,sante,Santé,8.0\n"
)

REVIEWS_JSONL = (
    '{"city_id":1,"author":"Marie D.","rating":4,"comment":"Super","tags":["culture"],'
    '"created_at":"2024-09-15T10:30:00"}\n'
    '{"city_id":2,"author":"Sophie M.","rating":5,"comment":"Top","tags":["gastro"],'
    '"created_at":"2024-10-01T09:00:00"}\n'
)


def _fake_open(files: dict[str, str]):
    """Side-effect for builtins.open that serves in-memory CSV/JSONL."""
    real_open = open

    def _opener(path, *args, **kwargs):
        for suffix, content in files.items():
            if str(path).endswith(suffix):
                return StringIO(content)
        return real_open(path, *args, **kwargs)

    return _opener


def _pg_mocks():
    """Mock session + factory pour PostgreSQL. Retourne (session, factory)."""
    session = AsyncMock()
    factory = MagicMock()
    ctx = AsyncMock()
    ctx.__aenter__ = AsyncMock(return_value=session)
    ctx.__aexit__ = AsyncMock(return_value=False)
    factory.return_value = ctx
    return session, factory


def _sql_texts(session) -> list[str]:
    """Extrait les requêtes SQL enregistrées par le mock session."""
    return [
        str(c.args[0].text) if hasattr(c.args[0], "text") else str(c.args[0])
        for c in session.execute.call_args_list
    ]


# ── seed_postgres ────────────────────────────────────────────────


class TestSeedPostgres:

    async def test_creates_tables_and_inserts_data(self):
        """seed_postgres doit créer les tables, puis insérer cities et scores."""
        session, factory = _pg_mocks()
        files = {"cities.csv": CITIES_CSV, "scores.csv": SCORES_CSV}

        with (
            patch("backend.scripts.seed_all.get_session_factory", return_value=factory),
            patch("builtins.open", side_effect=_fake_open(files)),
        ):
            from backend.scripts.seed_all import seed_postgres

            await seed_postgres()

        sqls = _sql_texts(session)
        assert sum("create table" in s.lower() for s in sqls) >= 2
        assert sum("insert into cities" in s.lower() for s in sqls) == 2
        assert sum("insert into scores" in s.lower() for s in sqls) == 3
        assert session.commit.await_count >= 3

    async def test_deletes_before_insert(self):
        """seed_postgres doit vider les tables avant de ré-insérer (idempotence)."""
        session, factory = _pg_mocks()
        files = {"cities.csv": CITIES_CSV, "scores.csv": SCORES_CSV}

        with (
            patch("backend.scripts.seed_all.get_session_factory", return_value=factory),
            patch("builtins.open", side_effect=_fake_open(files)),
        ):
            from backend.scripts.seed_all import seed_postgres

            await seed_postgres()

        sqls = _sql_texts(session)
        assert sum("delete" in s.lower() for s in sqls) >= 2


# ── seed_mongo ───────────────────────────────────────────────────


class TestSeedMongo:

    def _mongo_mocks(self):
        collection = MagicMock()
        collection.delete_many = AsyncMock()
        collection.insert_many = AsyncMock()
        db = MagicMock()
        db.__getitem__ = MagicMock(return_value=collection)
        return collection, db

    async def test_clears_and_inserts_reviews(self):
        """seed_mongo doit vider puis insérer tous les documents JSONL."""
        collection, db = self._mongo_mocks()
        files = {"reviews.jsonl": REVIEWS_JSONL}

        with (
            patch("backend.scripts.seed_all.get_mongo_db", return_value=db),
            patch("builtins.open", side_effect=_fake_open(files)),
        ):
            from backend.scripts.seed_all import seed_mongo

            await seed_mongo()

        collection.delete_many.assert_awaited_once_with({})
        collection.insert_many.assert_awaited_once()
        docs = collection.insert_many.call_args[0][0]
        assert len(docs) == 2

    async def test_parses_created_at_to_datetime(self):
        """Les champs created_at string doivent être convertis en datetime."""
        collection, db = self._mongo_mocks()
        files = {"reviews.jsonl": REVIEWS_JSONL}

        with (
            patch("backend.scripts.seed_all.get_mongo_db", return_value=db),
            patch("builtins.open", side_effect=_fake_open(files)),
        ):
            from backend.scripts.seed_all import seed_mongo

            await seed_mongo()

        docs = collection.insert_many.call_args[0][0]
        for doc in docs:
            assert isinstance(doc["created_at"], datetime)


# ── seed_neo4j ───────────────────────────────────────────────────


class TestSeedNeo4j:

    def _neo4j_mocks(self):
        session = AsyncMock()
        driver = MagicMock()
        ctx = AsyncMock()
        ctx.__aenter__ = AsyncMock(return_value=session)
        ctx.__aexit__ = AsyncMock(return_value=False)
        driver.session = MagicMock(return_value=ctx)
        return session, driver

    def _cypher_texts(self, session) -> list[str]:
        return [str(c.args[0]) for c in session.run.call_args_list]

    async def test_creates_nodes_and_relations(self):
        """seed_neo4j doit créer City, Criterion, STRONG_IN et SIMILAR_TO."""
        session, driver = self._neo4j_mocks()
        files = {"cities.csv": CITIES_CSV, "scores.csv": SCORES_CSV}

        with (
            patch("backend.scripts.seed_all.get_neo4j_driver", return_value=driver),
            patch("builtins.open", side_effect=_fake_open(files)),
        ):
            from backend.scripts.seed_all import seed_neo4j

            await seed_neo4j()

        cyphers = self._cypher_texts(session)
        assert any("DETACH DELETE" in s for s in cyphers), "Doit nettoyer le graphe"
        assert any("Criterion" in s and "MERGE" in s for s in cyphers), "Doit créer Criterion"
        assert any("City" in s and "MERGE" in s for s in cyphers), "Doit créer City"
        assert any("STRONG_IN" in s for s in cyphers), "Doit créer STRONG_IN"
        assert any("SIMILAR_TO" in s for s in cyphers), "Doit créer SIMILAR_TO"


# ── main ─────────────────────────────────────────────────────────


class TestSeedMain:

    async def test_main_calls_all_seeds_in_order(self):
        """main() doit appeler seed_postgres, seed_mongo, seed_neo4j dans l'ordre."""
        call_order = []

        with (
            patch("backend.scripts.seed_all.seed_postgres", new_callable=AsyncMock,
                  side_effect=lambda: call_order.append("pg")),
            patch("backend.scripts.seed_all.seed_mongo", new_callable=AsyncMock,
                  side_effect=lambda: call_order.append("mongo")),
            patch("backend.scripts.seed_all.seed_neo4j", new_callable=AsyncMock,
                  side_effect=lambda: call_order.append("neo4j")),
        ):
            from backend.scripts.seed_all import main

            await main()

        assert call_order == ["pg", "mongo", "neo4j"]
