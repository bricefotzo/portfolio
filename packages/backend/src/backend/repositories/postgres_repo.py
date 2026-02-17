"""Repository PostgreSQL — accès aux villes et scores.

TODO (étudiants) : Implémenter chaque méthode avec des requêtes SQL
via SQLAlchemy async (ou raw SQL avec asyncpg).
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# Colonnes autorisées pour le tri (protection contre l'injection SQL)
_ALLOWED_SORT = {"overall_score", "population", "name", "department", "region"}


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
        # TODO: Implémenter la requête SQL (filtres, tri, pagination, count)
        # ✂️ SOLUTION START
        conditions = []
        params: dict = {}

        if search:
            conditions.append("name ILIKE :search")
            params["search"] = f"%{search}%"
        if region:
            conditions.append("region = :region")
            params["region"] = region
        if department:
            conditions.append("department = :department")
            params["department"] = department
        if min_population is not None:
            conditions.append("population >= :min_pop")
            params["min_pop"] = min_population

        where_clause = (" WHERE " + " AND ".join(conditions)) if conditions else ""

        # Sécuriser le tri
        col = sort_by if sort_by in _ALLOWED_SORT else "overall_score"
        direction = "ASC" if sort_order == "asc" else "DESC"
        order_clause = f" ORDER BY {col} {direction}"

        # Total
        count_sql = f"SELECT COUNT(*) FROM cities{where_clause}"
        result = await self.session.execute(text(count_sql), params)
        total = result.scalar_one()

        # Données paginées
        offset = (page - 1) * page_size
        data_sql = (
            f"SELECT id, name, department, region, population, overall_score "
            f"FROM cities{where_clause}{order_clause} "
            f"LIMIT :limit OFFSET :offset"
        )
        params["limit"] = page_size
        params["offset"] = offset

        result = await self.session.execute(text(data_sql), params)
        rows = result.mappings().all()
        return [dict(r) for r in rows], total
        # ✂️ SOLUTION END

    async def get_city_by_id(self, city_id: int) -> Optional[dict]:
        """Récupère les détails d'une ville par son ID.

        TODO: Implémenter la requête SQL pour récupérer une ville
        avec toutes ses colonnes (name, department, region, population,
        description, latitude, longitude, overall_score).
        """
        # TODO: Implémenter SELECT une ville par id
        # ✂️ SOLUTION START
        sql = text(
            "SELECT id, name, department, region, population, description, "
            "latitude, longitude, overall_score "
            "FROM cities WHERE id = :city_id"
        )
        result = await self.session.execute(sql, {"city_id": city_id})
        row = result.mappings().first()
        return dict(row) if row else None
        # ✂️ SOLUTION END

    async def get_city_scores(self, city_id: int) -> list[dict]:
        """Récupère les scores par catégorie pour une ville.

        TODO: Implémenter la jointure entre cities et scores.
        Retourner une liste de dicts: [{"category": ..., "score": ..., "label": ...}]
        """
        # TODO: Implémenter SELECT scores pour une ville (table scores)
        # ✂️ SOLUTION START
        sql = text(
            "SELECT category, label, score "
            "FROM scores WHERE city_id = :city_id "
            "ORDER BY category"
        )
        result = await self.session.execute(sql, {"city_id": city_id})
        return [dict(r) for r in result.mappings().all()]
        # ✂️ SOLUTION END
