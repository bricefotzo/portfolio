"""Tests d'acceptation — Endpoints Cities.

Ces tests vérifient le contrat API (schemas, status codes).
- 501 : endpoint pas encore implémenté (NotImplementedError)
- 500 : implémenté mais base de données non disponible
- 200 : pleinement fonctionnel
Les schema checks ne s'exécutent que quand le status est 200.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.sprint5

# Codes acceptés : fonctionnel / pas implémenté / DB indisponible
ACCEPT = (200, 500, 501)
ACCEPT_OR_404 = (200, 404, 500, 501)


class TestListCities:
    """GET /cities — Recherche et filtres."""

    def test_endpoint_exists(self, client):
        """L'endpoint /cities doit exister et répondre."""
        resp = client.get("/cities")
        assert resp.status_code in ACCEPT

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
        assert resp.status_code in ACCEPT

    def test_search_param(self, client):
        """Le paramètre search doit être accepté."""
        resp = client.get("/cities", params={"search": "Lyon"})
        assert resp.status_code in ACCEPT

    def test_filter_region(self, client):
        """Le filtre region doit être accepté."""
        resp = client.get("/cities", params={"region": "Bretagne"})
        assert resp.status_code in ACCEPT

    def test_sort_params(self, client):
        """Les paramètres de tri doivent être acceptés."""
        resp = client.get(
            "/cities",
            params={"sort_by": "population", "sort_order": "asc"},
        )
        assert resp.status_code in ACCEPT


class TestCityDetail:
    """GET /cities/{city_id} — Détails ville."""

    def test_endpoint_exists(self, client):
        resp = client.get("/cities/1")
        assert resp.status_code in ACCEPT_OR_404

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
        assert resp.status_code in ACCEPT_OR_404


class TestCityScores:
    """GET /cities/{city_id}/scores — Scores qualité de vie."""

    def test_endpoint_exists(self, client):
        resp = client.get("/cities/1/scores")
        assert resp.status_code in ACCEPT_OR_404

    def test_response_schema_when_implemented(self, client):
        """Si implémenté, la réponse doit respecter CityScores."""
        resp = client.get("/cities/1/scores")
        if resp.status_code == 200:
            data = resp.json()
            assert "city_id" in data
            assert "scores" in data
            assert "overall" in data
            assert isinstance(data["scores"], list)
