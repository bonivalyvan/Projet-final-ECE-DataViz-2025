import streamlit as st
import sys
import os
import plotly.express as px

from utils.visualization import load_css, style_plot
from utils.data_loader import sidebar_filters
from utils.rfm_calculator import compute_rfm

load_css()
df, analysis_date = sidebar_filters()

if df is not None:
    st.title("Segmentation & Priorisation")
    rfm_df = compute_rfm(df, analysis_date)

    with st.expander("📘 Guide des Segments", expanded=False):
        st.markdown("""
        - **🏆 Champions** : Acheté récemment, souvent et pour cher.
        - **⚠️ À Risque** : Gros clients inactifs.
        """)

    summary = rfm_df.groupby('Segment_Label').agg(
        {'CustomerID': 'count', 'Monetary': 'sum', 'Recency': 'mean'}).reset_index()
    summary.columns = ['Segment', 'Clients', 'CA Total', 'Récence (j)']

    c1, c2 = st.columns([5, 4])
    with c1:
        # CORRECTION ICI : width="stretch" pour le tableau
        st.dataframe(summary, width="stretch")
    with c2:
        fig_scat = px.scatter(summary, x='Récence (j)', y='CA Total', size='Clients', color='Segment', size_max=50)
        fig_scat.update_layout(xaxis_autorange="reversed")
        # CORRECTION ICI : width="stretch" pour le graph
        st.plotly_chart(style_plot(fig_scat, "Matrice Valeur / Risque"), width="stretch")

    st.subheader("⚡ Actions recommandées")
    a1, a2, a3 = st.columns(3)
    with a1: st.markdown('<div class="custom-alert alert-green"><strong>🏆 Champions</strong><br>VIP & Upsell</div>',
                         unsafe_allow_html=True)
    with a2: st.markdown('<div class="custom-alert alert-yellow"><strong>⚠️ À Risque</strong><br>Win-back</div>',
                         unsafe_allow_html=True)
    with a3: st.markdown('<div class="custom-alert alert-red"><strong>💤 Hibernants</strong><br>Nettoyage</div>',
                         unsafe_allow_html=True)