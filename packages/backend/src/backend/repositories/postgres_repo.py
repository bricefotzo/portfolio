"""Repository PostgreSQL — accès aux villes et scores.

TODO (étudiants) : Implémenter chaque méthode avec des requêtes SQL
via SQLAlchemy async (ou raw SQL avec asyncpg).
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession


class PostgresRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_cities(
        self,
        *,
        search: Optional[str] = None,
        region: Optional[str] = None,
        department: Optional[str] = None,
        min_population: Optional[int] = None,
        sort_by: str = "overall_score",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict], int]:
        """Recherche de villes avec filtres, tri et pagination.

        TODO: Implémenter la requête SQL avec :
        - Filtre ILIKE sur le nom de ville (search)
        - Filtre exact sur region et department
        - Filtre >= sur population
        - Tri dynamique (overall_score, population, name…)
        - Pagination OFFSET/LIMIT
        - Retourner (liste_de_dicts, total_count)
        """
        raise NotImplementedError("PostgresRepository.get_cities — À implémenter")

    async def get_city_by_id(self, city_id: int) -> Optional[dict]:
        """Récupère les détails d'une ville par son ID.

        TODO: Implémenter la requête SQL pour récupérer une ville
        avec toutes ses colonnes (name, department, region, population,
        description, latitude, longitude, overall_score).
        """
        raise NotImplementedError("PostgresRepository.get_city_by_id — À implémenter")

    async def get_city_scores(self, city_id: int) -> list[dict]:
        """Récupère les scores par catégorie pour une ville.

        TODO: Implémenter la jointure entre cities et scores.
        Retourner une liste de dicts: [{"category": ..., "score": ..., "label": ...}]
        """
        raise NotImplementedError("PostgresRepository.get_city_scores — À implémenter")
