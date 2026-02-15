"""Page d'accueil SmartCity Explorer."""
import streamlit as st

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🔍 Explorer")
    st.markdown(
        "Recherchez et filtrez les villes par région, "
        "département, population et critères de qualité de vie."
    )

with col2:
    st.markdown("### 📊 Comparer")
    st.markdown(
        "Visualisez les scores détaillés de chaque ville "
        "avec des graphiques radar et barres interactifs."
    )

with col3:
    st.markdown("### 🤝 Recommander")
    st.markdown(
        "Découvrez des villes similaires grâce au graphe "
        "de relations Neo4j et aux critères communs."
    )

st.markdown("---")
st.markdown(
    "**Projet pédagogique** — "
    "Architecture polyglotte : PostgreSQL + MongoDB + Neo4j | "
    "Backend FastAPI | Frontend Streamlit"
)