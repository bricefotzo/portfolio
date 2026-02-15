"""Tests unitaires — TP1 : Repository PostgreSQL.

Jour 1 Matin — Implémenter l'accès aux données PostgreSQL.

Commande :
    uv run pytest tests/unit/test_tp1_postgres_repo.py -v

Fichier à implémenter :
    packages/backend/src/backend/repositories/postgres_repo.py

Méthodes à implémenter :
    1. get_city_by_id(city_id) -> dict | None
    2. get_city_scores(city_id) -> list[dict]
    3. get_cities(**filters) -> tuple[list[dict], int]
"""

from __future__ import annotations

from backend.repositories.postgres_repo import PostgresRepository

from .conftest import FakeResult


# ── get_city_by_id ──────────────────────────────────────────────


class TestGetCityById:
    """PostgresRepository.get_city_by_id() — SELECT une ville par ID."""

    async def test_returns_dict_when_found(self, pg_session):
        """Doit retourner un dict quand la ville existe."""
        row = {
            "id": 1,
            "name": "Lyon",
            "department": "Rhône",
            "region": "Auvergne-Rhône-Alpes",
            "population": 516092,
            "description": "Capitale des Gaules",
            "latitude": 45.76,
            "longitude": 4.83,
            "overall_score": 7.5,
        }
        pg_session.execute.return_value = FakeResult(rows=[row])

        repo = PostgresRepository(pg_session)
        result = await repo.get_city_by_id(1)

        assert result is not None
        assert isinstance(result, dict)
        assert result["name"] == "Lyon"
        assert result["overall_score"] == 7.5

    async def test_returns_none_when_not_found(self, pg_session):
        """Doit retourner None si la ville n'existe pas."""
        pg_session.execute.return_value = FakeResult(rows=[])

        repo = PostgresRepository(pg_session)
        result = await repo.get_city_by_id(99999)

        assert result is None

    async def test_contains_all_required_fields(self, pg_session):
        """Le dict retourné doit contenir toutes les colonnes attendues."""
        row = {
            "id": 1,
            "name": "Paris",
            "department": "Paris",
            "region": "Île-de-France",
            "population": 2161000,
            "description": "Capitale",
            "latitude": 48.85,
            "longitude": 2.35,
            "overall_score": 6.8,
        }
        pg_session.execute.return_value = FakeResult(rows=[row])

        repo = PostgresRepository(pg_session)
        result = await repo.get_city_by_id(1)

        required = (
            "id",
            "name",
            "department",
            "region",
            "population",
            "description",
            "latitude",
            "longitude",
            "overall_score",
        )
        for field in required:
            assert field in result, f"Champ manquant : {field}"


# ── get_city_scores ─────────────────────────────────────────────


class TestGetCityScores:
    """PostgresRepository.get_city_scores() — Scores par catégorie."""

    async def test_returns_list_of_dicts(self, pg_session):
        """Doit retourner une liste de dicts {category, score, label}."""
        scores = [
            {"category": "environnement", "score": 8.0, "label": "Environnement"},
            {"category": "sante", "score": 7.5, "label": "Santé"},
            {"category": "transport", "score": 6.0, "label": "Transport"},
        ]
        pg_session.execute.return_value = FakeResult(rows=scores)

        repo = PostgresRepository(pg_session)
        result = await repo.get_city_scores(1)

        assert isinstance(result, list)
        assert len(result) == 3
        assert all(isinstance(r, dict) for r in result)

    async def test_score_dict_has_required_keys(self, pg_session):
        """Chaque dict doit contenir category, score et label."""
        scores = [{"category": "securite", "score": 7.0, "label": "Sécurité"}]
        pg_session.execute.return_value = FakeResult(rows=scores)

        repo = PostgresRepository(pg_session)
        result = await repo.get_city_scores(1)

        assert len(result) == 1
        for key in ("category", "score", "label"):
            assert key in result[0], f"Clé manquante : {key}"

    async def test_returns_empty_list_when_no_scores(self, pg_session):
        """Doit retourner [] si aucun score trouvé."""
        pg_session.execute.return_value = FakeResult(rows=[])

        repo = PostgresRepository(pg_session)
        result = await repo.get_city_scores(99999)

        assert result == []


