"""Client HTTP pour communiquer avec l'API FastAPI backend."""

from __future__ import annotations

import os
from typing import Any, Optional

import httpx

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

_client = httpx.Client(base_url=API_BASE_URL, timeout=10.0)


def _handle_response(response: httpx.Response) -> dict[str, Any]:
    """Gère la réponse HTTP et retourne le JSON."""
    if response.status_code == 404:
        return {}
    response.raise_for_status()
    return response.json()


# ── Health ─────────────────────────────────────────────────────
def check_health() -> dict:
    try:
        resp = _client.get("/health")
        return _handle_response(resp)
    except httpx.HTTPError:
        return {"status": "error", "version": "N/A"}


# ── Cities ─────────────────────────────────────────────────────
def search_cities(
    *,
    search: Optional[str] = None,
    region: Optional[str] = None,
    department: Optional[str] = None,
    min_population: Optional[int] = None,
    sort_by: str = "overall_score",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 20,
) -> dict:
    params: dict[str, Any] = {
        "sort_by": sort_by,
        "sort_order": sort_order,
        "page": page,
        "page_size": page_size,
    }
    if search:
        params["search"] = search
    if region:
        params["region"] = region
    if department:
        params["department"] = department
    if min_population is not None:
        params["min_population"] = min_population

    resp = _client.get("/cities", params=params)
    return _handle_response(resp)


def get_city(city_id: int) -> dict:
    resp = _client.get(f"/cities/{city_id}")
    return _handle_response(resp)


def get_city_scores(city_id: int) -> dict:
    resp = _client.get(f"/cities/{city_id}/scores")
    return _handle_response(resp)


# ── Reviews ────────────────────────────────────────────────────
def get_reviews(city_id: int, page: int = 1, page_size: int = 10) -> dict:
    resp = _client.get(
        f"/cities/{city_id}/reviews",
        params={"page": page, "page_size": page_size},
    )
    return _handle_response(resp)


def create_review(city_id: int, author: str, rating: int, comment: str, tags: list[str]) -> dict:
    resp = _client.post(
        f"/cities/{city_id}/reviews",
        json={
            "author": author,
            "rating": rating,
            "comment": comment,
            "tags": tags,
        },
    )
    return _handle_response(resp)


# ── Recommendations ───────────────────────────────────────────
def get_recommendations(city_id: int, k: int = 5) -> dict:
    resp = _client.get("/recommendations", params={"city_id": city_id, "k": k})
    return _handle_response(resp)
