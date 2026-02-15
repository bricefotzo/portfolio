"""Tests unitaires — TP3 : Service Reviews.

Jour 2 Matin (partie 2) — Implémenter l'orchestration des avis.

Commande :
    uv run pytest tests/unit/test_tp3_review_service.py -v

Fichier à implémenter :
    packages/backend/src/backend/services/review_service.py

Méthodes à implémenter :
    1. get_reviews(city_id, page, page_size) -> ReviewsResponse
    2. create_review(city_id, review) -> Review
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from backend.models import Review, ReviewCreate, ReviewsResponse
from backend.services.review_service import ReviewService


@pytest.fixture
def mock_repo():
    """Mock du MongoRepository."""
    return AsyncMock()


@pytest.fixture
def service(mock_repo):
    return ReviewService(repo=mock_repo)


# ── get_reviews ─────────────────────────────────────────────────


class TestGetReviews:
    """ReviewService.get_reviews() — Récupération paginée."""

    async def test_returns_reviews_response(self, service, mock_repo):
        """Doit retourner un ReviewsResponse."""
        mock_repo.get_reviews.return_value = (
            [
                {
                    "id": "abc",
                    "author": "Alice",
                    "rating": 4,
                    "comment": "Bien",
                    "tags": [],
                    "created_at": None,
                }
            ],
            1,
        )

        result = await service.get_reviews(city_id=1)

        assert isinstance(result, ReviewsResponse)
        assert result.total == 1
        assert len(result.reviews) == 1

    async def test_converts_dicts_to_review_objects(self, service, mock_repo):
        """Doit convertir les dicts en objets Review avec city_id."""
        mock_repo.get_reviews.return_value = (
            [
                {
                    "id": "r1",
                    "author": "Bob",
                    "rating": 5,
                    "comment": "Super",
                    "tags": ["nature"],
                    "created_at": None,
                }
            ],
            1,
        )

        result = await service.get_reviews(city_id=3)

        review = result.reviews[0]
        assert isinstance(review, Review)
        assert review.author == "Bob"
        assert review.city_id == 3

    async def test_passes_pagination_to_repo(self, service, mock_repo):
        """Doit transmettre les paramètres de pagination."""
        mock_repo.get_reviews.return_value = ([], 0)

        await service.get_reviews(city_id=1, page=3, page_size=5)

        mock_repo.get_reviews.assert_called_once_with(1, page=3, page_size=5)

    async def test_empty_reviews(self, service, mock_repo):
        """Doit gérer correctement l'absence d'avis."""
        mock_repo.get_reviews.return_value = ([], 0)

        result = await service.get_reviews(city_id=1)

        assert result.total == 0
        assert result.reviews == []


# ── create_review ───────────────────────────────────────────────


class TestCreateReview:
    """ReviewService.create_review() — Création d'un avis."""

    async def test_returns_review_object(self, service, mock_repo):
        """Doit retourner un objet Review."""
        mock_repo.create_review.return_value = {
            "id": "new_1",
            "author": "Charlie",
            "rating": 4,
            "comment": "Agréable",
            "tags": [],
            "created_at": datetime.now(timezone.utc),
        }

        review_in = ReviewCreate(author="Charlie", rating=4, comment="Agréable")
        result = await service.create_review(city_id=2, review=review_in)

        assert isinstance(result, Review)
        assert result.city_id == 2
        assert result.author == "Charlie"

    async def test_passes_data_to_repo(self, service, mock_repo):
        """Doit appeler repo.create_review avec city_id et les données."""
        mock_repo.create_review.return_value = {
            "id": "new_2",
            "author": "Dana",
            "rating": 5,
            "comment": "Parfait",
            "tags": ["calme"],
            "created_at": datetime.now(timezone.utc),
        }

        review_in = ReviewCreate(author="Dana", rating=5, comment="Parfait", tags=["calme"])
        await service.create_review(city_id=4, review=review_in)

        mock_repo.create_review.assert_called_once()
        call_args = mock_repo.create_review.call_args
        assert call_args[0][0] == 4  # city_id

    async def test_converts_review_create_to_dict(self, service, mock_repo):
        """Doit convertir ReviewCreate en dict avant d'appeler le repo."""
        mock_repo.create_review.return_value = {
            "id": "new_3",
            "author": "Emma",
            "rating": 3,
            "comment": "Correct",
            "tags": [],
            "created_at": datetime.now(timezone.utc),
        }

        review_in = ReviewCreate(author="Emma", rating=3, comment="Correct")
        await service.create_review(city_id=1, review=review_in)

        call_args = mock_repo.create_review.call_args
        data = call_args[0][1]  # second positional argument
        assert isinstance(data, dict)
        assert data["author"] == "Emma"
        assert data["rating"] == 3