# ── get_cities ──────────────────────────────────────────────────


class TestGetCities:
    """PostgresRepository.get_cities() — Recherche avec filtres et pagination."""

    async def test_returns_tuple_list_and_total(self, pg_session):
        """Doit retourner (list[dict], int)."""
        cities = [
            {
                "id": 1,
                "name": "Lyon",
                "department": "Rhône",
                "region": "ARA",
                "population": 500000,
                "overall_score": 7.5,
            },
        ]
        pg_session.execute.side_effect = [
            FakeResult(scalar=1),  # COUNT(*)
            FakeResult(rows=cities),  # SELECT ... LIMIT/OFFSET
        ]

        repo = PostgresRepository(pg_session)
        rows, total = await repo.get_cities()

        assert isinstance(rows, list)
        assert isinstance(total, int)
        assert total == 1
        assert len(rows) == 1

    async def test_returns_dicts_with_city_fields(self, pg_session):
        """Les dicts doivent contenir les champs d'une ville."""
        city = {
            "id": 2,
            "name": "Marseille",
            "department": "Bouches-du-Rhône",
            "region": "PACA",
            "population": 870000,
            "overall_score": 6.5,
        }
        pg_session.execute.side_effect = [
            FakeResult(scalar=1),
            FakeResult(rows=[city]),
        ]

        repo = PostgresRepository(pg_session)
        rows, _ = await repo.get_cities()

        assert rows[0]["name"] == "Marseille"
        assert rows[0]["population"] == 870000

    async def test_empty_results(self, pg_session):
        """Doit retourner ([], 0) quand aucun résultat."""
        pg_session.execute.side_effect = [
            FakeResult(scalar=0),
            FakeResult(rows=[]),
        ]

        repo = PostgresRepository(pg_session)
        rows, total = await repo.get_cities(search="VilleInexistante")

        assert total == 0
        assert rows == []

    async def test_calls_execute_twice(self, pg_session):
        """Doit appeler session.execute au moins 2 fois (count + data)."""
        pg_session.execute.side_effect = [
            FakeResult(scalar=0),
            FakeResult(rows=[]),
        ]

        repo = PostgresRepository(pg_session)
        await repo.get_cities()

        assert pg_session.execute.call_count == 2

    async def test_accepts_search_parameter(self, pg_session):
        """Doit accepter le paramètre search sans erreur."""
        pg_session.execute.side_effect = [
            FakeResult(scalar=0),
            FakeResult(rows=[]),
        ]

        repo = PostgresRepository(pg_session)
        rows, total = await repo.get_cities(search="Lyon")

        assert isinstance(rows, list)
        assert isinstance(total, int)

    async def test_accepts_region_filter(self, pg_session):
        """Doit accepter le filtre region sans erreur."""
        pg_session.execute.side_effect = [
            FakeResult(scalar=0),
            FakeResult(rows=[]),
        ]

        repo = PostgresRepository(pg_session)
        rows, total = await repo.get_cities(region="Bretagne")

        assert isinstance(rows, list)

    async def test_accepts_pagination_params(self, pg_session):
        """Doit accepter page et page_size sans erreur."""
        pg_session.execute.side_effect = [
            FakeResult(scalar=0),
            FakeResult(rows=[]),
        ]

        repo = PostgresRepository(pg_session)
        rows, total = await repo.get_cities(page=3, page_size=5)

        assert isinstance(rows, list)

    async def test_accepts_sort_params(self, pg_session):
        """Doit accepter sort_by et sort_order sans erreur."""
        pg_session.execute.side_effect = [
            FakeResult(scalar=0),
            FakeResult(rows=[]),
        ]

        repo = PostgresRepository(pg_session)
        rows, total = await repo.get_cities(sort_by="population", sort_order="asc")

        assert isinstance(rows, list)
