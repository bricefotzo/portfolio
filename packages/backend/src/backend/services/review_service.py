"""Service métier — Avis utilisateurs (MongoDB).

TODO (étudiants) : Implémenter la logique d'orchestration.
"""

from __future__ import annotations

from backend.models import Review, ReviewCreate, ReviewsResponse
from backend.repositories.mongo_repo import MongoRepository


class ReviewService:
    def __init__(self, repo: MongoRepository):
        self.repo = repo

    async def get_reviews(
        self,
        city_id: int,
        *,
        page: int = 1,
        page_size: int = 10,
    ) -> ReviewsResponse:
        """Récupère les avis d'une ville.

        TODO: Appeler self.repo.get_reviews(...) et convertir en ReviewsResponse.
        """
        raise NotImplementedError("ReviewService.get_reviews — À implémenter")

    async def create_review(self, city_id: int, review: ReviewCreate) -> Review:
        """Crée un nouvel avis.

        TODO:
        1. Convertir ReviewCreate en dict
        2. Appeler self.repo.create_review(city_id, data)
        3. Retourner un Review
        """
        raise NotImplementedError("ReviewService.create_review — À implémenter")
