import streamlit as st
import sys
import os

from utils.visualization import load_css
from utils.data_loader import sidebar_filters
from utils.rfm_calculator import compute_rfm

load_css()
df, analysis_date = sidebar_filters()

if df is not None:
    st.title("Exports CRM")
    rfm_df = compute_rfm(df, analysis_date)

    target_segs = st.multiselect("Cibler segments", rfm_df['Segment_Label'].unique(),
                                 default=['Champions 🏆', 'À Risque ⚠️'])

    if target_segs:
        export = rfm_df[rfm_df['Segment_Label'].isin(target_segs)].copy()
        st.write(f"Prévisualisation ({len(export)} clients) :")

        # CORRECTION ICI : width="stretch"
        st.dataframe(export.head(10), width="stretch")

        st.download_button("📥 Télécharger CSV", export.to_csv(index=False).encode('utf-8'), f"CRM_Export.csv",
                           "text/csv")
    else:
        st.info("Sélectionnez un segment pour activer l'export.")