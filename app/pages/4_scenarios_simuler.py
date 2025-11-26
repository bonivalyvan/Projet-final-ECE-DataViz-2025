import streamlit as st
import sys
import os
import numpy as np
import plotly.graph_objects as go


from utils.visualization import load_css, style_plot
from utils.data_loader import sidebar_filters
from utils.rfm_calculator import compute_rfm

load_css()
df, analysis_date = sidebar_filters()

if df is not None:
    st.title("Simulateur d'Impact")
    rfm_df = compute_rfm(df, analysis_date)

    c1, c2, c3 = st.columns(3)
    sim_margin = c1.slider("Marge (%)", 0.05, 0.50, 0.20, 0.01)
    sim_retention = c2.slider("Rétention cible (r)", 0.1, 0.95, 0.60, 0.05)
    discount_rate = c3.number_input("Taux d'actualisation", 0.05, 0.20, 0.10)

    avg_spend = rfm_df['Monetary'].mean()
    denom = (1 + discount_rate - sim_retention)
    clv_sim = (avg_spend * sim_margin * sim_retention) / denom if denom != 0 else 0

    k1, k2 = st.columns(2)
    k1.metric("CLV Projetée", f"{clv_sim:.2f} €")
    k2.metric("Valeur Parc Client", f"{clv_sim * df['Customer ID'].nunique():,.0f} €")

    # Surface 3D
    r_range = np.linspace(0.3, 0.9, 15)
    m_range = np.linspace(0.1, 0.4, 15)
    z = [[(avg_spend * m * r) / (1 + discount_rate - r) for r in r_range] for m in m_range]
    fig_3d = go.Figure(data=[go.Surface(z=z, x=r_range, y=m_range, colorscale='Purples')])
    fig_3d.update_layout(scene=dict(xaxis_title='Rétention', yaxis_title='Marge', zaxis_title='CLV (€)'), height=500)

    # CORRECTION ICI : width="stretch"
    st.plotly_chart(style_plot(fig_3d, "Sensibilité Marge vs Rétention"), width="stretch")