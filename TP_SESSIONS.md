# SmartCity Explorer — Sessions TP

## Vue d'ensemble

| Sprint | Horaire | Thème | Fichiers à implémenter | Tests à lancer |
|--------|---------|-------|------------------------|----------------|
| **Sprint 1** | Jour 1 — Matin (4h) | Setup + PostgreSQL | `postgres_repo.py` | `tests/unit/test_tp1_postgres_repo.py` |
| **Sprint 2** | Jour 1 — Après-midi (4h) | Service City | `city_service.py` | `tests/unit/test_tp2_city_service.py` + `tests/test_cities.py` |
| **Sprint 3** | Jour 2 — Matin (4h) | MongoDB + Reviews | `mongo_repo.py` + `review_service.py` | `tests/unit/test_tp3_*.py` + `tests/test_reviews.py` |
| **Sprint 4** | Jour 2 — Après-midi (4h) | Neo4j + Recommandations | `neo4j_repo.py` + `recommendation_service.py` | `tests/unit/test_tp4_*.py` + `tests/test_reco.py` |
| **Sprint 5** | Jour 3 — Matin (4h) | Intégration + Seed + Révision | `seed_all.py` (optionnel) | `uv run pytest -v` (tous) |
| **Contrôle** | Jour 3 — Soir | Évaluation | — | — |

Each database serves a specific purpose:
- **PostgreSQL** : Données structurées des villes (profils, scores, filtrage)
- **MongoDB** : Documents flexibles pour les avis utilisateurs (CRUD, agrégation)
- **Neo4j** : Graphe de similarité entre villes (relations, recommandations)

---

## Sprint 1: Setup + Repository PostgreSQL

Bienvenue dans le projet SmartCity Explorer. Aujourd'hui, nous allons mettre en place l'environnement et implémenter les premières requêtes SQL via SQLAlchemy async.

### Setup de l'environnement

**Step 1:** Installer uv (si pas déjà fait)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Step 2:** Installer les dépendances
```bash
uv sync --all-packages
```

**Step 3:** Copier et configurer les variables d'environnement
```bash
cp .env.example .env
# → Remplir les identifiants DB (POSTGRES_URI, MONGODB_URI, NEO4J_URI)
```

**Step 4:** Lancer les bases de données
```bash
docker compose up -d
```

**Step 5:** Charger les données initiales
```bash
just seed
```

**Step 6:** Vérifier que le serveur démarre
```bash
just dev-backend
# → http://localhost:8000/docs
```

**Step 7:** Vérifier que les tests de base passent
```bash
uv run pytest tests/test_health.py -v
```

### Rappel d'architecture
```
Route API  →  Service  →  Repository  →  Base de données
(FastAPI)     (logique)   (requêtes)     (PostgreSQL / MongoDB / Neo4j)
```

### Task

Implémenter les requêtes SQL du repository PostgreSQL pour gérer les données des villes.

### User Stories

- "En tant que développeur, je veux récupérer les informations d'une ville par son identifiant"
- "En tant que développeur, je veux lister les scores d'une ville par catégorie"
- "En tant que développeur, je veux rechercher des villes avec des filtres, du tri et de la pagination"

### Methods to Implement

File: `packages/backend/src/backend/repositories/postgres_repo.py`

#### 1. `get_city_by_id(city_id)` → `dict | None`
- **Difficulté** : ★☆☆
- **Concept** : SELECT simple avec paramètre
- **SQL attendu** : `SELECT id, name, department, region, population, description, latitude, longitude, overall_score FROM cities WHERE id = :city_id`
- **Retour** : `dict(row)` si trouvé, `None` sinon

#### 2. `get_city_scores(city_id)` → `list[dict]`
- **Difficulté** : ★☆☆
- **Concept** : SELECT avec filtre, retour de liste
- **SQL attendu** : `SELECT category, label, score FROM scores WHERE city_id = :city_id ORDER BY category`
- **Retour** : liste de `{"category": ..., "score": ..., "label": ...}`

#### 3. `get_cities(**filters)` → `tuple[list[dict], int]`
- **Difficulté** : ★★★
- **Concepts** : filtres dynamiques, ILIKE, tri sécurisé, pagination OFFSET/LIMIT
- **Étapes** :
  1. Construire la clause WHERE dynamiquement selon les filtres
  2. Requête COUNT(*) pour le total
  3. Requête SELECT avec ORDER BY et LIMIT/OFFSET
  4. Retourner `(liste_de_dicts, total)`
