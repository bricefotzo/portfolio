"""Tests unitaires — TP3 : Repository MongoDB.

Jour 2 Matin (partie 1) — Implémenter l'accès aux avis MongoDB.

Commande :
    uv run pytest tests/unit/test_tp3_mongo_repo.py -v

Fichier à implémenter :
    packages/backend/src/backend/repositories/mongo_repo.py

Méthodes à implémenter :
    1. get_reviews(city_id, page, page_size) -> tuple[list[dict], int]
    2. create_review(city_id, review_data) -> dict
    3. get_average_rating(city_id) -> float | None
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.repositories.mongo_repo import MongoRepository

from .conftest import FakeAggregationCursor, FakeCursor, FakeInsertResult


@pytest.fixture
def collection():
    """Mock de la collection Motor 'reviews'."""
    coll = MagicMock()
    coll.count_documents = AsyncMock(return_value=0)
    coll.insert_one = AsyncMock(return_value=FakeInsertResult("abc123"))
    coll.find = MagicMock(return_value=FakeCursor([]))
    coll.aggregate = MagicMock(return_value=FakeAggregationCursor([]))
    return coll


@pytest.fixture
def mongo_db(collection):
    db = MagicMock()
    db.__getitem__ = MagicMock(return_value=collection)
    return db


@pytest.fixture
def repo(mongo_db):
    return MongoRepository(mongo_db)


# ── get_reviews ─────────────────────────────────────────────────


class TestGetReviews:
    """MongoRepository.get_reviews() — Lecture paginée des avis."""

    async def test_returns_tuple_list_and_total(self, repo, collection):
        """Doit retourner (list[dict], int)."""
        collection.count_documents.return_value = 0
        collection.find.return_value = FakeCursor([])

        docs, total = await repo.get_reviews(city_id=1)

        assert isinstance(docs, list)
        assert isinstance(total, int)

    async def test_converts_objectid_to_str(self, repo, collection):
        """Doit convertir _id (ObjectId) en champ 'id' (str)."""
        doc = {
            "_id": "507f1f77bcf86cd799439011",
            "city_id": 1,
            "author": "Alice",
            "rating": 4,
            "comment": "Super",
        }
        collection.count_documents.return_value = 1
        collection.find.return_value = FakeCursor([doc])

        docs, _ = await repo.get_reviews(city_id=1)

        assert len(docs) == 1
        assert "id" in docs[0]
        assert "_id" not in docs[0]
        assert isinstance(docs[0]["id"], str)

    async def test_returns_correct_total(self, repo, collection):
        """Le total doit refléter le count_documents."""
        collection.count_documents.return_value = 42
        collection.find.return_value = FakeCursor([])

        _, total = await repo.get_reviews(city_id=1)

        assert total == 42

    async def test_filters_by_city_id(self, repo, collection):
        """Doit filtrer par city_id."""
        collection.count_documents.return_value = 0
        collection.find.return_value = FakeCursor([])

        await repo.get_reviews(city_id=5)

        # count_documents doit recevoir un filtre avec city_id
        call_args = collection.count_documents.call_args[0][0]
        assert call_args.get("city_id") == 5

    async def test_multiple_reviews(self, repo, collection):
        """Doit retourner plusieurs avis correctement."""
        docs = [
            {"_id": "id1", "city_id": 1, "author": "Alice", "rating": 4, "comment": "Bien"},
            {"_id": "id2", "city_id": 1, "author": "Bob", "rating": 5, "comment": "Super"},
        ]
        collection.count_documents.return_value = 2
        collection.find.return_value = FakeCursor(docs)

        result_docs, total = await repo.get_reviews(city_id=1)

        assert total == 2
        assert len(result_docs) == 2
        assert result_docs[0]["author"] == "Alice"
        assert result_docs[1]["author"] == "Bob"


# ── create_review ───────────────────────────────────────────────


class TestCreateReview:
    """MongoRepository.create_review() — Création d'un avis."""

    async def test_returns_dict_with_id(self, repo, collection):
        """Doit retourner un dict contenant un champ 'id'."""
        collection.insert_one.return_value = FakeInsertResult("new_id_456")

        result = await repo.create_review(1, {"author": "Bob", "rating": 5, "comment": "Top"})

        assert isinstance(result, dict)
        assert "id" in result
        assert result["id"] == "new_id_456"

    async def test_adds_city_id_to_document(self, repo, collection):
        """Doit ajouter city_id au document inséré."""
        collection.insert_one.return_value = FakeInsertResult("id_789")

        result = await repo.create_review(7, {"author": "Eve", "rating": 3, "comment": "OK"})

        assert result["city_id"] == 7

    async def test_adds_created_at_timestamp(self, repo, collection):
        """Doit ajouter un champ created_at (datetime)."""
        collection.insert_one.return_value = FakeInsertResult("id_abc")

        result = await repo.create_review(
            1, {"author": "Dan", "rating": 4, "comment": "Bien"}
        )

        assert "created_at" in result
        assert isinstance(result["created_at"], datetime)

    async def test_calls_insert_one(self, repo, collection):
        """Doit appeler collection.insert_one()."""
        collection.insert_one.return_value = FakeInsertResult("id_xyz")

        await repo.create_review(1, {"author": "Kim", "rating": 5, "comment": "Génial"})

        collection.insert_one.assert_called_once()

    async def test_preserves_original_review_data(self, repo, collection):
        """Le résultat doit contenir les données de l'avis original."""
        collection.insert_one.return_value = FakeInsertResult("id_000")

        result = await repo.create_review(
            1, {"author": "Léa", "rating": 3, "comment": "Moyen", "tags": ["bruit"]}
        )

        assert result["author"] == "Léa"
        assert result["rating"] == 3
        assert result["comment"] == "Moyen"


# ── get_average_rating ──────────────────────────────────────────


class TestGetAverageRating:
    """MongoRepository.get_average_rating() — Pipeline d'agrégation."""

    async def test_returns_float_when_reviews_exist(self, repo, collection):
        """Doit retourner un float (moyenne arrondie)."""
        collection.aggregate.return_value = FakeAggregationCursor(
            [{"_id": None, "avg_rating": 4.2}]
        )

        result = await repo.get_average_rating(city_id=1)

        assert isinstance(result, float)
        assert result == 4.2

    async def test_returns_none_when_no_reviews(self, repo, collection):
        """Doit retourner None si aucun avis."""
        collection.aggregate.return_value = FakeAggregationCursor([])

        result = await repo.get_average_rating(city_id=999)

        assert result is None

    async def test_uses_aggregation_pipeline(self, repo, collection):
        """Doit utiliser collection.aggregate() (pas find)."""
        collection.aggregate.return_value = FakeAggregationCursor([])

        await repo.get_average_rating(city_id=1)

        collection.aggregate.assert_called_once()
