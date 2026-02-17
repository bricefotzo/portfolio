---
theme: default
title: SmartCity Explorer — Tech Overview
info: |
  High-level technical overview of the repository stack and tooling.
class: text-center
drawings:
  persist: false
transition: slide-left
mdc: true
---

# SmartCity Explorer
## Tech Overview

Architecture, tooling, and delivery workflow used in this repo.

---
layout: two-cols
---

# What this repo is

- **Monorepo Python** with 3 packages:
  - `backend` (FastAPI)
  - `frontend` (Streamlit)
  - `shared` (Pydantic schemas)
- Focus: city exploration + recommendations
- Multi-database architecture

::right::

```text
packages/
├─ backend/
├─ frontend/
└─ shared/
```

---

# `uv` + workspaces

- Dependency management and execution with **uv**
- Workspace declared in root `pyproject.toml`
- Unified install command:

```bash
uv sync --all-packages
```

- Run commands in package context:

```bash
uv run --package backend uvicorn backend.main:app --reload
uv run --package frontend streamlit run packages/frontend/src/frontend/app.py
```

---

# `just` command runner

The `justfile` centralizes developer workflows:

- Setup: `just install`
- Dev servers: `just dev-backend`, `just dev-frontend`
- Quality: `just fmt`, `just lint`
- Tests: `just test`, `just test-v`
- Data/bootstrap: `just seed`, `just db-up`, `just db-down`

=> one place for daily commands and teaching sessions.

---

# Code quality with Ruff

- Linting + formatting via **Ruff**
- Config is in `pyproject.toml`
- Enabled rule families: `E`, `F`, `I`, `W`
- Target Python version: `py311`

```bash
uv run ruff check .
uv run ruff format .
```

---

# GitHub Actions + Classroom

Workflow file: `.github/workflows/classroom.yml`

- Uses **GitHub Classroom autograding** actions
- Runs 4 graded steps:
  - Sprint 1 tests
  - Sprint 2 tests
  - Sprint 3 tests
  - Sprint 4 tests
- Aggregates scores with grading reporter

This gives per-sprint visibility and automated evaluation.

---

# Docker Compose for databases

`docker-compose.yml` provides local infra:

- PostgreSQL (structured city/scores)
- MongoDB (reviews)
- Neo4j (graph recommendations)

Typical flow:

```bash
docker compose up -d
docker compose ps
```

---

# Pydantic at the core

The `shared` package contains common schemas:

- API request/response validation
- Typed contracts across backend + frontend
- Cleaner service/repository boundaries

Benefit: strong typing + consistent data models across layers.

---

# Markdown-driven documentation

Project knowledge is documented in Markdown:

- `README.md` → quickstart + architecture
- `TP_SESSIONS.md` → sprint-by-sprint pedagogy
- `docs/DOCKER_DB.md` → database setup details

Good for onboarding and classroom use.

---

# Why Slidev here?

Slidev fits this repo because it is:

- **Markdown-first** (same docs culture)
- **Versionable** (slides in Git)
- **Easy to maintain** by instructors/maintainers

Run locally (without adding project deps):

```bash
npx slidev slides/tech-overview.md
```

---
layout: center
class: text-center
---

# End

Questions?
