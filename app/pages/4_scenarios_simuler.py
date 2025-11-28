import streamlit as st

st.set_page_config(
    page_title="Scénarios",
    page_icon="chart_with_upwards_trend",
    layout="wide"
)
import sys
import os
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px

from utils.visualization import load_css, style_plot
from utils.data_loader import sidebar_filters
from utils.rfm_calculator import compute_rfm

load_css()
df, analysis_date = sidebar_filters()

if df is not None:
    st.title("Simulateur d'Impact Business")
    rfm_df = compute_rfm(df, analysis_date)
    
    st.markdown("#### Paramètres de Simulation")
    
    # parametres avec tooltips
    c1, c2, c3 = st.columns(3)
    sim_margin = c1.slider("Marge %", 0.05, 0.50, 0.20, 0.01, 
                          help="Pourcentage de profit sur chaque vente")
    sim_retention = c2.slider("Rétention Cible (R)", 0.1, 0.95, 0.60, 0.05,
                              help="Probabilité qu'un client revienne acheter")
    discount_rate = c3.number_input("Taux d'Actualisation (D)", 0.05, 0.20, 0.10, 0.01,
                                   help="Coût du capital, préférence temporelle")
    
    # calcul clv baseline et scenario
    avg_spend = rfm_df['Monetary'].mean()
    denom = (1 + discount_rate - sim_retention)
    clv_baseline = (avg_spend * 0.20 * 0.60) / (1 + 0.10 - 0.60) if (1 + 0.10 - 0.60) != 0 else 0
    clv_sim = (avg_spend * sim_margin * sim_retention) / denom if denom != 0 else 0
    
    # clv baseline vs scenario - ajout pour comparer visuellement
    st.markdown("###")
    st.subheader("CLV Baseline vs Scénario")
    
    k1, k2, k3 = st.columns(3)
    k1.metric("CLV Baseline (Défaut)", f"{clv_baseline:.2f} €", 
             help="CLV avec Marge 20%, Rétention 60%, D=10%")
    k2.metric("CLV Projetée (Scénario)", f"{clv_sim:.2f} €", 
             delta=f"{clv_sim - clv_baseline:.2f} €")
    k3.metric("Valeur Parc Client", f"{clv_sim * df['Customer ID'].nunique():,.0f} €",
             help="CLV x Nombre de clients actifs")
    
    # graphique comparatif baseline vs scenario
    comparison = pd.DataFrame({
        'type': ['baseline', 'scenario'],
        'clv': [clv_baseline, clv_sim],
        'marge': [0.20, sim_margin],
        'retention': [0.60, sim_retention]
    })
    
    fig_comp = px.bar(comparison, x='type', y='clv', text_auto='.2f', 
                     color='type', color_discrete_map={'baseline': '#94A3B8', 'scenario': '#4F46E5'})
    st.plotly_chart(style_plot(fig_comp, "Comparaison CLV : Baseline vs Scénario"), use_container_width=True)

    # clv projetee par segment rfm - ajout pour voir impact par segment
    st.markdown("---")
    st.subheader("CLV Projetée par Segment RFM")
    
    avg_spend_by_seg = rfm_df.groupby('Segment_Label')['Monetary'].mean().reset_index()
    avg_spend_by_seg.columns = ['Segment', 'CA Historique']
    avg_spend_by_seg['CLV Baseline'] = avg_spend_by_seg['CA Historique']
    avg_spend_by_seg['CLV Scénario'] = (avg_spend_by_seg['CA Historique'] * sim_margin * sim_retention) / denom if denom != 0 else 0
    avg_spend_by_seg['delta'] = avg_spend_by_seg['CLV Scénario'] - avg_spend_by_seg['CLV Baseline']
    
    fig_seg_clv = go.Figure()
    fig_seg_clv.add_trace(go.Bar(x=avg_spend_by_seg['Segment'], y=avg_spend_by_seg['CLV Baseline'], 
                                name='CLV Baseline', marker_color='#94A3B8'))
    fig_seg_clv.add_trace(go.Bar(x=avg_spend_by_seg['Segment'], y=avg_spend_by_seg['CLV Scénario'], 
                                name='CLV Scénario', marker_color='#4F46E5'))
    fig_seg_clv.update_layout(barmode='group')
    st.plotly_chart(style_plot(fig_seg_clv, "CLV par Segment : Impact du Scénario"), use_container_width=True)
    
    st.dataframe(avg_spend_by_seg.round(2), use_container_width=True)

    # sensibilite 3d
    st.markdown("---")
    st.subheader("Analyse de Sensibilité : Marge x Rétention")
    
    r_range = np.linspace(0.3, 0.9, 15)
    m_range = np.linspace(0.1, 0.4, 15)
    z = [[(avg_spend * m * r) / (1 + discount_rate - r) if (1 + discount_rate - r) != 0 else 0 
          for r in r_range] for m in m_range]
    
    fig_3d = go.Figure(data=[go.Surface(z=z, x=r_range, y=m_range, colorscale='Purples')])
    fig_3d.update_layout(
        scene=dict(
            xaxis_title='Taux de Rétention (R)',
            yaxis_title='Marge %',
            zaxis_title='CLV'
        ),
        height=600
    )
    st.plotly_chart(style_plot(fig_3d, "Surface de Sensibilité CLV"), use_container_width=True)
    
    st.markdown("""
    **Comment lire ce graphique** : Chaque point représente une combinaison Marge / Rétention et la CLV résultante.
    Plus la surface est haute (violet foncé), plus la CLV est élevée.
    Utiliser ce graphique pour identifier les zones optimales où investir.
    **Insight** : Une hausse de 5% de rétention impacte plus la CLV qu'une hausse de 5% de marge.
    """)