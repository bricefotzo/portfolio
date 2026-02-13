# SmartCity Explorer

Application data-driven pour comparer les villes françaises selon des critères de qualité de vie (environnement, santé, sécurité, transports…) et recommander des villes similaires.

## Architecture

| Couche | Techno | Rôle |
|--------|--------|------|
| Frontend | Streamlit | Interface d'exploration (fourni) |
| Backend | FastAPI | API REST (à compléter) |
| PostgreSQL | asyncpg / SQLAlchemy | Villes + scores structurés |
| MongoDB | Motor | Avis utilisateurs |
| Neo4j | neo4j-driver | Graphe de similarité & recommandations |

## Démarrage rapide

```bash
# 1. Installer uv (si pas déjà fait)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Cloner et installer
git clone <repo-url> smartcity-explorer
cd smartcity-explorer
cp .env.example .env        # Remplir vos credentials DB
uv sync --all-packages

# 3. Lancer
just dev-backend   # Terminal 1 → http://localhost:8000/docs
just dev-frontend  # Terminal 2 → http://localhost:8501
```

## Structure du projet

```
smartcity-explorer/
├── packages/
│   ├── backend/          # FastAPI — squelette à compléter
│   ├── frontend/         # Streamlit — fourni complet
│   └── shared/           # Schémas Pydantic partagés
├── datasets/             # Données de référence
├── tests/                # Tests d'acceptation
├── justfile              # Commandes dev
└── .env.example          # Variables d'environnement
```

## Travail attendu (étudiants)

1. **Repositories** (`packages/backend/src/backend/repositories/`) — Implémenter les accès PostgreSQL, MongoDB et Neo4j
2. **Services** (`packages/backend/src/backend/services/`) — Orchestrer la logique métier
3. **Vérifier** que tous les tests passent (`just test`)

## Endpoints API

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/health` | Health check |
| GET | `/cities` | Recherche + filtres + tri + pagination |
| GET | `/cities/{city_id}` | Détails d'une ville |
| GET | `/cities/{city_id}/scores` | Scores qualité de vie |
| GET | `/cities/{city_id}/reviews` | Avis utilisateurs |
| POST | `/cities/{city_id}/reviews` | Ajouter un avis |
| GET | `/recommendations` | Villes similaires (Neo4j) |

## Commandes utiles

```bash
just install       # Installer toutes les dépendances
just dev-backend   # Lancer le backend (port 8000)
just dev-frontend  # Lancer le frontend (port 8501)
just test          # Lancer les tests
just fmt           # Formater le code
just lint          # Vérifier le style
```
