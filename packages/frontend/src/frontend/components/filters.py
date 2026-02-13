"""Composants de filtres pour la sidebar."""

from __future__ import annotations

import streamlit as st

# Régions françaises métropolitaines
REGIONS = [
    "Auvergne-Rhône-Alpes",
    "Bourgogne-Franche-Comté",
    "Bretagne",
    "Centre-Val de Loire",
    "Corse",
    "Grand Est",
    "Hauts-de-France",
    "Île-de-France",
    "Normandie",
    "Nouvelle-Aquitaine",
    "Occitanie",
    "Pays de la Loire",
    "Provence-Alpes-Côte d'Azur",
]

SORT_OPTIONS = {
    "Score global (desc)": ("overall_score", "desc"),
    "Score global (asc)": ("overall_score", "asc"),
    "Nom (A→Z)": ("name", "asc"),
    "Nom (Z→A)": ("name", "desc"),
    "Population (desc)": ("population", "desc"),
    "Population (asc)": ("population", "asc"),
}


def render_search_filters() -> dict:
    """Affiche les filtres dans la sidebar et retourne les valeurs."""
    st.sidebar.header("Filtres")

    search = st.sidebar.text_input(
        "Rechercher une ville",
        value=st.session_state.get("search_query", ""),
        placeholder="Ex: Lyon, Bordeaux…",
    )

    region = st.sidebar.selectbox(
        "Région",
        options=["Toutes"] + REGIONS,
        index=0,
    )

    department = st.sidebar.text_input(
        "Département",
        placeholder="Ex: Rhône, Gironde…",
    )

    min_population = st.sidebar.slider(
        "Population minimum",
        min_value=0,
        max_value=500_000,
        value=0,
        step=10_000,
        format="%d",
    )

    sort_label = st.sidebar.selectbox(
        "Trier par",
        options=list(SORT_OPTIONS.keys()),
        index=0,
    )
    sort_by, sort_order = SORT_OPTIONS[sort_label]

    return {
        "search": search if search else None,
        "region": region if region != "Toutes" else None,
        "department": department if department else None,
        "min_population": min_population if min_population > 0 else None,
        "sort_by": sort_by,
        "sort_order": sort_order,
    }
