"""Repository MongoDB — accès aux avis utilisateurs.

TODO (étudiants) : Implémenter chaque méthode avec des requêtes MongoDB
via Motor (async).
"""

from __future__ import annotations

from datetime import datetime, timezone
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
        # ✂️ SOLUTION START
        query = {"city_id": city_id}

        total = await self.collection.count_documents(query)

        skip = (page - 1) * page_size
        cursor = (
            self.collection.find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(page_size)
        )

        docs = []
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            docs.append(doc)

        return docs, total
        # ✂️ SOLUTION END

    async def create_review(self, city_id: int, review_data: dict) -> dict:
        """Crée un nouvel avis pour une ville.

        TODO: Implémenter :
        - Ajouter city_id et created_at au document
        - Insérer dans la collection reviews
        - Retourner le document créé (avec id converti en str)
        """
        # ✂️ SOLUTION START
        doc = {
            **review_data,
            "city_id": city_id,
            "created_at": datetime.now(timezone.utc),
        }

        result = await self.collection.insert_one(doc)
        doc["id"] = str(result.inserted_id)
        doc.pop("_id", None)
        return doc
        # ✂️ SOLUTION END

    async def get_average_rating(self, city_id: int) -> Optional[float]:
        """Calcule la note moyenne pour une ville.

        TODO: Implémenter un pipeline d'agrégation MongoDB :
        - $match par city_id
        - $group avec $avg sur rating
        """
        # ✂️ SOLUTION START
        pipeline = [
            {"$match": {"city_id": city_id}},
            {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}}},
        ]

        results = await self.collection.aggregate(pipeline).to_list(length=1)
        if results:
            return round(results[0]["avg_rating"], 2)
        return None
        # ✂️ SOLUTION END
