"""Fixtures et helpers pour les tests unitaires.

Fournit des mocks pour les sessions de base de données (PostgreSQL,
MongoDB, Neo4j) afin de tester chaque couche indépendamment.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest


# ── Helpers SQLAlchemy ──────────────────────────────────────────


class FakeRow(dict):
    """Simule une ligne SQLAlchemy (RowMapping)."""

    pass


class FakeMappingResult:
    """Simule result.mappings() de SQLAlchemy."""

    def __init__(self, rows: list[dict]):
        self._rows = [FakeRow(r) for r in rows]

    def all(self) -> list[FakeRow]:
        return self._rows

    def first(self):
        return self._rows[0] if self._rows else None


class FakeResult:
    """Simule le CursorResult de SQLAlchemy.

    Utilisation dans les tests :
        pg_session.execute.return_value = FakeResult(rows=[...])
        pg_session.execute.side_effect = [FakeResult(scalar=5), FakeResult(rows=[...])]
    """

    def __init__(self, *, rows: list[dict] | None = None, scalar=None):
        self._rows = rows or []
        self._scalar = scalar

    def scalar_one(self):
        return self._scalar

    def mappings(self) -> FakeMappingResult:
        return FakeMappingResult(self._rows)


@pytest.fixture
def pg_session() -> AsyncMock:
    """Mock d'une AsyncSession SQLAlchemy."""
    return AsyncMock()


# ── Helpers MongoDB (Motor) ─────────────────────────────────────


class FakeCursor:
    """Simule un curseur Motor (async iterable avec chaînage).

    Usage :
        collection.find.return_value = FakeCursor([{"_id": "abc", ...}])
    """

    def __init__(self, docs: list[dict]):
        self._docs = list(docs)
        self._iter: list[dict] = []

    def sort(self, *args, **kwargs):
        return self

    def skip(self, n: int):
        return self

    def limit(self, n: int):
        return self

    def __aiter__(self):
        self._iter = list(self._docs)
        return self

    async def __anext__(self):
        if not self._iter:
            raise StopAsyncIteration
        return self._iter.pop(0)


class FakeAggregationCursor:
    """Simule un curseur d'agrégation Motor.

    Usage :
        collection.aggregate.return_value = FakeAggregationCursor([{"avg_rating": 4.2}])
    """

    def __init__(self, docs: list[dict]):
        self._docs = docs

    async def to_list(self, length=None):
        return self._docs


class FakeInsertResult:
    """Simule le résultat de collection.insert_one()."""

    def __init__(self, inserted_id="fake_id_123"):
        self.inserted_id = inserted_id


@pytest.fixture
def mongo_collection() -> MagicMock:
    """Mock d'une collection Motor."""
    collection = MagicMock()
    collection.count_documents = AsyncMock(return_value=0)
    collection.insert_one = AsyncMock(return_value=FakeInsertResult())
    collection.find = MagicMock(return_value=FakeCursor([]))
    collection.aggregate = MagicMock(return_value=FakeAggregationCursor([]))
    return collection


@pytest.fixture
def mongo_db(mongo_collection) -> MagicMock:
    """Mock d'une AsyncIOMotorDatabase."""
    db = MagicMock()
    db.__getitem__ = MagicMock(return_value=mongo_collection)
    return db


# ── Helpers Neo4j ───────────────────────────────────────────────


class FakeNeo4jResult:
    """Simule le résultat d'une requête Neo4j.

    Usage :
        session.run.return_value = FakeNeo4jResult([{"city": {...}, ...}])
    """

    def __init__(self, records: list[dict]):
        self._records = records

    async def data(self) -> list[dict]:
        return self._records


@pytest.fixture
def neo4j_session() -> AsyncMock:
    """Mock d'une session Neo4j."""
    return AsyncMock()


@pytest.fixture
def neo4j_driver(neo4j_session) -> MagicMock:
    """Mock du driver Neo4j async.

    Simule le context manager ``async with driver.session() as session``.
    """
    driver = MagicMock()
    ctx = AsyncMock()
    ctx.__aenter__ = AsyncMock(return_value=neo4j_session)
    ctx.__aexit__ = AsyncMock(return_value=False)
    driver.session = MagicMock(return_value=ctx)
    return driver
