"""Page 1 — Recherche et exploration de villes."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from frontend import api_client
from frontend.components.filters import render_search_filters
from frontend.state import init_state, select_city

st.set_page_config(page_title="Explorer — SmartCity", page_icon="🔍", layout="wide")
init_state()

st.title("🔍 Explorer les villes")

# ── Filtres (sidebar) ─────────────────────────────────────────
filters = render_search_filters()

# ── Pagination ─────────────────────────────────────────────────
page = st.session_state.get("page", 1)
page_size = 20

# ── Appel API ──────────────────────────────────────────────────
try:
    data = api_client.search_cities(
        search=filters["search"],
        region=filters["region"],
        department=filters["department"],
        min_population=filters["min_population"],
        sort_by=filters["sort_by"],
        sort_order=filters["sort_order"],
        page=page,
        page_size=page_size,
    )
except Exception as e:
    st.error(f"Erreur lors de l'appel API : {e}")
    st.stop()

cities = data.get("cities", [])
total = data.get("total", 0)

# ── Résultats ──────────────────────────────────────────────────
if not cities:
    st.info("Aucune ville trouvée. Ajustez vos filtres ou vérifiez le backend.")
    st.stop()

st.markdown(f"**{total} ville(s) trouvée(s)** — Page {page}")

# Tableau de résultats
df = pd.DataFrame(cities)
if not df.empty:
    display_cols = ["name", "department", "region", "population", "overall_score"]
    available_cols = [c for c in display_cols if c in df.columns]
    df_display = df[available_cols].copy()
    df_display.columns = ["Ville", "Département", "Région", "Population", "Score global"][
        : len(available_cols)
    ]

    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
    )

# ── Sélection d'une ville ─────────────────────────────────────
st.markdown("### Sélectionner une ville")

city_options = {f"{c['name']} ({c.get('department', '')})": c for c in cities}
selected_label = st.selectbox("Choisissez une ville :", options=list(city_options.keys()))

if selected_label:
    selected = city_options[selected_label]
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Voir les détails", use_container_width=True):
            select_city(selected["id"], selected["name"])
            st.switch_page("frontend/pages/2_City_Details.py")
    with col2:
        if st.button("🤝 Recommandations", use_container_width=True):
            select_city(selected["id"], selected["name"])
            st.switch_page("frontend/pages/3_Recommendations.py")

# ── Pagination ─────────────────────────────────────────────────
total_pages = max(1, (total + page_size - 1) // page_size)

st.markdown("---")
pcol1, pcol2, pcol3 = st.columns([1, 2, 1])
with pcol1:
    if page > 1 and st.button("← Précédent"):
        st.session_state.page = page - 1
        st.rerun()
with pcol2:
    st.markdown(f"<center>Page {page} / {total_pages}</center>", unsafe_allow_html=True)
with pcol3:
    if page < total_pages and st.button("Suivant →"):
        st.session_state.page = page + 1
        st.rerun()
