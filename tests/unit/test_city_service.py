"""Tests unitaires — Service City.

Le service est fourni ; ces tests vérifient le comportement (repos mockés).

Commande :
    uv run pytest tests/unit/test_city_service.py -v
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from backend.models import CityDetail, CityListResponse, CityScores
from backend.services.city_service import CityService

pytestmark = pytest.mark.sprint4


@pytest.fixture
def mock_repo():
    """Mock du PostgresRepository."""
    return AsyncMock()


@pytest.fixture
def service(mock_repo):
    return CityService(repo=mock_repo)


# ── search_cities ───────────────────────────────────────────────


class TestSearchCities:
    """CityService.search_cities() — Recherche de villes."""

    async def test_returns_city_list_response(self, service, mock_repo):
        """Doit retourner un CityListResponse."""
        mock_repo.get_cities.return_value = (
            [
                {
                    "id": 1,
                    "name": "Lyon",
                    "department": "Rhône",
                    "region": "ARA",
                    "population": 500000,
                    "overall_score": 7.5,
                }
            ],
            1,
        )

        result = await service.search_cities()

        assert isinstance(result, CityListResponse)

    async def test_maps_rows_to_city_objects(self, service, mock_repo):
        """Doit convertir les dicts du repo en objets City."""
        mock_repo.get_cities.return_value = (
            [
                {
                    "id": 1,
                    "name": "Lyon",
                    "department": "Rhône",
                    "region": "ARA",
                    "population": 500000,
                    "overall_score": 7.5,
                },
                {
                    "id": 2,
                    "name": "Paris",
                    "department": "Paris",
                    "region": "IDF",
                    "population": 2161000,
                    "overall_score": 6.8,
                },
            ],
            2,
        )

        result = await service.search_cities()

        assert result.total == 2
        assert len(result.cities) == 2
        assert result.cities[0].name == "Lyon"
        assert result.cities[1].name == "Paris"

    async def test_passes_parameters_to_repo(self, service, mock_repo):
        """Doit transmettre les paramètres au repository."""
        mock_repo.get_cities.return_value = ([], 0)

        await service.search_cities(search="Lyon", region="ARA", page=2, page_size=5)

        mock_repo.get_cities.assert_called_once()
        kwargs = mock_repo.get_cities.call_args[1]
        assert kwargs["search"] == "Lyon"
        assert kwargs["region"] == "ARA"
        assert kwargs["page"] == 2
        assert kwargs["page_size"] == 5

    async def test_empty_results(self, service, mock_repo):
        """Doit gérer correctement l'absence de résultats."""
        mock_repo.get_cities.return_value = ([], 0)

        result = await service.search_cities()

        assert result.total == 0
        assert result.cities == []

    async def test_preserves_page_info(self, service, mock_repo):
        """Doit conserver page et page_size dans la réponse."""
        mock_repo.get_cities.return_value = ([], 0)

        result = await service.search_cities(page=3, page_size=10)

        assert result.page == 3
        assert result.page_size == 10


# ── get_city_detail ─────────────────────────────────────────────


class TestGetCityDetail:
    """CityService.get_city_detail() — Détails ville + scores."""

    async def test_returns_city_detail_with_scores(self, service, mock_repo):
        """Doit combiner les infos ville + scores dans un CityDetail."""
        mock_repo.get_city_by_id.return_value = {
            "id": 1,
            "name": "Lyon",
            "department": "Rhône",
            "region": "ARA",
            "population": 500000,
            "description": "Belle ville",
            "latitude": 45.76,
            "longitude": 4.83,
            "overall_score": 7.5,
        }
        mock_repo.get_city_scores.return_value = [
            {"category": "environnement", "score": 8.0, "label": "Environnement"},
        ]

        result = await service.get_city_detail(1)

        assert isinstance(result, CityDetail)
        assert result.name == "Lyon"
        assert len(result.scores) == 1
        assert result.scores[0].category == "environnement"

    async def test_returns_none_when_city_not_found(self, service, mock_repo):
        """Doit retourner None si la ville n'existe pas."""
        mock_repo.get_city_by_id.return_value = None

        result = await service.get_city_detail(99999)

        assert result is None

    async def test_calls_both_repo_methods(self, service, mock_repo):
        """Doit appeler get_city_by_id ET get_city_scores."""
        mock_repo.get_city_by_id.return_value = {
            "id": 1,
            "name": "Lyon",
            "department": "Rhône",
            "region": "ARA",
            "population": 500000,
            "description": "",
            "latitude": 0.0,
            "longitude": 0.0,
            "overall_score": 7.0,
        }
        mock_repo.get_city_scores.return_value = []

        await service.get_city_detail(1)

        mock_repo.get_city_by_id.assert_called_once_with(1)
        mock_repo.get_city_scores.assert_called_once_with(1)

    async def test_handles_empty_scores(self, service, mock_repo):
        """Doit fonctionner même si la ville n'a aucun score."""
        mock_repo.get_city_by_id.return_value = {
            "id": 1,
            "name": "Lyon",
            "department": "Rhône",
            "region": "ARA",
            "population": 500000,
            "description": "",
            "latitude": 0.0,
            "longitude": 0.0,
            "overall_score": 7.0,
        }
        mock_repo.get_city_scores.return_value = []

        result = await service.get_city_detail(1)

        assert isinstance(result, CityDetail)
        assert result.scores == []


# ── get_city_scores ─────────────────────────────────────────────


class TestGetCityScores:
    """CityService.get_city_scores() — Scores qualité de vie."""

    async def test_returns_city_scores(self, service, mock_repo):
        """Doit retourner un CityScores avec les scores convertis."""
        mock_repo.get_city_by_id.return_value = {
            "id": 1,
            "name": "Lyon",
            "department": "Rhône",
            "region": "ARA",
            "population": 500000,
            "overall_score": 7.5,
        }
        mock_repo.get_city_scores.return_value = [
            {"category": "env", "score": 8.0, "label": "Environnement"},
            {"category": "sante", "score": 7.0, "label": "Santé"},
        ]

        result = await service.get_city_scores(1)

        assert isinstance(result, CityScores)
        assert result.city_id == 1
        assert result.overall == 7.5
        assert len(result.scores) == 2

    async def test_returns_none_when_city_not_found(self, service, mock_repo):
        """Doit retourner None si la ville n'existe pas."""
        mock_repo.get_city_by_id.return_value = None

        result = await service.get_city_scores(99999)

        assert result is None