- **Attention** : ne pas oublier de valider `sort_by` contre `_ALLOWED_SORT`

### Testing
```bash
# Lancer les tests unitaires Sprint 1
uv run pytest tests/unit/test_tp1_postgres_repo.py -v
```

| Test | Méthode testée | Ce qui est vérifié |
|------|---------------|-------------------|
| `TestGetCityById::test_returns_dict_when_found` | `get_city_by_id` | Retourne un dict |
| `TestGetCityById::test_returns_none_when_not_found` | `get_city_by_id` | Retourne None si absent |
| `TestGetCityById::test_contains_all_required_fields` | `get_city_by_id` | Toutes les colonnes présentes |
| `TestGetCityScores::test_returns_list_of_dicts` | `get_city_scores` | Liste de dicts |
| `TestGetCityScores::test_score_dict_has_required_keys` | `get_city_scores` | Clés category/score/label |
| `TestGetCityScores::test_returns_empty_list_when_no_scores` | `get_city_scores` | Liste vide si rien |
| `TestGetCities::test_returns_tuple_list_and_total` | `get_cities` | Retour (list, int) |
| `TestGetCities::test_returns_dicts_with_city_fields` | `get_cities` | Champs de ville |
| `TestGetCities::test_empty_results` | `get_cities` | Gestion du vide |
| `TestGetCities::test_calls_execute_twice` | `get_cities` | 2 requêtes (count + data) |
| `TestGetCities::test_accepts_*` | `get_cities` | Paramètres acceptés |

---

## Sprint 2: Service City (Orchestration)

Maintenant que le repository fonctionne, nous allons implémenter la couche service qui orchestre les appels au repository et convertit les données brutes en modèles Pydantic.

### Task

Implémenter la couche d'orchestration entre les routes API et le repository PostgreSQL.

### User Stories

- "En tant qu'utilisateur, je veux rechercher des villes et obtenir une liste paginée"
- "En tant qu'utilisateur, je veux voir les détails d'une ville avec ses scores"
- "En tant qu'utilisateur, je veux consulter les scores d'une ville par catégorie"

### Methods to Implement

File: `packages/backend/src/backend/services/city_service.py`

#### 1. `search_cities(**params)` → `CityListResponse`
- **Difficulté** : ★☆☆
- **Logique** :
  1. Appeler `self.repo.get_cities(...)` en transmettant tous les paramètres
  2. Convertir chaque dict en objet `City(**row)`
  3. Retourner `CityListResponse(cities=..., total=..., page=..., page_size=...)`

#### 2. `get_city_detail(city_id)` → `CityDetail | None`
- **Difficulté** : ★★☆
- **Logique** :
  1. Appeler `self.repo.get_city_by_id(city_id)` → retourner `None` si absent
  2. Appeler `self.repo.get_city_scores(city_id)`
  3. Convertir les scores en `[ScoreCategory(**s) for s in score_rows]`
  4. Combiner : `CityDetail(**row, scores=scores)`

#### 3. `get_city_scores(city_id)` → `CityScores | None`
- **Difficulté** : ★★☆
- **Logique** :
  1. Vérifier que la ville existe (`get_city_by_id`) → `None` si absente
  2. Récupérer les scores (`get_city_scores` du repo)
  3. Retourner `CityScores(city_id=..., scores=..., overall=...)`

### Testing
```bash
# Tests unitaires Sprint 2
uv run pytest tests/unit/test_tp2_city_service.py -v

# Tests d'acceptation (endpoint complet route → service → repo)
uv run pytest tests/test_cities.py -v

# Les deux ensemble
uv run pytest tests/unit/test_tp2_city_service.py tests/test_cities.py -v
```

