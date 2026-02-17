# Démarrer les bases de données avec Docker Compose

Ce document explique comment lancer **PostgreSQL**, **MongoDB** et **Neo4j** en local avec Docker Compose pour le projet SmartCity Explorer.

## Prérequis

- [Docker](https://docs.docker.com/get-docker/) et [Docker Compose](https://docs.docker.com/compose/install/) installés sur votre machine.

## Démarrer toutes les bases

À la racine du projet :

```bash
docker compose up -d
```

- `-d` lance les conteneurs en arrière-plan (détaché).
- Les trois services (`postgres`, `mongo`, `neo4j`) démarrent et restent actifs jusqu’à un `docker compose down`.

## Vérifier que les services sont prêts

Les conteneurs ont des **healthchecks**. Pour voir l’état :

```bash
docker compose ps
```

Quand tous les services sont `healthy`, vous pouvez lancer le backend et le seed.

## Ports et accès

| Service   | Port(s)        | Usage                          |
|----------|----------------|---------------------------------|
| PostgreSQL | **5432**     | Connexion app (asyncpg)         |
| MongoDB    | **27017**    | Connexion app (Motor)          |
| Neo4j      | **7474** (HTTP), **7687** (Bolt) | 7474 = Browser UI, 7687 = driver |

- **Neo4j Browser** : http://localhost:7474 (connexion avec user/mot de passe du `.env`).

## Variables d’environnement

Le fichier `docker-compose.yml` utilise des variables avec valeurs par défaut. Pour les surcharger, créez un fichier `.env` à la racine (par exemple en copiant `.env.example`) :

```bash
cp .env.example .env
```

Variables utiles pour Docker Compose (noms utilisés dans `docker-compose.yml`) :

| Variable          | Défaut     | Rôle                          |
|-------------------|------------|-------------------------------|
| `POSTGRES_USER`   | smartcity  | Utilisateur PostgreSQL        |
| `POSTGRES_PASSWORD` | smartcity | Mot de passe PostgreSQL    |
| `POSTGRES_DB`     | smartcity  | Nom de la base PostgreSQL    |
| `MONGO_USER` / `MONGO_PASSWORD` / `MONGO_DB` | smartcity | MongoDB |
| `NEO4J_USER`      | neo4j      | Utilisateur Neo4j             |
| `NEO4J_PASSWORD`   | smartcity  | Mot de passe Neo4j            |

L’**application backend** lit sa propre config (par ex. `POSTGRES_URL`, `MONGO_URL`, `NEO4J_URI`, etc.) dans le même `.env`. Assurez-vous que les URLs dans `.env` correspondent aux identifiants et ports utilisés par Docker (voir `.env.example`).

## Arrêter les bases

```bash
docker compose down
```

Pour supprimer aussi les **volumes** (données persistantes) :

```bash
docker compose down -v
```

## Ordre recommandé pour le TP

1. **Démarrer les bases** : `docker compose up -d`
2. **Vérifier** : `docker compose ps` (tous `healthy`)
3. **Configurer** : `.env` avec les bonnes URLs (voir `.env.example`)
4. **Implémenter les connexions DB** (fichiers dans `backend/db/`)
5. **Lancer le seed** : `just seed` ou `python -m backend.scripts.seed_all`
6. **Lancer le backend** : `just dev-backend` et tester l’API

Voir **TP_SESSIONS.md** pour le détail des sprints (DB → seed → repos) et des tests.
