"""Script de seed — charge les datasets dans les bases de données.

Usage: python -m backend.scripts.seed_all

TODO (optionnel — étudiants ou fourni) :
1. Lire datasets/cities.csv et insérer dans PostgreSQL
2. Lire datasets/scores.csv et insérer dans PostgreSQL
3. Lire datasets/reviews.jsonl et insérer dans MongoDB
4. Créer les nœuds et relations dans Neo4j
"""

from __future__ import annotations

import asyncio
import csv
import json
from pathlib import Path

DATASETS_DIR = Path(__file__).resolve().parents[5] / "datasets"


async def seed_postgres():
    """Charge cities.csv et scores.csv dans PostgreSQL."""
    print(f"[seed] Chargement depuis {DATASETS_DIR / 'cities.csv'}")
    # TODO: Implémenter
    print("[seed] PostgreSQL — À implémenter")


async def seed_mongo():
    """Charge reviews.jsonl dans MongoDB."""
    print(f"[seed] Chargement depuis {DATASETS_DIR / 'reviews.jsonl'}")
    # TODO: Implémenter
    print("[seed] MongoDB — À implémenter")


async def seed_neo4j():
    """Crée le graphe de villes, critères et relations dans Neo4j."""
    # TODO: Implémenter
    print("[seed] Neo4j — À implémenter")


async def main():
    print("=" * 50)
    print("SmartCity Explorer — Seed")
    print("=" * 50)
    await seed_postgres()
    await seed_mongo()
    await seed_neo4j()
    print("[seed] Terminé.")


if __name__ == "__main__":
    asyncio.run(main())
