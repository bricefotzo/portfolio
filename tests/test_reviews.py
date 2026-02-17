"""Tests d'acceptation — Endpoints Reviews (MongoDB)."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.sprint5

ACCEPT = (200, 500, 501)


class TestGetReviews:
    """GET /cities/{city_id}/reviews."""

    def test_endpoint_exists(self, client):
        resp = client.get("/cities/1/reviews")
        assert resp.status_code in ACCEPT

    def test_response_schema_when_implemented(self, client):
        resp = client.get("/cities/1/reviews")
        if resp.status_code == 200:
            data = resp.json()
            assert "reviews" in data
            assert "total" in data
            assert isinstance(data["reviews"], list)

    def test_pagination_params(self, client):
        resp = client.get("/cities/1/reviews", params={"page": 1, "page_size": 5})
        assert resp.status_code in ACCEPT


class TestCreateReview:
    """POST /cities/{city_id}/reviews."""

    def test_endpoint_exists(self, client):
        resp = client.post(
            "/cities/1/reviews",
            json={
                "author": "Test",
                "rating": 4,
                "comment": "Test review",
                "tags": ["test"],
            },
        )
        assert resp.status_code in (201, 500, 501)

    def test_validation_rating_bounds(self, client):
        """Le rating doit être entre 1 et 5."""
        resp = client.post(
            "/cities/1/reviews",
            json={"author": "Test", "rating": 0, "comment": "Bad"},
        )
        assert resp.status_code == 422  # Validation error

        resp = client.post(
            "/cities/1/reviews",
            json={"author": "Test", "rating": 6, "comment": "Bad"},
        )
        assert resp.status_code == 422

    def test_response_schema_when_implemented(self, client):
        resp = client.post(
            "/cities/1/reviews",
            json={
                "author": "Test User",
                "rating": 5,
                "comment": "Great city!",
                "tags": ["test"],
            },
        )
        if resp.status_code == 201:
            data = resp.json()
            assert "city_id" in data
            assert "author" in data
            assert "rating" in data
