# SmartCity Explorer — Sessions TP

## Objectifs pédagogiques

1. **Connexions DB** : Créer en Python les connexions à PostgreSQL, MongoDB et Neo4j à partir de la config (fichiers dans `backend/db/`, marqués **TODO**).
2. **Seed** : Compléter les **TODO** du script de seed pour charger les jeux de données dans les trois bases (après les connexions DB).
3. **Repositories (CRUD)** : Implémenter toutes les méthodes des repositories (chaque méthode est à faire, marquée **TODO**).
4. **Services** : Implémenter **quelques** méthodes des services (orchestration repo → modèles Pydantic) — voir Sprint 4.
5. **Fin** : Le reste des services, les **routes API** et le frontend sont **fournis — à ne pas implémenter**.

---

## Démarrer les bases de données (Docker Compose)

Avant de coder, lancez les trois bases en local :

```bash
docker compose up -d
```

Vérifiez que les services sont `healthy` :

```bash
docker compose ps
```

**Documentation détaillée** : voir **[docs/DOCKER_DB.md](docs/DOCKER_DB.md)** (ports, variables d’environnement, arrêt des conteneurs).

---

## Setup de l'environnement

```bash
# 1. Installer uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Installer les dépendances
uv sync --all-packages

# 3. Configurer les variables d'environnement
cp .env.example .env
# → Remplir les identifiants DB (POSTGRES_URL, MONGO_URL, NEO4J_URI, etc.)

# 4. Lancer les bases (voir docs/DOCKER_DB.md)
docker compose up -d

# Après cette étape, sauter les étapes seed, dev-backend et passer directement à la partie Sprints

# 5. Après avoir implémenté les connexions DB et le seed : charger les données
just seed

# 6. Vérifier que le serveur démarre
just dev-backend
# → http://localhost:8000/docs
```

Rôle des bases :
- **PostgreSQL** : Données structurées des villes (profils, scores, filtrage).
- **MongoDB** : Documents flexibles pour les avis utilisateurs (CRUD, agrégation).
- **Neo4j** : Graphe de similarité entre villes (relations, recommandations).

---

## Sprints

| Étape | Contenu | À implémenter |
|-------|---------|----------------|
| **1. DB** | Connexions PostgreSQL, MongoDB, Neo4j | Oui — **TODO** dans `backend/db/` |
| **2. Seed** | Chargement des datasets (cities, scores, reviews, graphe Neo4j) | Oui — **TODO** dans le script de seed |
| **3. Repos** | Toutes les méthodes des repositories (Postgres, Mongo, Neo4j) | Oui — **TODO** dans chaque méthode |
| **4. Services** | Une méthode par service : `search_cities`, `get_reviews`, partie de `get_recommendations` | Oui — **TODO** + bloc à compléter |
| **5. Fin** | Reste des services, routes API, frontend | **Non** — fourni, ne pas modifier |

---

## Lancer les tests par sprint

Les tests sont regroupés par marqueur pytest. Vous pouvez lancer uniquement les tests cohérents avec le sprint en cours :

```bash
# Sprint 1 — Connexions DB
uv run pytest -m sprint1 -v

# Sprint 2 — Seed (module importable + fonctions présentes)
uv run pytest -m sprint2 -v

# Sprint 3 — Repositories (Postgres, Mongo, Neo4j)
uv run pytest -m sprint3 -v

# Sprint 4 — Services (city, review, recommendation)
uv run pytest -m sprint4 -v

# Sprint 5 — Intégration (API, santé)
uv run pytest -m sprint5 -v
```

**Tous les tests unitaires (sprints 1 à 4)** :

```bash
uv run pytest -m "sprint1 or sprint2 or sprint3 or sprint4" -v
```

**Tous les tests (y compris intégration)** :

```bash
uv run pytest -v
```

---

## Sprint 1 : Connexions DB (PostgreSQL, MongoDB, Neo4j)

**Objectif** : Implémenter les **TODO** de création des connexions à partir de la configuration (singletons).

### Fichiers à modifier (rechercher `# TODO` dans ces fichiers)

| Fichier | À compléter |
|---------|-------------|
| `packages/backend/src/backend/db/postgres.py` | `get_engine()` — créer l’engine async avec `settings.postgres_url` ; `get_session_factory()` — créer la session factory avec `get_engine()`. |
| `packages/backend/src/backend/db/mongo.py` | `get_mongo_db()` — créer le client Motor avec `settings.mongo_url`, retourner `client[settings.mongo_db]`. |
| `packages/backend/src/backend/db/neo4j.py` | `get_neo4j_driver()` — créer le driver avec `AsyncGraphDatabase.driver(uri, auth=(user, password))`. |

### Tests

```bash
uv run pytest -m sprint1 -v
# ou : uv run pytest tests/unit/test_db_postgres.py tests/unit/test_db_mongo.py tests/unit/test_db_neo4j.py -v
```

---

## Sprint 2 : Seed (chargement des données)

**Objectif** : Compléter les **TODO** du script de seed pour charger cities/scores dans PostgreSQL, reviews dans MongoDB, et le graphe dans Neo4j.

### Fichier à modifier

`packages/backend/src/backend/scripts/seed_all.py`

- **TODO** en tête de fichier : rappel des trois parties à implémenter.
- **TODO** + blocs à compléter dans : `seed_postgres()`, `seed_mongo()`, `seed_neo4j()`.

Après avoir implémenté les connexions DB (Sprint 1), exécuter :

```bash
just seed
# ou : python -m backend.scripts.seed_all
```

