"""Utilitaires partagés."""

from __future__ import annotations


def clamp(value: float, min_val: float = 0.0, max_val: float = 10.0) -> float:
    """Borne une valeur entre min_val et max_val."""
    return max(min_val, min(max_val, value))


def round_score(value: float, decimals: int = 1) -> float:
    """Arrondit un score."""
    return round(value, decimals)
