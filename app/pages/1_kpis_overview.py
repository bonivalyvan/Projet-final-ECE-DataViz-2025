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
    st.title("Tableau de Bord Exécutif")
    rfm_df = compute_rfm(df, analysis_date)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Clients Actifs", f"{df['Customer ID'].nunique():,}")
    c2.metric("Chiffre d'Affaires", f"{df['TotalPrice'].sum():,.0f} €")
    c3.metric("Panier Moyen", f"{df['TotalPrice'].sum() / df['Invoice'].nunique():.1f} €")
    c4.metric("CLV Hist. Moy.", f"{rfm_df['Monetary'].mean():.1f} €")

    st.markdown("###")
    col1, col2 = st.columns([3, 2])

    with col1:
        top_countries = df.groupby('Country')['TotalPrice'].sum().reset_index().sort_values('TotalPrice',
                                                                                            ascending=False).head(8)
        fig_country = px.bar(top_countries, x='TotalPrice', y='Country', orientation='h', text_auto='.2s',
                             color='TotalPrice', color_continuous_scale='Purples')
        # CORRECTION ICI : width="stretch"
        st.plotly_chart(style_plot(fig_country, "Top Marchés (CA)"), width="stretch")

    with col2:
        seg_counts = rfm_df['Segment_Label'].value_counts().reset_index()
        seg_counts.columns = ['Segment', 'Count']
        fig_pie = px.pie(seg_counts, names='Segment', values='Count', hole=0.6,
                         color_discrete_sequence=px.colors.qualitative.Prism)
        # CORRECTION ICI : width="stretch"
        st.plotly_chart(style_plot(fig_pie, "Répartition Segments"), width="stretch")