| Test | Méthode testée | Ce qui est vérifié |
|------|---------------|-------------------|
| `TestSearchCities::test_returns_city_list_response` | `search_cities` | Type de retour |
| `TestSearchCities::test_maps_rows_to_city_objects` | `search_cities` | Conversion dict→City |
| `TestSearchCities::test_passes_parameters_to_repo` | `search_cities` | Transmission des params |
| `TestSearchCities::test_empty_results` | `search_cities` | Gestion du vide |
| `TestSearchCities::test_preserves_page_info` | `search_cities` | Page/page_size conservés |
| `TestGetCityDetail::test_returns_city_detail_with_scores` | `get_city_detail` | Combinaison ville+scores |
| `TestGetCityDetail::test_returns_none_when_city_not_found` | `get_city_detail` | None si absent |
| `TestGetCityDetail::test_calls_both_repo_methods` | `get_city_detail` | Appel des 2 méthodes repo |
| `TestGetCityScores::test_returns_city_scores` | `get_city_scores` | CityScores correct |
| `TestGetCityScores::test_returns_none_when_city_not_found` | `get_city_scores` | None si absent |

---

## Sprint 3: MongoDB + Service Reviews

Nous abordons maintenant MongoDB, une base documentaire. Vous allez implémenter les opérations CRUD pour les avis utilisateurs, puis la couche service correspondante.

### Task

Implémenter les opérations MongoDB pour gérer les avis, puis orchestrer via le service.

### User Stories

- "En tant qu'utilisateur, je veux consulter les avis sur une ville avec pagination"
- "En tant qu'utilisateur, je veux publier un avis sur une ville"
- "En tant que développeur, je veux calculer la note moyenne d'une ville via agrégation"

### Part 1: Repository MongoDB (~2h30)

File: `packages/backend/src/backend/repositories/mongo_repo.py`

#### 1. `get_reviews(city_id, page, page_size)` → `tuple[list[dict], int]`
- **Difficulté** : ★★☆
- **Concepts** : `find()`, `sort()`, `skip()`, `limit()`, `count_documents()`, curseur async
- **Étapes** :
  1. `total = await self.collection.count_documents({"city_id": city_id})`
  2. `cursor = self.collection.find({"city_id": city_id}).sort("created_at", -1).skip(...).limit(...)`
  3. Itérer avec `async for doc in cursor` et convertir `_id` en `id` (str)
  4. Retourner `(docs, total)`

#### 2. `create_review(city_id, review_data)` → `dict`
- **Difficulté** : ★☆☆
- **Concepts** : `insert_one()`, ajout de champs automatiques
- **Étapes** :
  1. Ajouter `city_id` et `created_at` (datetime UTC) au document
  2. `result = await self.collection.insert_one(doc)`
  3. Convertir `result.inserted_id` en `id` (str)
  4. Retourner le document complet

#### 3. `get_average_rating(city_id)` → `float | None`
- **Difficulté** : ★★☆
- **Concept** : pipeline d'agrégation `$match` + `$group` + `$avg`
- **Pipeline** :
  ```python
  [
      {"$match": {"city_id": city_id}},
      {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}}},
  ]
  ```

### Part 2: Service Reviews (~1h30)

File: `packages/backend/src/backend/services/review_service.py`

#### 1. `get_reviews(city_id, page, page_size)` → `ReviewsResponse`
- **Difficulté** : ★☆☆
- Appeler le repo, convertir les dicts en `Review(city_id=city_id, **doc)`

#### 2. `create_review(city_id, review)` → `Review`
- **Difficulté** : ★☆☆
- Convertir `ReviewCreate` en dict (`review.model_dump()`), appeler le repo

### Testing
```bash
# Tests unitaires Sprint 3 (repo + service)
uv run pytest tests/unit/test_tp3_mongo_repo.py tests/unit/test_tp3_review_service.py -v

# Tests d'acceptation
uv run pytest tests/test_reviews.py -v

# Tout Sprint 3
uv run pytest tests/unit/test_tp3_mongo_repo.py tests/unit/test_tp3_review_service.py tests/test_reviews.py -v
```

