"""Composants graphiques réutilisables."""

from __future__ import annotations

import plotly.graph_objects as go


def radar_chart(scores: list[dict], city_name: str = "Ville") -> go.Figure:
    """Crée un radar chart des scores qualité de vie.

    Args:
        scores: Liste de dicts {"category": str, "score": float, "label": str}
        city_name: Nom de la ville pour le titre
    """
    if not scores:
        fig = go.Figure()
        fig.add_annotation(text="Aucun score disponible", showarrow=False)
        return fig

    categories = [s.get("label", s.get("category", "")) for s in scores]
    values = [s.get("score", 0) for s in scores]

    # Fermer le polygone
    categories = categories + [categories[0]]
    values = values + [values[0]]

    fig = go.Figure(
        data=go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            name=city_name,
            line_color="#636EFA",
            fillcolor="rgba(99, 110, 250, 0.25)",
        )
    )
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10]),
        ),
        showlegend=False,
        title=f"Profil qualité de vie — {city_name}",
        margin=dict(l=60, r=60, t=60, b=40),
    )
    return fig


def bar_chart(scores: list[dict], city_name: str = "Ville") -> go.Figure:
    """Crée un bar chart horizontal des scores."""
    if not scores:
        fig = go.Figure()
        fig.add_annotation(text="Aucun score disponible", showarrow=False)
        return fig

    labels = [s.get("label", s.get("category", "")) for s in scores]
    values = [s.get("score", 0) for s in scores]

    # Couleurs selon le score
    colors = []
    for v in values:
        if v >= 7:
            colors.append("#2ecc71")
        elif v >= 5:
            colors.append("#f39c12")
        else:
            colors.append("#e74c3c")

    fig = go.Figure(
        data=go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker_color=colors,
            text=[f"{v:.1f}" for v in values],
            textposition="auto",
        )
    )
    fig.update_layout(
        xaxis=dict(range=[0, 10], title="Score"),
        yaxis=dict(autorange="reversed"),
        title=f"Scores — {city_name}",
        margin=dict(l=120, r=20, t=50, b=40),
        height=max(300, len(scores) * 40 + 100),
    )
    return fig


def stars(rating: int, max_stars: int = 5) -> str:
    """Retourne une représentation texte d'une note en étoiles."""
    return "★" * rating + "☆" * (max_stars - rating)
