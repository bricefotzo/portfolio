"""Tests unitaires — TP4 : Service Recommendations.

Jour 2 Après-midi (partie 2) — Implémenter l'orchestration multi-repo.

Commande :
    uv run pytest tests/unit/test_tp4_reco_service.py -v

Fichier à implémenter :
    packages/backend/src/backend/services/recommendation_service.py

Méthode à implémenter :
    1. get_recommendations(city_id, k) -> RecommendationsResponse | None
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from backend.models import RecommendationsResponse
from backend.services.recommendation_service import RecommendationService


@pytest.fixture
def mock_neo4j_repo():
    return AsyncMock()


@pytest.fixture
def mock_postgres_repo():
    return AsyncMock()


@pytest.fixture
def service(mock_neo4j_repo, mock_postgres_repo):
    return RecommendationService(
        neo4j_repo=mock_neo4j_repo,
        postgres_repo=mock_postgres_repo,
    )


class TestGetRecommendations:
    """RecommendationService.get_recommendations() — Orchestration multi-repo."""

    async def test_returns_none_when_source_city_not_found(
        self, service, mock_postgres_repo
    ):
        """Doit retourner None si la ville source n'existe pas."""
        mock_postgres_repo.get_city_by_id.return_value = None

        result = await service.get_recommendations(city_id=99999)

        assert result is None

    async def test_returns_recommendations_response(
        self, service, mock_neo4j_repo, mock_postgres_repo
    ):
        """Doit retourner un RecommendationsResponse quand tout fonctionne."""
        mock_postgres_repo.get_city_by_id.side_effect = [
            # Premier appel : ville source
            {
                "id": 1,
                "name": "Lyon",
                "department": "Rhône",
                "region": "ARA",
                "population": 500000,
                "overall_score": 7.5,
            },
            # Deuxième appel : enrichissement de la recommandation
            {
                "id": 2,
                "name": "Marseille",
                "department": "BDR",
                "region": "PACA",
                "population": 870000,
                "overall_score": 6.5,
            },
        ]
        mock_neo4j_repo.get_similar_cities.return_value = [
            {
                "city": {"city_id": 2, "name": "Marseille"},
                "similarity_score": 0.85,
                "common_strengths": ["transport"],
            },
        ]

        result = await service.get_recommendations(city_id=1, k=3)

        assert isinstance(result, RecommendationsResponse)
        assert result.source_city == "Lyon"
        assert len(result.recommendations) == 1

    async def test_checks_source_city_exists(
        self, service, mock_postgres_repo, mock_neo4j_repo
    ):
        """Doit d'abord vérifier que la ville source existe via PostgreSQL."""
        mock_postgres_repo.get_city_by_id.return_value = None

        await service.get_recommendations(city_id=1)

        mock_postgres_repo.get_city_by_id.assert_called_with(1)

    async def test_calls_neo4j_for_similar_cities(
        self, service, mock_neo4j_repo, mock_postgres_repo
    ):
        """Doit appeler neo4j_repo.get_similar_cities()."""
        mock_postgres_repo.get_city_by_id.return_value = {
            "id": 1,
            "name": "Lyon",
            "department": "Rhône",
            "region": "ARA",
            "population": 500000,
            "overall_score": 7.5,
        }
        mock_neo4j_repo.get_similar_cities.return_value = []

        await service.get_recommendations(city_id=1, k=3)

        mock_neo4j_repo.get_similar_cities.assert_called_once_with(1, k=3)

    async def test_recommendation_item_structure(
        self, service, mock_neo4j_repo, mock_postgres_repo
    ):
        """Chaque recommendation doit contenir city, similarity_score, common_strengths."""
        mock_postgres_repo.get_city_by_id.side_effect = [
            {
                "id": 1,
                "name": "Lyon",
                "department": "Rhône",
                "region": "ARA",
                "population": 500000,
                "overall_score": 7.5,
            },
            {
                "id": 5,
                "name": "Nantes",
                "department": "LA",
                "region": "PDL",
                "population": 300000,
                "overall_score": 7.8,
            },
        ]
        mock_neo4j_repo.get_similar_cities.return_value = [
            {
                "city": {"city_id": 5, "name": "Nantes"},
                "similarity_score": 0.92,
                "common_strengths": ["environnement", "santé"],
            },
        ]

        result = await service.get_recommendations(city_id=1)

        reco = result.recommendations[0]
        assert reco.city.name == "Nantes"
        assert reco.similarity_score == 0.92
        assert "environnement" in reco.common_strengths

    async def test_empty_recommendations(
        self, service, mock_neo4j_repo, mock_postgres_repo
    ):
        """Doit gérer correctement l'absence de recommandations."""
        mock_postgres_repo.get_city_by_id.return_value = {
            "id": 1,
            "name": "Lyon",
            "department": "Rhône",
            "region": "ARA",
            "population": 500000,
            "overall_score": 7.5,
        }
        mock_neo4j_repo.get_similar_cities.return_value = []

        result = await service.get_recommendations(city_id=1, k=5)

        assert isinstance(result, RecommendationsResponse)
        assert result.source_city == "Lyon"
        assert result.recommendations == []
