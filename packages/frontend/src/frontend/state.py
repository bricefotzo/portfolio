"""Gestion de l'état Streamlit (session_state helpers)."""

from __future__ import annotations

import streamlit as st


def init_state():
    """Initialise les clés de session par défaut."""
    defaults = {
        "selected_city_id": None,
        "selected_city_name": None,
        "search_query": "",
        "region_filter": None,
        "department_filter": None,
        "sort_by": "overall_score",
        "page": 1,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def select_city(city_id: int, city_name: str):
    """Sélectionne une ville pour la page détails."""
    st.session_state.selected_city_id = city_id
    st.session_state.selected_city_name = city_name


def get_selected_city() -> tuple[int | None, str | None]:
    """Retourne (city_id, city_name) sélectionnés."""
    return st.session_state.get("selected_city_id"), st.session_state.get("selected_city_name")
