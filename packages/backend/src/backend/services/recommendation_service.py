"""Service métier — Recommandations (Neo4j).

TODO (étudiants) : Implémenter la logique d'orchestration.
"""

from __future__ import annotations

from typing import Optional

from backend.models import RecommendationsResponse
from backend.repositories.neo4j_repo import Neo4jRepository
from backend.repositories.postgres_repo import PostgresRepository


class RecommendationService:
    def __init__(self, neo4j_repo: Neo4jRepository, postgres_repo: PostgresRepository):
        self.neo4j_repo = neo4j_repo
        self.postgres_repo = postgres_repo

    async def get_recommendations(
        self,
        city_id: int,
        k: int = 5,
    ) -> Optional[RecommendationsResponse]:
        """Recommandations de villes similaires.

        TODO:
        1. Vérifier que la ville source existe (postgres_repo.get_city_by_id)
        2. Appeler neo4j_repo.get_similar_cities(city_id, k)
        3. Pour chaque résultat, enrichir avec les infos Postgres si besoin
        4. Construire et retourner un RecommendationsResponse
        """
        raise NotImplementedError("RecommendationService.get_recommendations — À implémenter")
