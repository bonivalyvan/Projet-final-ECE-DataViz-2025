import streamlit as st
from utils.visualization import load_css
from utils.data_loader import sidebar_filters

# Configuration Globale
st.set_page_config(page_title="Retail Analytics", page_icon="🛍️", layout="wide")
load_css()

# Sidebar (juste pour l'info ici, car les filtres sont globaux mais appliqués par page)
# Dans la page d'accueil, on peut soit masquer les filtres, soit les afficher.
# Pour simplifier la navigation, on affiche l'intro.

st.title("Bienvenue sur Retail Analytics")

st.markdown(f"""
<div style='background-color: white; padding: 25px; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 20px;'>
    <h3 style='color: #4F46E5; margin-top:0;'>👋 Votre assistant de pilotage CRM</h3>
    <p style='color: #475569; font-size: 1.1rem;'>
        Cette application modulaire permet à l'équipe marketing de diagnostiquer la rétention, segmenter la base client et simuler l'impact financier de vos campagnes.
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    ### 🚀 Ce que vous pouvez faire
    - **KPIs** : Vue d'ensemble de la performance.
    - **Diagnostiquer** : Analysez la santé de vos cohortes.
    - **Segmenter** : Identifiez vos VIPs et clients à risque.
    - **Simuler** : Projetez l'impact financier.
    - **Agir** : Exportez les données.
    """)

with col2:
    st.markdown("""
    ### 🧠 Méthodologie
    - **RFM** : Récence, Fréquence, Montant.
    - **Cohortes** : Analyse comportementale temporelle.
    - **CLV** : Valeur vie client (Customer Lifetime Value).
    """)

st.info("👈 **Utilisez le menu latéral** pour naviguer entre les différentes pages d'analyse.")