"""Tests unitaires — Seed methods (Sprint 2).

Vérifie le comportement de chaque fonction seed avec des mocks
pour les connexions base de données.

Commande :
    uv run pytest tests/unit/test_seed_methods.py -v
    uv run pytest -m sprint2 -v
"""

from __future__ import annotations

import json
from datetime import datetime
from io import StringIO
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = pytest.mark.sprint2


# ── Helpers ──────────────────────────────────────────────────────


def _make_cities_csv(rows: list[dict] | None = None) -> str:
    """Build a minimal cities.csv string."""
    if rows is None:
        rows = [
            {
                "id": "1",
                "name": "Paris",
                "department": "Paris",
                "region": "Île-de-France",
                "population": "2161000",
                "description": "Capitale de la France",
                "latitude": "48.8566",
                "longitude": "2.3522",
                "overall_score": "6.8",
            },
            {
                "id": "2",
                "name": "Lyon",
                "department": "Rhône",
                "region": "Auvergne-Rhône-Alpes",
                "population": "516092",
                "description": "Métropole dynamique",
                "latitude": "45.7640",
                "longitude": "4.8357",
                "overall_score": "7.5",
            },
        ]
    header = "id,name,department,region,population,description,latitude,longitude,overall_score"
    lines = [header]
    for r in rows:
        lines.append(",".join(str(r[k]) for k in header.split(",")))
    return "\n".join(lines) + "\n"


def _make_scores_csv(rows: list[dict] | None = None) -> str:
    """Build a minimal scores.csv string."""
    if rows is None:
        rows = [
            {"city_id": "1", "category": "sante", "label": "Santé", "score": "7.8"},
            {"city_id": "1", "category": "transport", "label": "Transports", "score": "9.0"},
            {"city_id": "2", "category": "sante", "label": "Santé", "score": "8.0"},
        ]
    header = "city_id,category,label,score"
    lines = [header]
    for r in rows:
        lines.append(",".join(str(r[k]) for k in header.split(",")))
    return "\n".join(lines) + "\n"


def _make_reviews_jsonl(docs: list[dict] | None = None) -> str:
    """Build a minimal reviews.jsonl string."""
    if docs is None:
        docs = [
            {
                "city_id": 1,
                "author": "Marie D.",
                "rating": 4,
                "comment": "Paris est magique.",
                "tags": ["culture"],
                "created_at": "2024-09-15T10:30:00",
            },
            {
                "city_id": 2,
                "author": "Sophie M.",
                "rating": 5,
                "comment": "Lyon est parfaite.",
                "tags": ["gastronomie"],
                "created_at": "2024-10-01T09:00:00",
            },
        ]
    return "\n".join(json.dumps(d, ensure_ascii=False) for d in docs) + "\n"


def _file_opener(file_contents: dict[str, str]):
    """Return a side_effect function for builtins.open that serves in-memory content."""

    real_open = open

    def _open_side_effect(path, *args, **kwargs):
        path_str = str(path)
        for key, content in file_contents.items():
            if path_str.endswith(key):
                return StringIO(content)
        return real_open(path, *args, **kwargs)

    return _open_side_effect


def _make_pg_mocks():
    """Create PostgreSQL session and factory mocks. Returns (session, factory)."""
    session = AsyncMock()
    factory = MagicMock()
    ctx = AsyncMock()
    ctx.__aenter__ = AsyncMock(return_value=session)
    ctx.__aexit__ = AsyncMock(return_value=False)
    factory.return_value = ctx
    return session, factory


def _extract_sql(session_mock: AsyncMock) -> list[str]:
    """Extract SQL strings from a mocked session's execute call history."""
    result = []
    for call in session_mock.execute.call_args_list:
        arg = call.args[0]
        result.append(str(arg.text) if hasattr(arg, "text") else str(arg))
    return result


# ── seed_postgres ────────────────────────────────────────────────


