set dotenv-load := true

# ── Installation ───────────────────────────────────────────────
install:
    uv sync --all-packages

# ── Développement ──────────────────────────────────────────────
dev-backend:
    uv run --package backend uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
    uv run --package frontend streamlit run packages/frontend/src/frontend/app.py --server.port 8501

# Lance les deux (ouvrir 2 terminaux recommandé)
dev:
    @echo "→ Terminal 1 : just dev-backend"
    @echo "→ Terminal 2 : just dev-frontend"

# ── Qualité ────────────────────────────────────────────────────
fmt:
    uv run ruff format .

lint:
    uv run ruff check .

lint-fix:
    uv run ruff check --fix .

# ── Tests ──────────────────────────────────────────────────────
test:
    uv run pytest -q

test-v:
    uv run pytest -v

# ── Seed (optionnel) ──────────────────────────────────────────
seed:
    uv run --package backend python -m backend.scripts.seed_all

# ── Clean ──────────────────────────────────────────────────────
clean:
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
