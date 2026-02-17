"""Connexion MongoDB via Motor (async)."""

from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from backend.core.config import get_settings

_client: AsyncIOMotorClient | None = None


def get_mongo_db() -> AsyncIOMotorDatabase:
    """Retourne la base MongoDB (singleton). À compléter : créer le client Motor avec settings.mongo_url, retourner client[settings.mongo_db]."""
    global _client
    if _client is None:
        # TODO: Créer le client Motor avec AsyncIOMotorClient(settings.mongo_url), puis retourner client[settings.mongo_db]
        # ✂️ SOLUTION START
        settings = get_settings()
        _client = AsyncIOMotorClient(settings.mongo_url)
        # ✂️ SOLUTION END
    return _client[get_settings().mongo_db]
