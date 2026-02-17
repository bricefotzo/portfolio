"""Connexion PostgreSQL via SQLAlchemy async."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.core.config import get_settings

_engine = None
_session_factory = None


def get_engine():
    """Crée le moteur SQLAlchemy async (singleton). À compléter : créer l'engine depuis settings.postgres_url."""
    global _engine
    if _engine is None:
        # TODO: Créer l'engine async avec create_async_engine(settings.postgres_url, echo=settings.debug)
        # ✂️ SOLUTION START
        settings = get_settings()
        _engine = create_async_engine(settings.postgres_url, echo=settings.debug)
        # ✂️ SOLUTION END
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Crée la factory de sessions async (singleton). À compléter : sessionmaker avec get_engine()."""
    global _session_factory
    if _session_factory is None:
        # TODO: Créer la session factory avec async_sessionmaker(get_engine(), expire_on_commit=False)
        # ✂️ SOLUTION START
        _session_factory = async_sessionmaker(get_engine(), expire_on_commit=False)
        # ✂️ SOLUTION END
    return _session_factory


async def get_db() -> AsyncSession:  # type: ignore[misc]
    """Dependency FastAPI — fournit une session DB."""
    factory = get_session_factory()
    async with factory() as session:
        yield session
