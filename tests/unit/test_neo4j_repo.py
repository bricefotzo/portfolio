"""Tests unitaires — Repository Neo4j.

Implémenter les requêtes Cypher.

Commande :
    uv run pytest tests/unit/test_neo4j_repo.py -v

Fichier à implémenter :
    packages/backend/src/backend/repositories/neo4j_repo.py

Méthodes à implémenter :
    1. get_similar_cities(city_id, k) -> list[dict]
    2. get_city_strengths(city_id) -> list[str]
"""

from __future__ import annotations

import pytest

from backend.repositories.neo4j_repo import Neo4jRepository

from .conftest import FakeNeo4jResult

pytestmark = pytest.mark.sprint3


# ── get_similar_cities ──────────────────────────────────────────


class TestGetSimilarCities:
    """Neo4jRepository.get_similar_cities() — Traversée du graphe SIMILAR_TO."""

    async def test_returns_list_of_dicts(self, neo4j_driver, neo4j_session):
        """Doit retourner une liste de dicts."""
        records = [
            {
                "city": {
                    "city_id": 2,
                    "name": "Marseille",
                    "department": "BDR",
                    "region": "PACA",
                    "population": 870000,
                    "overall_score": 6.5,
                },
                "similarity_score": 0.87,
                "common_strengths": ["transport", "culture"],
            },
        ]
        neo4j_session.run.return_value = FakeNeo4jResult(records)

        repo = Neo4jRepository(neo4j_driver)
        result = await repo.get_similar_cities(city_id=1, k=5)

        assert isinstance(result, list)
        assert len(result) == 1

    async def test_result_contains_required_keys(self, neo4j_driver, neo4j_session):
        """Chaque résultat doit contenir city, similarity_score, common_strengths."""
        records = [
            {
                "city": {
                    "city_id": 3,
                    "name": "Toulouse",
                    "department": "HG",
                    "region": "Occitanie",
                    "population": 480000,
                    "overall_score": 7.0,
                },
                "similarity_score": 0.75,
                "common_strengths": ["environnement"],
            },
        ]
        neo4j_session.run.return_value = FakeNeo4jResult(records)

        repo = Neo4jRepository(neo4j_driver)
        result = await repo.get_similar_cities(city_id=1, k=3)

        item = result[0]
        assert "city" in item
        assert "similarity_score" in item
        assert "common_strengths" in item
        assert isinstance(item["common_strengths"], list)

    async def test_returns_empty_list_when_no_similar(self, neo4j_driver, neo4j_session):
        """Doit retourner [] si aucune ville similaire trouvée."""
        neo4j_session.run.return_value = FakeNeo4jResult([])

        repo = Neo4jRepository(neo4j_driver)
        result = await repo.get_similar_cities(city_id=999, k=5)

        assert result == []

    async def test_calls_session_run(self, neo4j_driver, neo4j_session):
        """Doit exécuter une requête Cypher via session.run()."""
        neo4j_session.run.return_value = FakeNeo4jResult([])

        repo = Neo4jRepository(neo4j_driver)
        await repo.get_similar_cities(city_id=1, k=5)

        neo4j_session.run.assert_called_once()

    async def test_multiple_results(self, neo4j_driver, neo4j_session):
        """Doit retourner plusieurs villes similaires."""
        records = [
            {
                "city": {"city_id": 2, "name": "Marseille"},
                "similarity_score": 0.92,
                "common_strengths": ["transport"],
            },
            {
                "city": {"city_id": 3, "name": "Toulouse"},
                "similarity_score": 0.85,
                "common_strengths": ["environnement", "santé"],
            },
            {
                "city": {"city_id": 4, "name": "Nantes"},
                "similarity_score": 0.78,
                "common_strengths": [],
            },
        ]
        neo4j_session.run.return_value = FakeNeo4jResult(records)

        repo = Neo4jRepository(neo4j_driver)
        result = await repo.get_similar_cities(city_id=1, k=3)

        assert len(result) == 3


# ── get_city_strengths ──────────────────────────────────────────


class TestGetCityStrengths:
    """Neo4jRepository.get_city_strengths() — Points forts (STRONG_IN)."""

    async def test_returns_list_of_strings(self, neo4j_driver, neo4j_session):
        """Doit retourner une liste de noms de critères (str)."""
        neo4j_session.run.return_value = FakeNeo4jResult(
            [
                {"name": "Environnement"},
                {"name": "Santé"},
                {"name": "Culture"},
            ]
        )

        repo = Neo4jRepository(neo4j_driver)
        result = await repo.get_city_strengths(city_id=1)

        assert isinstance(result, list)
        assert len(result) == 3
        assert all(isinstance(s, str) for s in result)
        assert "Environnement" in result

    async def test_returns_empty_list_when_no_strengths(self, neo4j_driver, neo4j_session):
        """Doit retourner [] si aucun point fort."""
        neo4j_session.run.return_value = FakeNeo4jResult([])

        repo = Neo4jRepository(neo4j_driver)
        result = await repo.get_city_strengths(city_id=999)

        assert result == []

    async def test_calls_session_run_with_city_id(self, neo4j_driver, neo4j_session):
        """Doit exécuter une requête Cypher avec city_id."""
        neo4j_session.run.return_value = FakeNeo4jResult([])

        repo = Neo4jRepository(neo4j_driver)
        await repo.get_city_strengths(city_id=42)

        neo4j_session.run.assert_called_once()
        call_kwargs = neo4j_session.run.call_args[1]
        assert call_kwargs.get("city_id") == 42
