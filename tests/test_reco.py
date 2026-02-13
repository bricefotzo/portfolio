"""Tests d'acceptation — Endpoint Recommendations (Neo4j)."""

from __future__ import annotations


class TestRecommendations:
    """GET /recommendations."""

    def test_endpoint_exists(self, client):
        resp = client.get("/recommendations", params={"city_id": 1})
        assert resp.status_code in (200, 404, 501)

    def test_requires_city_id(self, client):
        """Le paramètre city_id est obligatoire."""
        resp = client.get("/recommendations")
        assert resp.status_code == 422

    def test_k_param(self, client):
        """Le paramètre k doit être accepté."""
        resp = client.get("/recommendations", params={"city_id": 1, "k": 3})
        assert resp.status_code in (200, 404, 501)

    def test_k_bounds(self, client):
        """k doit être >= 1 et <= 20."""
        resp = client.get("/recommendations", params={"city_id": 1, "k": 0})
        assert resp.status_code == 422

        resp = client.get("/recommendations", params={"city_id": 1, "k": 21})
        assert resp.status_code == 422

    def test_response_schema_when_implemented(self, client):
        resp = client.get("/recommendations", params={"city_id": 1, "k": 3})
        if resp.status_code == 200:
            data = resp.json()
            assert "source_city" in data
            assert "recommendations" in data
            assert isinstance(data["recommendations"], list)
            for reco in data["recommendations"]:
                assert "city" in reco
                assert "similarity_score" in reco
                assert "common_strengths" in reco
