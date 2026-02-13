"""Page 3 — Recommandations de villes similaires (Neo4j)."""

from __future__ import annotations

import streamlit as st

from frontend import api_client
from frontend.components.charts import bar_chart
from frontend.state import get_selected_city, init_state, select_city

st.set_page_config(page_title="Recommandations — SmartCity", page_icon="🤝", layout="wide")
init_state()

st.title("🤝 Recommandations")

# ── Récupérer la ville sélectionnée ───────────────────────────
city_id, city_name = get_selected_city()

if city_id is None:
    st.warning("Aucune ville sélectionnée.")
    st.info("Rendez-vous sur la page **Explorer** pour choisir une ville.")
    if st.button("🔍 Aller à Explorer"):
        st.switch_page("frontend/pages/1_Search.py")
    st.stop()

st.markdown(f"Villes similaires à **{city_name}**")

# ── Paramètres ─────────────────────────────────────────────────
k = st.sidebar.slider("Nombre de recommandations", min_value=1, max_value=20, value=5)

# ── Appel API ──────────────────────────────────────────────────
try:
    data = api_client.get_recommendations(city_id, k=k)
except Exception as e:
    st.error(f"Erreur API : {e}")
    st.stop()

if not data:
    st.error("Ville non trouvée.")
    st.stop()

recommendations = data.get("recommendations", [])

if not recommendations:
    st.info(
        "Aucune recommandation disponible. "
        "Le graphe Neo4j doit être peuplé avec les relations SIMILAR_TO et STRONG_IN."
    )
    st.stop()

# ── Affichage des recommandations ──────────────────────────────
for i, reco in enumerate(recommendations):
    city = reco.get("city", {})
    similarity = reco.get("similarity_score", 0)
    strengths = reco.get("common_strengths", [])

    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.markdown(
                f"### {i + 1}. {city.get('name', '?')} "
                f"({city.get('department', '')})"
            )
            st.markdown(
                f"**Région** : {city.get('region', '—')} | "
                f"**Population** : {city.get('population', 0):,}".replace(",", " ")
            )

        with col2:
            st.metric("Similarité", f"{similarity:.0%}")

        with col3:
            st.metric("Score global", f"{city.get('overall_score', 0):.1f}/10")

        # Forces communes
        if strengths:
            st.markdown(
                "**Forces communes** : " + " ".join(f"`{s}`" for s in strengths)
            )

        # Bouton détails
        if st.button(f"📊 Détails de {city.get('name', '?')}", key=f"reco_{i}"):
            select_city(city.get("id", 0), city.get("name", ""))
            st.switch_page("frontend/pages/2_City_Details.py")

        st.markdown("---")

# ── Navigation ─────────────────────────────────────────────────
if st.button("🔍 Retour à l'exploration"):
    st.switch_page("frontend/pages/1_Search.py")
if st.button("📊 Retour aux détails"):
    st.switch_page("frontend/pages/2_City_Details.py")
