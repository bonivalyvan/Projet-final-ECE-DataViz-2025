import streamlit as st

st.set_page_config(
    page_title="KPIs Overview",
    page_icon="dashboard",
    layout="wide"
)
import sys
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.visualization import load_css, style_plot
from utils.data_loader import sidebar_filters
from utils.rfm_calculator import compute_rfm

load_css()
df, analysis_date = sidebar_filters()

if df is not None:
    st.title("Tableau de Bord Exécutif")
    rfm_df = compute_rfm(df, analysis_date)

    # kpis principaux
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Clients Actifs", f"{df['Customer ID'].nunique():,}")
    c2.metric("Chiffre d'Affaires", f"{df['TotalPrice'].sum():,.0f} €")
    c3.metric("Panier Moyen", f"{df['TotalPrice'].sum() / df['Invoice'].nunique():.1f} €")
    c4.metric("CLV Historique Moyenne", f"{rfm_df['Monetary'].mean():.1f} €")
    
    st.markdown("###")
    
    # graphiques
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # top pays
        top_countries = df.groupby('Country')['TotalPrice'].sum().reset_index().sort_values('TotalPrice', ascending=False).head(8)
        fig_country = px.bar(top_countries, x='TotalPrice', y='Country', orientation='h', 
                           text_auto='.2s', color='TotalPrice', color_continuous_scale='RdYlGn_r')
        fig_country.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(style_plot(fig_country, "Top 8 Marchés par CA"), use_container_width=True)
        
    with col2:
        # repartition segments
        seg_counts = rfm_df['Segment_Label'].value_counts().reset_index()
        seg_counts.columns = ['Segment', 'Count']
        fig_pie = px.pie(seg_counts, names='Segment', values='Count', hole=0.6, 
                       color_discrete_sequence=px.colors.qualitative.Prism)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(style_plot(fig_pie, "Répartition Segments RFM"), use_container_width=True)

    # evolution temporelle - ajout pour analyser la saisonnalite
    st.markdown("---")
    st.subheader("Évolution Temporelle et Saisonnalité")
    
    df['YearMonth'] = df['InvoiceDate'].dt.to_period('M')
    monthly_ca = df.groupby('YearMonth').agg({
        'TotalPrice': 'sum',
        'Customer ID': 'nunique'
    }).reset_index()
    monthly_ca['YearMonth'] = monthly_ca['YearMonth'].astype(str)
    
    # graphique double axe ca et clients
    fig_time = make_subplots(specs=[[{"secondary_y": True}]])
    fig_time.add_trace(go.Bar(x=monthly_ca['YearMonth'], y=monthly_ca['TotalPrice'], 
                              name="CA", marker_color='#4F46E5'), secondary_y=False)
    fig_time.add_trace(go.Scatter(x=monthly_ca['YearMonth'], y=monthly_ca['Customer ID'], 
                                  name="Clients Actifs", mode='lines+markers', marker_color='#10B981'), secondary_y=True)
    fig_time.update_xaxes(title_text="Mois", tickangle=-45)
    fig_time.update_yaxes(title_text="CA", secondary_y=False)
    fig_time.update_yaxes(title_text="Clients", secondary_y=True)
    st.plotly_chart(style_plot(fig_time, "CA Mensuel et Clients Actifs"), use_container_width=True)