class TestSeedPostgres:
    """Tests for seed_postgres()."""

    async def test_creates_tables(self):
        """seed_postgres must issue CREATE TABLE IF NOT EXISTS for cities and scores."""
        session, factory = _make_pg_mocks()
        files = {"cities.csv": _make_cities_csv(), "scores.csv": _make_scores_csv()}
        with (
            patch("backend.scripts.seed_all.get_session_factory", return_value=factory),
            patch("builtins.open", side_effect=_file_opener(files)),
        ):
            from backend.scripts.seed_all import seed_postgres

            await seed_postgres()

        sql_calls = _extract_sql(session)
        create_stmts = [s for s in sql_calls if "CREATE TABLE" in s.upper()]
        assert len(create_stmts) >= 2, "Should create both cities and scores tables"
        assert any("cities" in s for s in create_stmts)
        assert any("scores" in s for s in create_stmts)

    async def test_deletes_existing_data(self):
        """seed_postgres must DELETE existing rows before inserting."""
        session, factory = _make_pg_mocks()
        files = {"cities.csv": _make_cities_csv(), "scores.csv": _make_scores_csv()}
        with (
            patch("backend.scripts.seed_all.get_session_factory", return_value=factory),
            patch("builtins.open", side_effect=_file_opener(files)),
        ):
            from backend.scripts.seed_all import seed_postgres

            await seed_postgres()

        sql_calls = _extract_sql(session)
        delete_stmts = [s for s in sql_calls if "DELETE" in s.upper()]
        assert len(delete_stmts) >= 2, "Should delete from both cities and scores"

    async def test_inserts_cities(self):
        """seed_postgres must INSERT all rows from cities.csv."""
        session, factory = _make_pg_mocks()
        files = {"cities.csv": _make_cities_csv(), "scores.csv": _make_scores_csv()}
        with (
            patch("backend.scripts.seed_all.get_session_factory", return_value=factory),
            patch("builtins.open", side_effect=_file_opener(files)),
        ):
            from backend.scripts.seed_all import seed_postgres

            await seed_postgres()

        sql_calls = _extract_sql(session)
        city_inserts = [s for s in sql_calls if "insert into cities" in s.lower()]
        assert len(city_inserts) == 2, "Should insert 2 cities from test CSV"

    async def test_inserts_scores(self):
        """seed_postgres must INSERT all rows from scores.csv."""
        session, factory = _make_pg_mocks()
        files = {"cities.csv": _make_cities_csv(), "scores.csv": _make_scores_csv()}
        with (
            patch("backend.scripts.seed_all.get_session_factory", return_value=factory),
            patch("builtins.open", side_effect=_file_opener(files)),
        ):
            from backend.scripts.seed_all import seed_postgres

            await seed_postgres()

        sql_calls = _extract_sql(session)
        score_inserts = [s for s in sql_calls if "insert into scores" in s.lower()]
        assert len(score_inserts) == 3, "Should insert 3 scores from test CSV"

    async def test_commits_after_operations(self):
        """seed_postgres must call commit() multiple times."""
        session, factory = _make_pg_mocks()
        files = {"cities.csv": _make_cities_csv(), "scores.csv": _make_scores_csv()}
        with (
            patch("backend.scripts.seed_all.get_session_factory", return_value=factory),
            patch("builtins.open", side_effect=_file_opener(files)),
        ):
            from backend.scripts.seed_all import seed_postgres

            await seed_postgres()

        assert session.commit.await_count >= 3, (
            "Should commit at least 3 times (create, delete, insert cities, insert scores)"
        )

    async def test_insert_parameters_contain_city_data(self):
        """Verify inserted city parameters contain correct data."""
        session, factory = _make_pg_mocks()
        files = {"cities.csv": _make_cities_csv(), "scores.csv": _make_scores_csv()}
        with (
            patch("backend.scripts.seed_all.get_session_factory", return_value=factory),
            patch("builtins.open", side_effect=_file_opener(files)),
        ):
            from backend.scripts.seed_all import seed_postgres

            await seed_postgres()

        city_insert_params = []
        for call in session.execute.call_args_list:
            sql = str(call.args[0].text) if hasattr(call.args[0], "text") else str(call.args[0])
            if "insert into cities" in sql.lower() and len(call.args) > 1:
                city_insert_params.append(call.args[1])

        assert len(city_insert_params) == 2
        names = {p["name"] for p in city_insert_params}
        assert "Paris" in names
        assert "Lyon" in names

        paris = next(p for p in city_insert_params if p["name"] == "Paris")
        assert paris["id"] == 1
        assert paris["population"] == 2161000
        assert paris["latitude"] == pytest.approx(48.8566)
        assert paris["overall_score"] == pytest.approx(6.8)


