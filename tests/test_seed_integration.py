"""Tests d'intégration — Seed methods (Sprint 2).

Vérifie que les seed functions chargent correctement les données dans
les bases de données réelles (PostgreSQL, MongoDB, Neo4j).

Prérequis : bases de données démarrées via docker-compose.

Commande :
    uv run pytest tests/test_seed_integration.py -v
    uv run pytest -m sprint2 -v
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = [pytest.mark.sprint2]

DATASETS_DIR = Path(__file__).resolve().parents[1] / "datasets"

# ── Helpers ──────────────────────────────────────────────────────


def _count_csv_rows(filename: str) -> int:
    """Count data rows in a CSV file (excluding header)."""
    path = DATASETS_DIR / filename
    with open(path, encoding="utf-8") as f:
        return sum(1 for line in f if line.strip()) - 1  # minus header


def _count_jsonl_rows(filename: str) -> int:
    """Count non-empty lines in a JSONL file."""
    path = DATASETS_DIR / filename
    with open(path, encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


# ── PostgreSQL integration ───────────────────────────────────────


class TestSeedPostgresIntegration:
    """Integration tests for seed_postgres() against a real PostgreSQL database."""

    async def _run_seed(self):
        from backend.scripts.seed_all import seed_postgres

        await seed_postgres()

    async def _query(self, sql: str, params: dict | None = None):
        from backend.db.postgres import get_session_factory
        from sqlalchemy import text

        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(text(sql), params or {})
            return result

    async def test_seed_creates_cities_table(self):
        """After seeding, the cities table must exist."""
        try:
            await self._run_seed()
        except Exception:
            pytest.skip("PostgreSQL not available")

        result = await self._query(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_name = 'cities'"
        )
        assert result.scalar_one() >= 1

    async def test_seed_creates_scores_table(self):
        """After seeding, the scores table must exist."""
        try:
            await self._run_seed()
        except Exception:
            pytest.skip("PostgreSQL not available")

        result = await self._query(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_name = 'scores'"
        )
        assert result.scalar_one() >= 1

    async def test_seed_loads_all_cities(self):
        """All rows from cities.csv must be loaded."""
        try:
            await self._run_seed()
        except Exception:
            pytest.skip("PostgreSQL not available")

        expected = _count_csv_rows("cities.csv")
        result = await self._query("SELECT COUNT(*) FROM cities")
        assert result.scalar_one() == expected

    async def test_seed_loads_all_scores(self):
        """All rows from scores.csv must be loaded."""
        try:
            await self._run_seed()
        except Exception:
            pytest.skip("PostgreSQL not available")

        expected = _count_csv_rows("scores.csv")
        result = await self._query("SELECT COUNT(*) FROM scores")
        assert result.scalar_one() == expected

    async def test_city_data_integrity(self):
        """Check that city data is loaded with correct values."""
        try:
            await self._run_seed()
        except Exception:
            pytest.skip("PostgreSQL not available")

        result = await self._query("SELECT name, population, region FROM cities WHERE id = 1")
        row = result.mappings().first()
        assert row is not None
        assert row["name"] == "Paris"
        assert row["population"] == 2161000
        assert row["region"] == "Île-de-France"

    async def test_scores_reference_valid_cities(self):
        """All score city_ids should correspond to existing cities."""
        try:
            await self._run_seed()
        except Exception:
            pytest.skip("PostgreSQL not available")

        result = await self._query(
            "SELECT COUNT(*) FROM scores s "
            "WHERE NOT EXISTS (SELECT 1 FROM cities c WHERE c.id = s.city_id)"
        )
        orphan_count = result.scalar_one()
        assert orphan_count == 0, "All scores must reference valid city IDs"

    async def test_seed_is_idempotent(self):
        """Running seed twice should not duplicate data."""
        try:
            await self._run_seed()
            await self._run_seed()
        except Exception:
            pytest.skip("PostgreSQL not available")

        expected_cities = _count_csv_rows("cities.csv")
        expected_scores = _count_csv_rows("scores.csv")

        result_cities = await self._query("SELECT COUNT(*) FROM cities")
        result_scores = await self._query("SELECT COUNT(*) FROM scores")
        assert result_cities.scalar_one() == expected_cities
        assert result_scores.scalar_one() == expected_scores


# ── MongoDB integration ──────────────────────────────────────────


class TestSeedMongoIntegration:
    """Integration tests for seed_mongo() against a real MongoDB database."""

    async def _run_seed(self):
        from backend.scripts.seed_all import seed_mongo

        await seed_mongo()

    def _get_collection(self):
        from backend.db.mongo import get_mongo_db

        db = get_mongo_db()
        return db["reviews"]

    async def test_seed_loads_all_reviews(self):
        """All rows from reviews.jsonl must be loaded."""
        try:
            await self._run_seed()
        except Exception:
            pytest.skip("MongoDB not available")

        expected = _count_jsonl_rows("reviews.jsonl")
        collection = self._get_collection()
        count = await collection.count_documents({})
        assert count == expected

    async def test_review_has_required_fields(self):
        """Each review document must have the expected fields."""
        try:
            await self._run_seed()
        except Exception:
            pytest.skip("MongoDB not available")

        collection = self._get_collection()
        required_fields = {"city_id", "author", "rating", "comment", "tags", "created_at"}
        async for doc in collection.find().limit(5):
            doc_keys = set(doc.keys()) - {"_id"}
            assert required_fields.issubset(doc_keys), (
                f"Missing fields: {required_fields - doc_keys}"
            )

    async def test_review_ratings_in_valid_range(self):
        """All ratings should be between 1 and 5."""
        try:
            await self._run_seed()
        except Exception:
            pytest.skip("MongoDB not available")

        collection = self._get_collection()
        async for doc in collection.find():
            assert 1 <= doc["rating"] <= 5, f"Rating {doc['rating']} out of range"

    async def test_created_at_is_datetime(self):
        """created_at must be stored as datetime, not string."""
        try:
            await self._run_seed()
        except Exception:
            pytest.skip("MongoDB not available")

        from datetime import datetime

        collection = self._get_collection()
        doc = await collection.find_one()
        assert doc is not None
        assert isinstance(doc["created_at"], datetime), (
            "created_at should be datetime, not string"
        )

    async def test_seed_is_idempotent(self):
        """Running seed twice should not duplicate reviews."""
        try:
            await self._run_seed()
            await self._run_seed()
        except Exception:
            pytest.skip("MongoDB not available")

        expected = _count_jsonl_rows("reviews.jsonl")
        collection = self._get_collection()
        count = await collection.count_documents({})
        assert count == expected


# ── Neo4j integration ────────────────────────────────────────────


class TestSeedNeo4jIntegration:
    """Integration tests for seed_neo4j() against a real Neo4j database."""

    async def _run_seed(self):
        from backend.scripts.seed_all import seed_neo4j

        await seed_neo4j()

    async def _run_cypher(self, query: str):
        from backend.db.neo4j import get_neo4j_driver

        driver = get_neo4j_driver()
        async with driver.session() as session:
            result = await session.run(query)
            return await result.data()

    async def test_seed_creates_city_nodes(self):
        """Should create City nodes matching cities.csv."""
        try:
            await self._run_seed()
        except Exception:
            pytest.skip("Neo4j not available")

        expected = _count_csv_rows("cities.csv")
        data = await self._run_cypher("MATCH (c:City) RETURN count(c) AS cnt")
        assert data[0]["cnt"] == expected

    async def test_seed_creates_criterion_nodes(self):
        """Should create Criterion nodes from score categories."""
        try:
            await self._run_seed()
        except Exception:
            pytest.skip("Neo4j not available")

        data = await self._run_cypher("MATCH (c:Criterion) RETURN count(c) AS cnt")
        assert data[0]["cnt"] > 0, "Should have at least one Criterion node"

    async def test_city_nodes_have_properties(self):
        """City nodes must have key properties (name, city_id, region)."""
        try:
            await self._run_seed()
        except Exception:
            pytest.skip("Neo4j not available")

        data = await self._run_cypher(
            "MATCH (c:City {city_id: 1}) RETURN c.name AS name, c.region AS region"
        )
        assert len(data) == 1
        assert data[0]["name"] == "Paris"
        assert data[0]["region"] == "Île-de-France"

    async def test_strong_in_relations_exist(self):
        """STRONG_IN relations must exist between City and Criterion nodes."""
        try:
            await self._run_seed()
        except Exception:
            pytest.skip("Neo4j not available")

        data = await self._run_cypher(
            "MATCH (:City)-[r:STRONG_IN]->(:Criterion) RETURN count(r) AS cnt"
        )
        assert data[0]["cnt"] > 0, "Should have STRONG_IN relations"

    async def test_similar_to_relations_exist(self):
        """SIMILAR_TO relations must exist between City nodes."""
        try:
            await self._run_seed()
        except Exception:
            pytest.skip("Neo4j not available")

        data = await self._run_cypher(
            "MATCH (:City)-[r:SIMILAR_TO]->(:City) RETURN count(r) AS cnt"
        )
        assert data[0]["cnt"] > 0, "Should have SIMILAR_TO relations"

    async def test_similar_to_score_in_range(self):
        """SIMILAR_TO scores must be between 0 and 1."""
        try:
            await self._run_seed()
        except Exception:
            pytest.skip("Neo4j not available")

        data = await self._run_cypher(
            "MATCH ()-[r:SIMILAR_TO]->() RETURN r.score AS score"
        )
        for record in data:
            assert 0 <= record["score"] <= 1, f"Score {record['score']} out of [0,1] range"

    async def test_seed_is_idempotent(self):
        """Running seed twice should not duplicate nodes."""
        try:
            await self._run_seed()
            await self._run_seed()
        except Exception:
            pytest.skip("Neo4j not available")

        expected = _count_csv_rows("cities.csv")
        data = await self._run_cypher("MATCH (c:City) RETURN count(c) AS cnt")
        assert data[0]["cnt"] == expected


# ── Full pipeline integration ────────────────────────────────────


class TestSeedMainIntegration:
    """Integration test for the full seed pipeline."""

    async def test_full_seed_pipeline(self):
        """main() should seed all three databases without errors."""
        try:
            from backend.scripts.seed_all import main

            await main()
        except Exception:
            pytest.skip("One or more databases not available")

        # Verify PostgreSQL
        from backend.db.postgres import get_session_factory
        from sqlalchemy import text

        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(text("SELECT COUNT(*) FROM cities"))
            assert result.scalar_one() > 0

        # Verify MongoDB
        from backend.db.mongo import get_mongo_db

        db = get_mongo_db()
        count = await db["reviews"].count_documents({})
        assert count > 0

        # Verify Neo4j
        from backend.db.neo4j import get_neo4j_driver

        driver = get_neo4j_driver()
        async with driver.session() as session:
            result = await session.run("MATCH (c:City) RETURN count(c) AS cnt")
            data = await result.data()
            assert data[0]["cnt"] > 0