| Test | Méthode testée | Ce qui est vérifié |
|------|---------------|-------------------|
| `TestGetReviews::test_returns_tuple_list_and_total` | `get_reviews` (repo) | Type de retour |
| `TestGetReviews::test_converts_objectid_to_str` | `get_reviews` (repo) | Conversion _id→id |
| `TestGetReviews::test_returns_correct_total` | `get_reviews` (repo) | Total correct |
| `TestGetReviews::test_filters_by_city_id` | `get_reviews` (repo) | Filtre city_id |
| `TestCreateReview::test_returns_dict_with_id` | `create_review` (repo) | Dict avec id |
| `TestCreateReview::test_adds_city_id_to_document` | `create_review` (repo) | city_id ajouté |
| `TestCreateReview::test_adds_created_at_timestamp` | `create_review` (repo) | Timestamp ajouté |
| `TestGetAverageRating::test_returns_float_when_reviews_exist` | `get_average_rating` | Float retourné |
| `TestGetAverageRating::test_returns_none_when_no_reviews` | `get_average_rating` | None si vide |
| `TestGetAverageRating::test_uses_aggregation_pipeline` | `get_average_rating` | Utilise aggregate() |
| `TestGetReviews::test_returns_reviews_response` | `get_reviews` (service) | ReviewsResponse |
| `TestCreateReview::test_returns_review_object` | `create_review` (service) | Review object |
| `TestCreateReview::test_converts_review_create_to_dict` | `create_review` (service) | model_dump() |

---

## Sprint 4: Neo4j + Recommandations

Découvrons Neo4j, une base de données graphe, et le langage Cypher. Nous allons parcourir un graphe de similarité entre villes pour construire un système de recommandations.

### Task

Implémenter les requêtes Cypher et le service de recommandation multi-repositories.

### User Stories

- "En tant qu'utilisateur, je veux découvrir des villes similaires à celle que je consulte"
- "En tant qu'utilisateur, je veux connaître les points forts d'une ville"
- "En tant que développeur, je veux orchestrer des données entre PostgreSQL et Neo4j"

### Rappel — Structure du graphe
```
(City)-[:STRONG_IN]->(Criterion)      # Points forts d'une ville
(City)-[:SIMILAR_TO {score: 0.87}]->(City)  # Similarité entre villes
```

### Part 1: Repository Neo4j (~2h)

File: `packages/backend/src/backend/repositories/neo4j_repo.py`

#### 1. `get_similar_cities(city_id, k)` → `list[dict]`
- **Difficulté** : ★★★
- **Concepts** : MATCH, relations pondérées, OPTIONAL MATCH, COLLECT, ORDER BY, LIMIT
- **Requête Cypher** :
  ```cypher
  MATCH (source:City {city_id: $city_id})-[r:SIMILAR_TO]->(target:City)
  OPTIONAL MATCH (source)-[:STRONG_IN]->(c:Criterion)<-[:STRONG_IN]-(target)
  WITH target, r.score AS similarity_score,
       COLLECT(DISTINCT c.name) AS common_strengths
  RETURN target { .city_id, .name, .department, .region,
                  .population, .overall_score } AS city,
         similarity_score, common_strengths
  ORDER BY similarity_score DESC
  LIMIT $k
  ```
- **Retour** : liste de `{"city": {...}, "similarity_score": float, "common_strengths": [str]}`

#### 2. `get_city_strengths(city_id)` → `list[str]`
- **Difficulté** : ★★☆
- **Requête Cypher** :
  ```cypher
  MATCH (c:City {city_id: $city_id})-[:STRONG_IN]->(cr:Criterion)
  RETURN cr.name AS name
  ```

### Part 2: Service Recommendations (~2h)

File: `packages/backend/src/backend/services/recommendation_service.py`

#### 1. `get_recommendations(city_id, k)` → `RecommendationsResponse | None`
- **Difficulté** : ★★★
- **Logique** :
  1. Vérifier que la ville source existe (via `postgres_repo.get_city_by_id`)
  2. Appeler `neo4j_repo.get_similar_cities(city_id, k)`
  3. Pour chaque résultat, enrichir avec les données PostgreSQL
  4. Construire les `RecommendationItem` avec `City`, `similarity_score`, `common_strengths`
  5. Retourner `RecommendationsResponse(source_city=..., recommendations=...)`

### Testing
```bash
# Tests unitaires Sprint 4 (repo + service)
uv run pytest tests/unit/test_tp4_neo4j_repo.py tests/unit/test_tp4_reco_service.py -v

# Tests d'acceptation
uv run pytest tests/test_reco.py -v

# Tout Sprint 4
uv run pytest tests/unit/test_tp4_neo4j_repo.py tests/unit/test_tp4_reco_service.py tests/test_reco.py -v
```