# ── seed_mongo ───────────────────────────────────────────────────


def _make_mongo_mocks():
    """Create MongoDB collection and db mocks. Returns (collection, db)."""
    collection = MagicMock()
    collection.delete_many = AsyncMock()
    collection.insert_many = AsyncMock()
    db = MagicMock()
    db.__getitem__ = MagicMock(return_value=collection)
    return collection, db


class TestSeedMongo:
    """Tests for seed_mongo()."""

    async def test_clears_existing_reviews(self):
        """seed_mongo must delete_many({}) before inserting."""
        collection, db = _make_mongo_mocks()
        files = {"reviews.jsonl": _make_reviews_jsonl()}
        with (
            patch("backend.scripts.seed_all.get_mongo_db", return_value=db),
            patch("builtins.open", side_effect=_file_opener(files)),
        ):
            from backend.scripts.seed_all import seed_mongo

            await seed_mongo()

        collection.delete_many.assert_awaited_once_with({})

    async def test_inserts_reviews(self):
        """seed_mongo must call insert_many with all review documents."""
        collection, db = _make_mongo_mocks()
        files = {"reviews.jsonl": _make_reviews_jsonl()}
        with (
            patch("backend.scripts.seed_all.get_mongo_db", return_value=db),
            patch("builtins.open", side_effect=_file_opener(files)),
        ):
            from backend.scripts.seed_all import seed_mongo

            await seed_mongo()

        collection.insert_many.assert_awaited_once()
        inserted_docs = collection.insert_many.call_args[0][0]
        assert len(inserted_docs) == 2

    async def test_review_fields_preserved(self):
        """Inserted documents must retain all fields from JSONL."""
        collection, db = _make_mongo_mocks()
        files = {"reviews.jsonl": _make_reviews_jsonl()}
        with (
            patch("backend.scripts.seed_all.get_mongo_db", return_value=db),
            patch("builtins.open", side_effect=_file_opener(files)),
        ):
            from backend.scripts.seed_all import seed_mongo

            await seed_mongo()

        docs = collection.insert_many.call_args[0][0]
        doc = next(d for d in docs if d["author"] == "Marie D.")
        assert doc["city_id"] == 1
        assert doc["rating"] == 4
        assert doc["comment"] == "Paris est magique."
        assert doc["tags"] == ["culture"]

    async def test_created_at_parsed_as_datetime(self):
        """String created_at values must be parsed to datetime objects."""
        collection, db = _make_mongo_mocks()
        files = {"reviews.jsonl": _make_reviews_jsonl()}
        with (
            patch("backend.scripts.seed_all.get_mongo_db", return_value=db),
            patch("builtins.open", side_effect=_file_opener(files)),
        ):
            from backend.scripts.seed_all import seed_mongo

            await seed_mongo()

        docs = collection.insert_many.call_args[0][0]
        for doc in docs:
            assert isinstance(doc["created_at"], datetime), (
                "created_at should be converted from string to datetime"
            )

    async def test_skips_empty_lines(self):
        """Empty lines in JSONL should be skipped."""
        collection, db = _make_mongo_mocks()
        jsonl_with_blanks = (
            '{"city_id": 1, "author": "A", "rating": 3, "comment": "x", '
            '"tags": [], "created_at": "2024-01-01T00:00:00"}\n'
            "\n"
            "\n"
            '{"city_id": 2, "author": "B", "rating": 4, "comment": "y", '
            '"tags": [], "created_at": "2024-02-01T00:00:00"}\n'
        )
        files = {"reviews.jsonl": jsonl_with_blanks}
        with (
            patch("backend.scripts.seed_all.get_mongo_db", return_value=db),
            patch("builtins.open", side_effect=_file_opener(files)),
        ):
            from backend.scripts.seed_all import seed_mongo

            await seed_mongo()

        docs = collection.insert_many.call_args[0][0]
        assert len(docs) == 2, "Should skip blank lines"

    async def test_no_insert_when_empty_file(self):
        """If JSONL is empty, insert_many should not be called."""
        collection, db = _make_mongo_mocks()
        files = {"reviews.jsonl": "\n\n"}
        with (
            patch("backend.scripts.seed_all.get_mongo_db", return_value=db),
            patch("builtins.open", side_effect=_file_opener(files)),
        ):
            from backend.scripts.seed_all import seed_mongo

            await seed_mongo()

        collection.insert_many.assert_not_awaited()


