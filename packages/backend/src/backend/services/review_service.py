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
        # TODO: Appeler self.repo.get_reviews(...) et convertir en ReviewsResponse.
        # ✂️ SOLUTION START
        docs, total = await self.repo.get_reviews(city_id, page=page, page_size=page_size)
        reviews = [Review(city_id=city_id, **doc) for doc in docs]
        # ✂️ SOLUTION END
        return ReviewsResponse(reviews=reviews, total=total)

    async def create_review(self, city_id: int, review: ReviewCreate) -> Review:
        """Crée un nouvel avis.

        TODO:
        1. Convertir ReviewCreate en dict
        2. Appeler self.repo.create_review(city_id, data)
        3. Retourner un Review
        """
        data = review.model_dump()
        doc = await self.repo.create_review(city_id, data)
        return Review(city_id=city_id, **doc)

