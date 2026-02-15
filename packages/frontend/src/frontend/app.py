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

pg = st.navigation(pages=[
        st.Page("pages/0_Home.py", title="Accueil", icon="🏠"),  # ← Changed
        st.Page("pages/1_Search.py", title="Explorer les villes", icon="🔍"),
        st.Page("pages/2_City_Details.py", title="Détails ville", icon="📊"),
        st.Page("pages/3_Recommendations.py", title="Recommandations", icon="🤝")
    ],
    position="top",
)

pg.run()

# Remove everything after pg.run() — the home content now lives in 0_Home.py
