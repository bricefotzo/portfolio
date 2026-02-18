---
theme: default
title: Cloud Database Setup — Neon · Aura · Atlas
info: |
  Step-by-step account creation for the three free-tier cloud databases.
class: text-center
drawings:
  persist: false
transition: slide-left
mdc: true
---

# Cloud Database Setup

Free-tier accounts for **Neon**, **Aura**, and **Atlas**

---

# Overview

| Database | Provider | Free tier |
|----------|----------|-----------|
| PostgreSQL | Neon | 0.5 GB storage, 1 project |
| Neo4j | AuraDB | 200k nodes, 1 instance |
| MongoDB | Atlas | 512 MB storage, shared cluster |

All three require **no credit card** for the free tier.

---
layout: two-cols
---

# Neon (PostgreSQL)

1. Go to **neon.tech** → Sign Up
2. Auth via GitHub / Google / email
3. Create a **Project** (choose region)
4. Neon auto-creates a default database
5. Copy the connection string from the dashboard

::right::

```ini
# .env
POSTGRES_URL="postgresql://user:pass@\
ep-xxx.region.aws.neon.tech/dbname\
?sslmode=require"
```

> Keep `?sslmode=require` — Neon enforces TLS.

---
layout: two-cols
---

# Aura (Neo4j)

1. Go to **neo4j.com/cloud/aura** → Start Free
2. Sign up with email or Google
3. Create a **Free instance** (AuraDB Free)
4. **Save the generated password** — shown once
5. Wait ~2 min for provisioning

::right::

```ini
# .env
NEO4J_URI="neo4j+s://xxxxxxxx.databases.neo4j.io"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="your-saved-password"
```

> URI scheme is `neo4j+s://` (TLS included).

---
layout: two-cols
---

# Atlas (MongoDB)

1. Go to **mongodb.com/atlas** → Try Free
2. Sign up → choose **M0 Free** cluster
3. Pick a cloud provider + region
4. Create a **DB user** (username + password)
5. Add your IP to the **IP Access List** (`0.0.0.0/0` for dev)
6. Click **Connect** → get the URI

::right::

```ini
# .env
MONGODB_URL="mongodb+srv://user:pass@\
cluster0.xxxxx.mongodb.net/\
?retryWrites=true&w=majority"
MONGODB_DB="smartcity"
```

> Replace `user`, `pass`, and the cluster hostname.

---

# Local `.env` — Full Template

```ini
# PostgreSQL — Neon
POSTGRES_URL="postgresql://user:pass@ep-xxx.region.aws.neon.tech/dbname?sslmode=require"

# Neo4j — AuraDB
NEO4J_URI="neo4j+s://xxxxxxxx.databases.neo4j.io"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="your-aura-password"

# MongoDB — Atlas
MONGODB_URL="mongodb+srv://user:pass@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority"
MONGODB_DB="smartcity"
```

> `.env` is git-ignored — never commit credentials.

---

# Verify Connections

```bash
# PostgreSQL
uv run python -c "
import psycopg, os
conn = psycopg.connect(os.environ['POSTGRES_URL'])
print('PG ok', conn.info.server_version); conn.close()"

# Neo4j
uv run python -c "
from neo4j import GraphDatabase; import os
d = GraphDatabase.driver(os.environ['NEO4J_URI'],
      auth=(os.environ['NEO4J_USER'], os.environ['NEO4J_PASSWORD']))
d.verify_connectivity(); print('Neo4j ok'); d.close()"

# MongoDB
uv run python -c "
from pymongo import MongoClient; import os
c = MongoClient(os.environ['MONGODB_URL'])
print('Mongo ok', c.server_info()['version'])"
```

---
layout: center
class: text-center
---

# Done

All three databases connected locally.
Run slides: `npx slidev slides/cloud-db-setup.md`
