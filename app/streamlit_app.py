import streamlit as st

st.set_page_config(
    page_title="Retail Analytics",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.data_loader import sidebar_filters

df, _ = sidebar_filters()

if df is not None:
    st.title("Bienvenue sur Retail Analytics")

    st.markdown("""
    <div style='background-color: white; padding: 25px; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 20px;'>
        <h3 style='color: #4F46E5; margin-top:0;'>Assistant de Pilotage CRM</h3>
        <p style='color: #475569; font-size: 1.1rem;'>
            Cette application permet à notre équipe marketing de diagnostiquer la rétention, segmenter la base client 
            et simuler l'impact financier de nos campagnes.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### Ce qu'on peut faire
        - **Diagnostiquer** : Analyser la santé de nos cohortes clients
        - **Segmenter** : Identifier nos VIPs et clients à risque via RFM
        - **Simuler** : Projeter l'impact d'une remise ou hausse de rétention sur la CLV
        - **Agir** : Exporter les listes de clients pour nos campagnes d'emailing
        """)
    
    with col2:
        st.markdown("""
        ### Méthodologie utilisée
        - **RFM** : Récence, Fréquence, Montant avec score de 1 à 4
        - **CLV** : Customer Lifetime Value estimée
        - **Cohortes** : Suivi du comportement de rachat mois par mois
        """)

    st.markdown("---")
    st.info("Utilisez le menu latéral pour filtrer les données et naviguer entre les vues.")

    # stats rapides
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Transactions", f"{len(df):,}")
    c2.metric("Clients Uniques", f"{df['Customer ID'].nunique():,}")
    c3.metric("Pays Couverts", f"{df['Country'].nunique()}")
    c4.metric("Produits", f"{df['Description'].nunique():,}")
else:
    st.warning("Veuillez charger les données via la sidebar.")