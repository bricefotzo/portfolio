"""Tests unitaires — Script de seed (Sprint 2).

Vérifier que le module seed est importable et expose les fonctions à implémenter.

Commande :
    uv run pytest tests/unit/test_seed.py -v
    uv run pytest -m sprint2 -v
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.sprint2


def test_seed_module_importable():
    """Le module backend.scripts.seed_all doit être importable."""
    import backend.scripts.seed_all as seed_module

    assert seed_module is not None


def test_seed_functions_exist():
    """Les fonctions seed_postgres, seed_mongo, seed_neo4j doivent exister et être callables."""
    import backend.scripts.seed_all as seed_module

    assert hasattr(seed_module, "seed_postgres")
    assert hasattr(seed_module, "seed_mongo")
    assert hasattr(seed_module, "seed_neo4j")
    assert callable(seed_module.seed_postgres)
    assert callable(seed_module.seed_mongo)
    assert callable(seed_module.seed_neo4j)


def test_main_exists():
    """La fonction main doit exister pour asyncio.run(main())."""
    import backend.scripts.seed_all as seed_module

    assert hasattr(seed_module, "main")
    assert callable(seed_module.main)