# ── seed_neo4j ───────────────────────────────────────────────────


def _make_neo4j_mocks():
    """Create Neo4j session and driver mocks. Returns (session, driver)."""
    session = AsyncMock()
    driver = MagicMock()
    ctx = AsyncMock()
    ctx.__aenter__ = AsyncMock(return_value=session)
    ctx.__aexit__ = AsyncMock(return_value=False)
    driver.session = MagicMock(return_value=ctx)
    return session, driver


class TestSeedNeo4j:
    """Tests for seed_neo4j()."""

    async def test_clears_graph(self):
        """seed_neo4j must DETACH DELETE all nodes first."""
        session, driver = _make_neo4j_mocks()
        files = {"cities.csv": _make_cities_csv(), "scores.csv": _make_scores_csv()}
        with (
            patch("backend.scripts.seed_all.get_neo4j_driver", return_value=driver),
            patch("builtins.open", side_effect=_file_opener(files)),
        ):
            from backend.scripts.seed_all import seed_neo4j

            await seed_neo4j()

        cypher_calls = [str(call.args[0]) for call in session.run.call_args_list]
        detach_delete = [s for s in cypher_calls if "DETACH DELETE" in s.upper()]
        assert len(detach_delete) >= 1, "Should clear the graph first"

    async def test_creates_criterion_nodes(self):
        """seed_neo4j must create Criterion nodes from score categories."""
        session, driver = _make_neo4j_mocks()
        files = {"cities.csv": _make_cities_csv(), "scores.csv": _make_scores_csv()}
        with (
            patch("backend.scripts.seed_all.get_neo4j_driver", return_value=driver),
            patch("builtins.open", side_effect=_file_opener(files)),
        ):
            from backend.scripts.seed_all import seed_neo4j

            await seed_neo4j()

        cypher_calls = [str(call.args[0]) for call in session.run.call_args_list]
        criterion_calls = [s for s in cypher_calls if "Criterion" in s and "MERGE" in s.upper()]
        assert len(criterion_calls) >= 1, "Should create Criterion nodes"

    async def test_creates_city_nodes(self):
        """seed_neo4j must create City nodes from cities.csv."""
        session, driver = _make_neo4j_mocks()
        files = {"cities.csv": _make_cities_csv(), "scores.csv": _make_scores_csv()}
        with (
            patch("backend.scripts.seed_all.get_neo4j_driver", return_value=driver),
            patch("builtins.open", side_effect=_file_opener(files)),
        ):
            from backend.scripts.seed_all import seed_neo4j

            await seed_neo4j()

        cypher_calls = [str(call.args[0]) for call in session.run.call_args_list]
        city_merge_calls = [
            s for s in cypher_calls if "MERGE" in s.upper() and "City" in s and "Criterion" not in s
        ]
        assert len(city_merge_calls) >= 2, "Should create at least 2 City nodes"

    async def test_creates_strong_in_relations(self):
        """seed_neo4j must create STRONG_IN relations for scores >= 7."""
        session, driver = _make_neo4j_mocks()
        scores_csv = _make_scores_csv([
            {"city_id": "1", "category": "sante", "label": "Santé", "score": "7.8"},
            {"city_id": "1", "category": "transport", "label": "Transports", "score": "9.0"},
            {"city_id": "1", "category": "securite", "label": "Sécurité", "score": "5.0"},
            {"city_id": "2", "category": "sante", "label": "Santé", "score": "8.0"},
        ])
        files = {"cities.csv": _make_cities_csv(), "scores.csv": scores_csv}
        with (
            patch("backend.scripts.seed_all.get_neo4j_driver", return_value=driver),
            patch("builtins.open", side_effect=_file_opener(files)),
        ):
            from backend.scripts.seed_all import seed_neo4j

            await seed_neo4j()

        cypher_calls = [str(call.args[0]) for call in session.run.call_args_list]
        strong_in_calls = [s for s in cypher_calls if "STRONG_IN" in s]
        # Scores >= 7: 7.8, 9.0, 8.0 = 3 relations; 5.0 is excluded
        assert len(strong_in_calls) >= 3, "Should create STRONG_IN only for scores >= 7"

    async def test_no_strong_in_for_low_scores(self):
        """Scores below 7 should NOT produce STRONG_IN relations."""
        session, driver = _make_neo4j_mocks()
        scores_csv = _make_scores_csv([
            {"city_id": "1", "category": "securite", "label": "Sécurité", "score": "5.0"},
            {"city_id": "2", "category": "environnement", "label": "Environnement", "score": "6.9"},
        ])
        files = {"cities.csv": _make_cities_csv(), "scores.csv": scores_csv}
        with (
            patch("backend.scripts.seed_all.get_neo4j_driver", return_value=driver),
            patch("builtins.open", side_effect=_file_opener(files)),
        ):
            from backend.scripts.seed_all import seed_neo4j

            await seed_neo4j()

        cypher_calls = [str(call.args[0]) for call in session.run.call_args_list]
        strong_in_calls = [s for s in cypher_calls if "STRONG_IN" in s and "MATCH" in s.upper()]
        # Filter out the SIMILAR_TO query which also references STRONG_IN in its MATCH clause
        direct_strong_in = [s for s in strong_in_calls if "SIMILAR_TO" not in s]
        assert len(direct_strong_in) == 0, "No STRONG_IN for scores < 7"

    async def test_creates_similar_to_relations(self):
        """seed_neo4j must create SIMILAR_TO relations between cities."""
        session, driver = _make_neo4j_mocks()
        files = {"cities.csv": _make_cities_csv(), "scores.csv": _make_scores_csv()}
        with (
            patch("backend.scripts.seed_all.get_neo4j_driver", return_value=driver),
            patch("builtins.open", side_effect=_file_opener(files)),
        ):
            from backend.scripts.seed_all import seed_neo4j

            await seed_neo4j()

        cypher_calls = [str(call.args[0]) for call in session.run.call_args_list]
        similar_to_calls = [s for s in cypher_calls if "SIMILAR_TO" in s]
        assert len(similar_to_calls) >= 1, "Should create SIMILAR_TO relations"


