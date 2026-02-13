"""Pydantic schemas — contrat API partagé entre backend et frontend."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Health ─────────────────────────────────────────────────────
class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"


# ── Scores ─────────────────────────────────────────────────────
class ScoreCategory(BaseModel):
    category: str = Field(..., examples=["environnement"])
    score: float = Field(..., ge=0, le=10, examples=[7.5])
    label: str = Field("", examples=["Environnement"])


class CityScores(BaseModel):
    city_id: int
    scores: list[ScoreCategory] = []
    overall: float = Field(0.0, ge=0, le=10, description="Score global moyen")


# ── City ───────────────────────────────────────────────────────
class City(BaseModel):
    """Résumé d'une ville (liste / recherche)."""

    id: int
    name: str = Field(..., examples=["Lyon"])
    department: str = Field("", examples=["Rhône"])
    region: str = Field("", examples=["Auvergne-Rhône-Alpes"])
    population: int = Field(0, examples=[516092])
    overall_score: float = Field(0.0, ge=0, le=10)


class CityDetail(City):
    """Détail complet d'une ville."""

    description: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    scores: list[ScoreCategory] = []


class CityListResponse(BaseModel):
    cities: list[City] = []
    total: int = 0
    page: int = 1
    page_size: int = 20


# ── Reviews ────────────────────────────────────────────────────
class Review(BaseModel):
    id: str = Field("", examples=["664a1f..."])
    city_id: int
    author: str = Field("Anonyme", examples=["Marie D."])
    rating: int = Field(..., ge=1, le=5, examples=[4])
    comment: str = Field("", examples=["Très agréable à vivre."])
    tags: list[str] = Field(default_factory=list, examples=[["transport", "culture"]])
    created_at: Optional[datetime] = None


class ReviewCreate(BaseModel):
    author: str = Field("Anonyme", max_length=100)
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field("", max_length=2000)
    tags: list[str] = Field(default_factory=list)


class ReviewsResponse(BaseModel):
    reviews: list[Review] = []
    total: int = 0


# ── Recommendations ───────────────────────────────────────────
class RecommendationItem(BaseModel):
    city: City
    similarity_score: float = Field(..., ge=0, le=1, examples=[0.87])
    common_strengths: list[str] = Field(
        default_factory=list,
        examples=[["environnement", "santé"]],
        description="Critères forts en commun (via STRONG_IN)",
    )


class RecommendationsResponse(BaseModel):
    source_city: str = Field(..., examples=["Lyon"])
    recommendations: list[RecommendationItem] = []
