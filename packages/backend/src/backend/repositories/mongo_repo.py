"""Repository MongoDB — accès aux avis utilisateurs.

TODO (étudiants) : Implémenter chaque méthode avec des requêtes MongoDB
via Motor (async).
"""

from __future__ import annotations

from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase


class MongoRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["reviews"]

    async def get_reviews(
        self,
        city_id: int,
        *,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[dict], int]:
        """Récupère les avis pour une ville avec pagination.

        TODO: Implémenter avec Motor :
        - Filtrer par city_id
        - Trier par created_at décroissant
        - Paginer avec skip/limit
        - Retourner (liste_de_docs, total_count)
        - Convertir ObjectId en str pour le champ "id"
        """
        raise NotImplementedError("MongoRepository.get_reviews — À implémenter")

    async def create_review(self, city_id: int, review_data: dict) -> dict:
        """Crée un nouvel avis pour une ville.

        TODO: Implémenter :
        - Ajouter city_id et created_at au document
        - Insérer dans la collection reviews
        - Retourner le document créé (avec id converti en str)
        """
        raise NotImplementedError("MongoRepository.create_review — À implémenter")

    async def get_average_rating(self, city_id: int) -> Optional[float]:
        """Calcule la note moyenne pour une ville.

        TODO: Implémenter un pipeline d'agrégation MongoDB :
        - $match par city_id
        - $group avec $avg sur rating
        """
        raise NotImplementedError("MongoRepository.get_average_rating — À implémenter")