# ── main ─────────────────────────────────────────────────────────


class TestSeedMain:
    """Tests for the main() orchestrator."""

    async def test_main_calls_all_seeds(self):
        """main() must call seed_postgres, seed_mongo, and seed_neo4j."""
        with (
            patch("backend.scripts.seed_all.seed_postgres", new_callable=AsyncMock) as mock_pg,
            patch("backend.scripts.seed_all.seed_mongo", new_callable=AsyncMock) as mock_mongo,
            patch("backend.scripts.seed_all.seed_neo4j", new_callable=AsyncMock) as mock_neo4j,
        ):
            from backend.scripts.seed_all import main

            await main()

        mock_pg.assert_awaited_once()
        mock_mongo.assert_awaited_once()
        mock_neo4j.assert_awaited_once()

    async def test_main_calls_seeds_in_order(self):
        """main() must call seeds in order: postgres, mongo, neo4j."""
        call_order = []

        async def track_pg():
            call_order.append("postgres")

        async def track_mongo():
            call_order.append("mongo")

        async def track_neo4j():
            call_order.append("neo4j")

        with (
            patch("backend.scripts.seed_all.seed_postgres", side_effect=track_pg),
            patch("backend.scripts.seed_all.seed_mongo", side_effect=track_mongo),
            patch("backend.scripts.seed_all.seed_neo4j", side_effect=track_neo4j),
        ):
            from backend.scripts.seed_all import main

            await main()

        assert call_order == ["postgres", "mongo", "neo4j"]
