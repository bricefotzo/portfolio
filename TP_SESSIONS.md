# SmartCity Explorer — Sessions TP

## Setup de l'environnement

```bash
# 1. Installer uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Installer les dépendances
uv sync --all-packages

# 3. Configurer les variables d'environnement
cp .env.example .env
# → Remplir les identifiants DB (POSTGRES_URI, MONGODB_URI, NEO4J_URI)

# 4. Lancer les bases de données
docker compose up -d

# 5. Charger les données initiales
just seed

# 6. Vérifier que le serveur démarre
just dev-backend
# → http://localhost:8000/docs

# 7. Vérifier que les tests de base passent
uv run pytest tests/test_health.py -v
```

Each database serves a specific purpose:
- **PostgreSQL** : Données structurées des villes (profils, scores, filtrage)
- **MongoDB** : Documents flexibles pour les avis utilisateurs (CRUD, agrégation)
- **Neo4j** : Graphe de similarité entre villes (relations, recommandations)

---

## Sprint 1 : Repository PostgreSQL

Implémenter les requêtes SQL du repository PostgreSQL pour gérer les données des villes : récupérer une ville par ID, lister ses scores par catégorie, et rechercher des villes avec filtres dynamiques, tri et pagination.

### Fichier à modifier

`packages/backend/src/backend/repositories/postgres_repo.py`

Méthodes : `get_city_by_id`, `get_city_scores`, `get_cities`

### Tests

```bash
uv run pytest tests/unit/test_tp1_postgres_repo.py -v
```

---

## Sprint 2 : Service City

Implémenter la couche service qui orchestre les appels au repository PostgreSQL et convertit les données brutes (dicts) en modèles Pydantic (`CityListResponse`, `CityDetail`, `CityScores`).

### Fichier à modifier

`packages/backend/src/backend/services/city_service.py`

Méthodes : `search_cities`, `get_city_detail`, `get_city_scores`

### Tests

```bash
uv run pytest tests/unit/test_tp2_city_service.py tests/test_cities.py -v
```

---

## Sprint 3 : MongoDB + Service Reviews

Implémenter les opérations MongoDB pour les avis utilisateurs (lecture paginée, création, calcul de moyenne via pipeline d'agrégation), puis la couche service qui convertit les résultats en modèles Pydantic (`ReviewsResponse`, `Review`).

### Fichiers à modifier

- `packages/backend/src/backend/repositories/mongo_repo.py` — Méthodes : `get_reviews`, `create_review`, `get_average_rating`
- `packages/backend/src/backend/services/review_service.py` — Méthodes : `get_reviews`, `create_review`

### Tests

```bash
uv run pytest tests/unit/test_tp3_mongo_repo.py tests/unit/test_tp3_review_service.py tests/test_reviews.py -v
```

---

## Sprint 4 : Neo4j + Recommandations

Implémenter les requêtes Cypher pour parcourir le graphe de similarité entre villes et identifier leurs points forts, puis le service de recommandation qui combine données PostgreSQL et Neo4j pour enrichir les résultats.

### Fichiers à modifier

- `packages/backend/src/backend/repositories/neo4j_repo.py` — Méthodes : `get_similar_cities`, `get_city_strengths`
- `packages/backend/src/backend/services/recommendation_service.py` — Méthode : `get_recommendations`

### Tests

```bash
uv run pytest tests/unit/test_tp4_neo4j_repo.py tests/unit/test_tp4_reco_service.py tests/test_reco.py -v
```

---

## Sprint 5 : Intégration

Valider le fonctionnement complet de l'application de bout en bout.

```bash
# Lancer tous les tests
uv run pytest -v

# Vérifier le style du code
just lint
```
