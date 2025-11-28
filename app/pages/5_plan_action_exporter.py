import streamlit as st

st.set_page_config(
    page_title="Plan d'action",
    page_icon="download",
    layout="wide"
)
import sys
import os
import pandas as pd

from utils.visualization import load_css
from utils.data_loader import sidebar_filters
from utils.rfm_calculator import compute_rfm

load_css()
df, analysis_date = sidebar_filters()

if df is not None:
    st.title("Exports CRM et Listes Activables")
    rfm_df = compute_rfm(df, analysis_date)
    
    st.markdown("""
    Cette page permet d'exporter les données filtrées pour passer à l'action dans vos outils CRM ou d'emailing.
    """)
    
    # selection des segments
    st.subheader("Sélectionner les segments à cibler")
    target_segs = st.multiselect(
        "Segments Cibles", 
        rfm_df['Segment_Label'].unique(), 
        default=['Champions', 'At Risk'],
        help="Sélectionner les segments pour lesquels vous souhaitez exporter la liste de clients"
    )
    
    if target_segs:
        export = rfm_df[rfm_df['Segment_Label'].isin(target_segs)].copy()
        
        # statistiques de l export - ajout pour donner un apercu
        c1, c2, c3 = st.columns(3)
        c1.metric("Clients à contacter", f"{len(export):,}")
        c2.metric("CA Potentiel", f"{export['Monetary'].sum():,.0f} €")
        c3.metric("Panier Moyen", f"{export['Monetary'].mean():.1f} €")
        
        # bouton de telechargement
        csv_data = export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Télécharger la liste CSV",
            data=csv_data,
            file_name=f"crm_export_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        # previsualisation
        st.markdown("###")
        st.subheader(f"Prévisualisation : {len(export)} clients")
        st.dataframe(export.head(20), use_container_width=True)
        
        # conseils utilisation - ajout pour guider l utilisateur
        st.markdown("---")
        st.markdown("""
        ### Comment utiliser cette liste
        
        1. Télécharger le CSV et l'importer dans votre outil d'emailing (Mailchimp, Sendgrid, etc.)
        2. Segmenter vos messages :
           - **Champions** : "Merci pour votre fidélité, voici un accès anticipé à nos nouveautés"
           - **À Risque** : "On s'ennuie de vous, revenez avec -15% sur votre prochain achat"
           - **Hibernants** : "Dernière chance -20% ou nous supprimons votre compte"
        3. Mesurer le ROI : Taux d'ouverture, Taux de conversion, CA généré
        """)
        
    else:
        st.info("Sélectionnez au moins un segment pour exporter.")