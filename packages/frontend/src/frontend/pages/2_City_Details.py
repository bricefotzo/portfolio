"""Page 2 — Détails d'une ville (scores + avis)."""

from __future__ import annotations

import streamlit as st

from frontend import api_client
from frontend.components.charts import bar_chart, radar_chart, stars
from frontend.state import get_selected_city, init_state, select_city

st.set_page_config(page_title="Détails — SmartCity", page_icon="📊", layout="wide")
init_state()

st.title("📊 Détails d'une ville")

# ── Récupérer la ville sélectionnée ───────────────────────────
city_id, city_name = get_selected_city()

if city_id is None:
    st.warning("Aucune ville sélectionnée.")
    st.info("Rendez-vous sur la page **Explorer** pour choisir une ville.")
    if st.button("🔍 Aller à Explorer"):
        st.switch_page("pages/1_Search.py")
    st.stop()

# ── Chargement des données ─────────────────────────────────────
try:
    city_data = api_client.get_city(city_id)
    scores_data = api_client.get_city_scores(city_id)
except Exception as e:
    st.error(f"Erreur API : {e}")
    st.stop()

if not city_data:
    st.error(f"Ville {city_id} non trouvée.")
    st.stop()

# ── En-tête ────────────────────────────────────────────────────
st.markdown(f"## {city_data.get('name', 'Ville inconnue')}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Région", city_data.get("region", "—"))
col2.metric("Département", city_data.get("department", "—"))
col3.metric("Population", f"{city_data.get('population', 0):,}".replace(",", " "))
col4.metric("Score global", f"{city_data.get('overall_score', 0):.1f}/10")

if city_data.get("description"):
    st.markdown(city_data["description"])

# ── Graphiques des scores ──────────────────────────────────────
st.markdown("---")
st.markdown("### Scores qualité de vie")

scores = scores_data.get("scores", city_data.get("scores", []))

if scores:
    tab_radar, tab_bar = st.tabs(["Radar", "Barres"])
    with tab_radar:
        fig_radar = radar_chart(scores, city_data.get("name", ""))
        st.plotly_chart(fig_radar, use_container_width=True)
    with tab_bar:
        fig_bar = bar_chart(scores, city_data.get("name", ""))
        st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("Aucun score disponible pour cette ville.")

# ── Avis utilisateurs ─────────────────────────────────────────
st.markdown("---")
st.markdown("### Avis utilisateurs")

try:
    reviews_data = api_client.get_reviews(city_id)
except Exception:
    reviews_data = {"reviews": [], "total": 0}

reviews = reviews_data.get("reviews", [])
total_reviews = reviews_data.get("total", 0)

if reviews:
    st.markdown(f"**{total_reviews} avis**")
    for review in reviews:
        with st.container():
            rcol1, rcol2 = st.columns([3, 1])
            with rcol1:
                author = review.get("author", "Anonyme")
                rating = review.get("rating", 0)
                st.markdown(f"**{author}** — {stars(rating)}")
            with rcol2:
                tags = review.get("tags", [])
                if tags:
                    st.markdown(" ".join(f"`{t}`" for t in tags))
            comment = review.get("comment", "")
            if comment:
                st.markdown(f"> {comment}")
            st.markdown("---")
else:
    st.info("Aucun avis pour cette ville.")

# ── Formulaire nouvel avis ─────────────────────────────────────
st.markdown("### Laisser un avis")

with st.form("review_form"):
    author = st.text_input("Votre nom", value="Anonyme", max_chars=100)
    rating = st.slider("Note", min_value=1, max_value=5, value=3)
    comment = st.text_area("Commentaire", max_chars=2000, placeholder="Votre avis sur cette ville…")
    tags_input = st.text_input("Tags (séparés par des virgules)", placeholder="transport, culture, calme")
    submitted = st.form_submit_button("Envoyer")

    if submitted:
        tags = [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else []
        try:
            result = api_client.create_review(city_id, author, rating, comment, tags)
            if result:
                st.success("Avis envoyé !")
                st.rerun()
            else:
                st.error("Erreur lors de l'envoi.")
        except Exception as e:
            st.error(f"Erreur : {e}")

# ── Navigation ─────────────────────────────────────────────────
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("🔍 Retour à l'exploration"):
        st.switch_page("pages/1_Search.py")
with col2:
    if st.button("🤝 Voir les recommandations"):
        st.switch_page("pages/3_Recommendations.py")
