"""Tests d'acceptation — Endpoints Cities.

Ces tests vérifient le contrat API (schemas, status codes).
Quand le backend n'est pas encore implémenté, les endpoints retournent 501.
Une fois implémenté, les tests vérifient le contrat complet.
"""

from __future__ import annotations

# Codes acceptés quand l'endpoint n'est pas encore implémenté
OK_OR_NOT_IMPL = (200, 501)


class TestListCities:
    """GET /cities — Recherche et filtres."""

    def test_endpoint_exists(self, client):
        """L'endpoint /cities doit exister et répondre (200 ou 501)."""
        resp = client.get("/cities")
        assert resp.status_code in OK_OR_NOT_IMPL

    def test_response_schema_when_implemented(self, client):
        """Si implémenté, la réponse doit respecter CityListResponse."""
        resp = client.get("/cities")
        if resp.status_code == 200:
            data = resp.json()
            assert "cities" in data
            assert "total" in data
            assert "page" in data
            assert "page_size" in data
            assert isinstance(data["cities"], list)

    def test_pagination_params(self, client):
        """Les paramètres de pagination doivent être acceptés."""
        resp = client.get("/cities", params={"page": 1, "page_size": 5})
        assert resp.status_code in OK_OR_NOT_IMPL

    def test_search_param(self, client):
        """Le paramètre search doit être accepté."""
        resp = client.get("/cities", params={"search": "Lyon"})
        assert resp.status_code in OK_OR_NOT_IMPL

    def test_filter_region(self, client):
        """Le filtre region doit être accepté."""
        resp = client.get("/cities", params={"region": "Bretagne"})
        assert resp.status_code in OK_OR_NOT_IMPL

    def test_sort_params(self, client):
        """Les paramètres de tri doivent être acceptés."""
        resp = client.get(
            "/cities",
            params={"sort_by": "population", "sort_order": "asc"},
        )
        assert resp.status_code in OK_OR_NOT_IMPL


class TestCityDetail:
    """GET /cities/{city_id} — Détails ville."""

    def test_endpoint_exists(self, client):
        resp = client.get("/cities/1")
        assert resp.status_code in (200, 404, 501)

    def test_response_schema_when_implemented(self, client):
        """Si implémenté, la réponse doit respecter CityDetail."""
        resp = client.get("/cities/1")
        if resp.status_code == 200:
            data = resp.json()
            assert "id" in data
            assert "name" in data
            assert "region" in data
            assert "overall_score" in data

    def test_not_found(self, client):
        """Une ville inexistante doit retourner 404 (si implémenté)."""
        resp = client.get("/cities/999999")
        assert resp.status_code in (404, 501)


class TestCityScores:
    """GET /cities/{city_id}/scores — Scores qualité de vie."""

    def test_endpoint_exists(self, client):
        resp = client.get("/cities/1/scores")
        assert resp.status_code in (200, 404, 501)

    def test_response_schema_when_implemented(self, client):
        """Si implémenté, la réponse doit respecter CityScores."""
        resp = client.get("/cities/1/scores")
        if resp.status_code == 200:
            data = resp.json()
            assert "city_id" in data
            assert "scores" in data
            assert "overall" in data
            assert isinstance(data["scores"], list)