### Tests

```bash
uv run pytest -m sprint2 -v
# Vérifie que le module seed est importable et expose seed_postgres, seed_mongo, seed_neo4j
```

---

## Sprint 3 : Repositories (tout est à implémenter)

**Objectif** : Implémenter **toutes** les méthodes des repositories (chaque méthode contient un **TODO** et un bloc à compléter).

### Postgres — `packages/backend/src/backend/repositories/postgres_repo.py`

| Méthode | TODO / Rôle |
|---------|-------------|
| `get_city_by_id(city_id)` | SELECT une ville par ID (toutes les colonnes). |
| `get_city_scores(city_id)` | SELECT des scores par catégorie pour une ville (table `scores`). |
| `get_cities(**filters)` | SELECT liste de villes avec filtres (search, region, department, min_population), tri et pagination. |

### Mongo — `packages/backend/src/backend/repositories/mongo_repo.py`

| Méthode | TODO / Rôle |
|---------|-------------|
| `get_reviews(city_id, page, page_size)` | Lecture paginée (find + sort + skip/limit), convertir `_id` en `id` (str). |
| `create_review(city_id, review_data)` | Créer un document (ajouter `city_id`, `created_at`), retourner le doc avec `id` (str). |
| `get_average_rating(city_id)` | Pipeline d’agrégation : `$match` par `city_id`, `$group` avec `$avg` sur `rating`. |

### Neo4j — `packages/backend/src/backend/repositories/neo4j_repo.py`

| Méthode | TODO / Rôle |
|---------|-------------|
| `get_similar_cities(city_id, k)` | MATCH ville → SIMILAR_TO → autres villes ; retourner les K plus proches avec score et critères communs. |
| `get_city_strengths(city_id)` | MATCH ville → STRONG_IN → critères ; retourner les noms des critères. |

### Tests

```bash
uv run pytest -m sprint3 -v
# ou : uv run pytest tests/unit/test_postgres_repo.py tests/unit/test_mongo_repo.py tests/unit/test_neo4j_repo.py -v
```

---

## Sprint 4 : Services (quelques méthodes à implémenter)

**Objectif** : Implémenter **une méthode (ou un bloc) par service** : appeler le repository et convertir le résultat en modèle Pydantic. Le reste des méthodes de chaque service est fourni.

### Fichiers à modifier (rechercher `# TODO` et `# ✂️ SOLUTION START`)

| Fichier | Méthode à compléter | Rôle |
|---------|---------------------|------|
| `packages/backend/src/backend/services/city_service.py` | `search_cities` | Appeler `self.repo.get_cities(...)` et convertir les lignes en `CityListResponse` (liste de `City`, total, page, page_size). |
| `packages/backend/src/backend/services/review_service.py` | `get_reviews` | Appeler `self.repo.get_reviews(city_id, page, page_size)` et convertir les docs en `ReviewsResponse` (liste de `Review`, total). |
| `packages/backend/src/backend/services/recommendation_service.py` | `get_recommendations` | Appeler `self.neo4j_repo.get_similar_cities(city_id, k)` pour obtenir les villes similaires (le reste de la méthode — construction des `RecommendationItem` et `RecommendationsResponse` — est fourni). |

**Fourni (ne pas modifier)** : `get_city_detail`, `get_city_scores` (city_service) ; `create_review` (review_service) ; le corps de `get_recommendations` après l’appel à `get_similar_cities` (recommendation_service).

### Tests

```bash
uv run pytest -m sprint4 -v
# ou : uv run pytest tests/unit/test_city_service.py tests/unit/test_review_service.py tests/unit/test_reco_service.py -v
```

---

## Sprint 5 : Fin (rien à implémenter)

Le reste des **services**, les **routes API** et le frontend sont fournis. Ils utilisent les repositories et les méthodes de service que vous avez implémentés. Aucun code à écrire ici.

### Intégration

Valider l’application de bout en bout :

```bash
# Tous les tests unitaires (sprints 1 à 4)
uv run pytest -m "sprint1 or sprint2 or sprint3 or sprint4" -v

# Tests d’intégration (sprint 5)
uv run pytest -m sprint5 -v

# Ou tout en une fois
uv run pytest -v

# Style
just lint
```

---

## Résumé — Ce que les étudiants complètent

| Sprint | Fichiers | Contenu |
|--------|----------|---------|
| 1 | `db/postgres.py`, `db/mongo.py`, `db/neo4j.py` | 4 blocs (engine, session_factory, mongo_db, neo4j_driver) — **TODO** |
| 2 | `backend/scripts/seed_all.py` | 3 blocs (seed_postgres, seed_mongo, seed_neo4j) — **TODO** |
| 3 | `repositories/postgres_repo.py` | 3 méthodes — **TODO** |
| 3 | `repositories/mongo_repo.py` | 3 méthodes — **TODO** |
| 3 | `repositories/neo4j_repo.py` | 2 méthodes — **TODO** |
| 4 | `services/city_service.py` | `search_cities` — **TODO** |
| 4 | `services/review_service.py` | `get_reviews` — **TODO** |
| 4 | `services/recommendation_service.py` | `get_recommendations` (appel à `get_similar_cities`) — **TODO** |
| 5 | — | Rien : reste des services, API et frontend fournis |

**Total à compléter** : connexions DB + seed + toutes les méthodes des repositories + 3 blocs dans les services. Tout le reste est fourni.

**Docker** : voir **[docs/DOCKER_DB.md](docs/DOCKER_DB.md)** pour lancer les bases avec `docker compose`.
