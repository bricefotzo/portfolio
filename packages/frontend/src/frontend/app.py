"""SmartCity Explorer — Application Streamlit principale."""

from __future__ import annotations

import streamlit as st

from frontend import api_client
from frontend.state import init_state

# ── Configuration de la page ───────────────────────────────────
st.set_page_config(
    page_title="SmartCity Explorer",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_state()

# ── Header ─────────────────────────────────────────────────────
st.title("🏙️ SmartCity Explorer")
st.markdown(
    "Explorez et comparez les villes françaises selon leurs critères "
    "de qualité de vie : environnement, santé, sécurité, transports…"
)

# ── Health check ───────────────────────────────────────────────
health = api_client.check_health()
if health.get("status") == "ok":
    st.sidebar.success(f"API connectée (v{health.get('version', '?')})")
else:
    st.sidebar.error("API non disponible — vérifiez que le backend est lancé")
    st.info(
        "**Pour démarrer :**\n"
        "```bash\n"
        "just dev-backend   # Terminal 1\n"
        "just dev-frontend  # Terminal 2\n"
        "```"
    )

# ── Navigation ─────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.markdown("### Navigation")
# st.sidebar.page_link("frontend/app.py", label="Accueil", icon="🏠")
# st.sidebar.page_link("packages/frontend/src/frontend/pages/1_Search.py", label="Explorer les villes", icon="🔍")
# st.sidebar.page_link("frontend/pages/2_City_Details.py", label="Détails ville", icon="📊")
# st.sidebar.page_link("frontend/pages/3_Recommendations.py", label="Recommandations", icon="🤝")

# ── Contenu accueil ────────────────────────────────────────────
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
