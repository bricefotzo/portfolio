"""Repository Neo4j — graphe de similarité et recommandations.

TODO (étudiants) : Implémenter chaque méthode avec des requêtes Cypher
via le driver Neo4j async.
"""

from __future__ import annotations

from neo4j import AsyncDriver


class Neo4jRepository:
    def __init__(self, driver: AsyncDriver):
        self.driver = driver

    async def get_similar_cities(
        self,
        city_id: int,
        k: int = 5,
    ) -> list[dict]:
        """Trouve les K villes les plus similaires via le graphe.

        TODO: Implémenter la requête Cypher :
        - MATCH sur le nœud City avec city_id
        - Traverser les relations SIMILAR_TO (pondérées)
          OU exploiter les relations STRONG_IN vers des critères communs
        - Retourner les K villes les plus proches avec :
          * city (dict des propriétés)
          * similarity_score
          * common_strengths (liste de critères communs via STRONG_IN)

        Exemple de structure de graphe attendue :
          (City)-[:STRONG_IN]->(Criterion)
          (City)-[:SIMILAR_TO {score: 0.87}]->(City)
        """
        # ✂️ SOLUTION START
        query = """
        MATCH (source:City {city_id: $city_id})-[r:SIMILAR_TO]->(target:City)
        OPTIONAL MATCH (source)-[:STRONG_IN]->(c:Criterion)<-[:STRONG_IN]-(target)
        WITH target, r.score AS similarity_score,
             COLLECT(DISTINCT c.name) AS common_strengths
        RETURN target {
            .city_id, .name, .department, .region,
            .population, .overall_score
        } AS city,
        similarity_score,
        common_strengths
        ORDER BY similarity_score DESC
        LIMIT $k
        """

        async with self.driver.session() as session:
            result = await session.run(query, city_id=city_id, k=k)
            records = await result.data()

        return [
            {
                "city": record["city"],
                "similarity_score": record["similarity_score"],
                "common_strengths": record["common_strengths"],
            }
            for record in records
        ]
        # ✂️ SOLUTION END

    async def get_city_strengths(self, city_id: int) -> list[str]:
        """Récupère les points forts d'une ville (relations STRONG_IN).

        TODO: Implémenter :
        - MATCH (c:City {city_id: $city_id})-[:STRONG_IN]->(cr:Criterion)
        - RETURN cr.name
        """
        # ✂️ SOLUTION START
        query = """
        MATCH (c:City {city_id: $city_id})-[:STRONG_IN]->(cr:Criterion)
        RETURN cr.name AS name
        """

        async with self.driver.session() as session:
            result = await session.run(query, city_id=city_id)
            records = await result.data()

        return [record["name"] for record in records]
        # ✂️ SOLUTION END