| Test | Méthode testée | Ce qui est vérifié |
|------|---------------|-------------------|
| `TestGetSimilarCities::test_returns_list_of_dicts` | `get_similar_cities` | Type de retour |
| `TestGetSimilarCities::test_result_contains_required_keys` | `get_similar_cities` | Clés city/score/strengths |
| `TestGetSimilarCities::test_returns_empty_list_when_no_similar` | `get_similar_cities` | Liste vide si rien |
| `TestGetSimilarCities::test_calls_session_run` | `get_similar_cities` | Requête Cypher exécutée |
| `TestGetCityStrengths::test_returns_list_of_strings` | `get_city_strengths` | Liste de strings |
| `TestGetCityStrengths::test_returns_empty_list_when_no_strengths` | `get_city_strengths` | Liste vide |
| `TestGetRecommendations::test_returns_none_when_source_city_not_found` | `get_recommendations` | None si ville absente |
| `TestGetRecommendations::test_returns_recommendations_response` | `get_recommendations` | Type correct |
| `TestGetRecommendations::test_calls_neo4j_for_similar_cities` | `get_recommendations` | Appel Neo4j |
| `TestGetRecommendations::test_recommendation_item_structure` | `get_recommendations` | Structure complète |

---

## Sprint 5: Intégration, Seed & Révision

Dernière session avant le contrôle. Nous allons assembler toutes les couches, vérifier le fonctionnement complet de l'application, et réviser les concepts clés.

### Task

Valider l'intégration de bout en bout et préparer le contrôle.

### User Stories

- "En tant que développeur, je veux vérifier que toute l'application fonctionne de bout en bout"
- "En tant qu'utilisateur, je veux naviguer dans l'application complète (API + frontend)"

### Vérification complète
```bash
# Lancer TOUS les tests (unitaires + acceptation)
uv run pytest -v

# Vérifier le style du code
just lint

# Formater si nécessaire
just fmt
```

### Checklist d'intégration
- [ ] `GET /health` → 200
- [ ] `GET /cities` → 200 avec liste de villes
- [ ] `GET /cities?search=Lyon` → résultats filtrés
- [ ] `GET /cities/1` → détails avec scores
- [ ] `GET /cities/1/scores` → scores par catégorie
- [ ] `GET /cities/1/reviews` → avis paginés
- [ ] `POST /cities/1/reviews` → création d'avis (201)
- [ ] `GET /recommendations?city_id=1` → villes similaires

### Test via Swagger UI
```bash
just dev-backend
# → http://localhost:8000/docs
```

### Test via le frontend Streamlit
```bash
just dev-frontend
# → http://localhost:8501
```

### Script de Seed (optionnel)
Fichier : `packages/backend/src/backend/scripts/seed_all.py`
```bash
just seed
```

---

## Jour 3 Soir — Contrôle

### Compétences évaluées
1. **PostgreSQL / SQL** : requêtes SELECT, filtres, jointures, pagination
2. **MongoDB** : CRUD, curseurs, pipeline d'agrégation
3. **Neo4j / Cypher** : traversée de graphe, relations pondérées
4. **Architecture** : pattern Service / Repository, conversion de données
5. **Python async** : async/await, SQLAlchemy async, Motor, Neo4j async driver

---

## Récapitulatif des commandes de test

```bash
# Sprint 1 — PostgreSQL Repository
uv run pytest tests/unit/test_tp1_postgres_repo.py -v

# Sprint 2 — City Service
uv run pytest tests/unit/test_tp2_city_service.py tests/test_cities.py -v

# Sprint 3 — MongoDB + Reviews
uv run pytest tests/unit/test_tp3_mongo_repo.py tests/unit/test_tp3_review_service.py tests/test_reviews.py -v

# Sprint 4 — Neo4j + Recommendations
uv run pytest tests/unit/test_tp4_neo4j_repo.py tests/unit/test_tp4_reco_service.py tests/test_reco.py -v

# Sprint 5 — Tout
uv run pytest -v
```

---

Remember to:
- Gérer les erreurs de manière appropriée
- Suivre les spécifications des tests
- Documenter votre code
- Utiliser les fonctionnalités propres à chaque base de données
