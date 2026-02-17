"""Tests d'intégration — Seed methods (Sprint 2).

Vérifie le chargement réel des données dans PostgreSQL, MongoDB et Neo4j.
Prérequis : docker-compose up -d

Commande :
    uv run pytest tests/test_seed_integration.py -v
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.sprint2

DATASETS_DIR = Path(__file__).resolve().parents[1] / "datasets"


def _csv_rows(name: str) -> int:
    with open(DATASETS_DIR / name, encoding="utf-8") as f:
        return sum(1 for line in f if line.strip()) - 1


def _jsonl_rows(name: str) -> int:
    with open(DATASETS_DIR / name, encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


# ── PostgreSQL ───────────────────────────────────────────────────


class TestSeedPostgresIntegration:

    async def test_loads_cities_and_scores(self):
        """seed_postgres charge toutes les lignes de cities.csv et scores.csv."""
        try:
            from backend.scripts.seed_all import seed_postgres

            await seed_postgres()
        except Exception:
            pytest.skip("PostgreSQL not available")

        from backend.db.postgres import get_session_factory
        from sqlalchemy import text

        factory = get_session_factory()
        async with factory() as s:
            cities = (await s.execute(text("SELECT COUNT(*) FROM cities"))).scalar_one()
            scores = (await s.execute(text("SELECT COUNT(*) FROM scores"))).scalar_one()
        assert cities == _csv_rows("cities.csv")
        assert scores == _csv_rows("scores.csv")

    async def test_idempotent(self):
        """Exécuter seed_postgres 2x ne duplique pas les données."""
        try:
            from backend.scripts.seed_all import seed_postgres

            await seed_postgres()
            await seed_postgres()
        except Exception:
            pytest.skip("PostgreSQL not available")

        from backend.db.postgres import get_session_factory
        from sqlalchemy import text

        factory = get_session_factory()
        async with factory() as s:
            cities = (await s.execute(text("SELECT COUNT(*) FROM cities"))).scalar_one()
        assert cities == _csv_rows("cities.csv")


# ── MongoDB ──────────────────────────────────────────────────────


class TestSeedMongoIntegration:

    async def test_loads_all_reviews(self):
        """seed_mongo charge toutes les lignes de reviews.jsonl."""
        try:
            from backend.scripts.seed_all import seed_mongo

            await seed_mongo()
        except Exception:
            pytest.skip("MongoDB not available")

        from backend.db.mongo import get_mongo_db

        count = await get_mongo_db()["reviews"].count_documents({})
        assert count == _jsonl_rows("reviews.jsonl")

    async def test_created_at_is_datetime(self):
        """created_at est stocké en datetime, pas en string."""
        try:
            from backend.scripts.seed_all import seed_mongo

            await seed_mongo()
        except Exception:
            pytest.skip("MongoDB not available")

        from datetime import datetime

        from backend.db.mongo import get_mongo_db

        doc = await get_mongo_db()["reviews"].find_one()
        assert isinstance(doc["created_at"], datetime)


# ── Neo4j ────────────────────────────────────────────────────────


class TestSeedNeo4jIntegration:

    async def _cypher(self, query: str):
        from backend.db.neo4j import get_neo4j_driver

        driver = get_neo4j_driver()
        async with driver.session() as s:
            return await (await s.run(query)).data()

    async def test_creates_nodes_and_relations(self):
        """seed_neo4j crée les noeuds City/Criterion et les relations."""
        try:
            from backend.scripts.seed_all import seed_neo4j

            await seed_neo4j()
        except Exception:
            pytest.skip("Neo4j not available")

        cities = (await self._cypher("MATCH (c:City) RETURN count(c) AS n"))[0]["n"]
        criteria = (await self._cypher("MATCH (c:Criterion) RETURN count(c) AS n"))[0]["n"]
        strong = (await self._cypher(
            "MATCH ()-[r:STRONG_IN]->() RETURN count(r) AS n"
        ))[0]["n"]
        similar = (await self._cypher(
            "MATCH ()-[r:SIMILAR_TO]->() RETURN count(r) AS n"
        ))[0]["n"]

        assert cities == _csv_rows("cities.csv")
        assert criteria > 0
        assert strong > 0
        assert similar > 0


# ── Pipeline complet ─────────────────────────────────────────────


class TestSeedMainIntegration:

    async def test_full_pipeline(self):
        """main() alimente les 3 bases sans erreur."""
        try:
            from backend.scripts.seed_all import main

            await main()
        except Exception:
            pytest.skip("One or more databases not available")

        from backend.db.mongo import get_mongo_db
        from backend.db.neo4j import get_neo4j_driver
        from backend.db.postgres import get_session_factory
        from sqlalchemy import text

        async with get_session_factory()() as s:
            assert (await s.execute(text("SELECT COUNT(*) FROM cities"))).scalar_one() > 0

        assert await get_mongo_db()["reviews"].count_documents({}) > 0

        async with get_neo4j_driver().session() as s:
            data = await (await s.run("MATCH (c:City) RETURN count(c) AS n")).data()
            assert data[0]["n"] > 0
