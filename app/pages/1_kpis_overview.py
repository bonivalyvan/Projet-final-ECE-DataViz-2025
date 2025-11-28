import streamlit as st
import sys
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from utils.visualization import load_css, style_plot, display_active_filters
from utils.data_loader import sidebar_filters
from utils.rfm_calculator import compute_rfm
from utils.cohort_calculator import compute_cohorts
from utils.kpi_helpers import get_kpi_help, KPI_DEFINITIONS

load_css()
df, analysis_date = sidebar_filters()

if df is not None:
    st.title("📊 Tableau de Bord Exécutif")
    
    # Afficher les filtres actifs
    from utils.data_loader import date_range, selected_countries, return_mode
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ✅ Filtres Actifs")
    st.sidebar.markdown(f"**Période** : {date_range[0].strftime('%d/%m/%y')} → {date_range[1].strftime('%d/%m/%y')}")
    st.sidebar.markdown(f"**Pays** : {', '.join(selected_countries[:3])}{'...' if len(selected_countries) > 3 else ''}")
    if return_mode == "Exclure les retours":
        st.sidebar.markdown("**📦 Retours** : ❌ Exclus")
    elif return_mode == "Uniquement les retours":
        st.sidebar.markdown("**📦 Retours** : Uniquement")
    else:
        st.sidebar.markdown("**📦 Retours** : ✅ Inclus")
    
    rfm_df = compute_rfm(df, analysis_date)
    
    # ============ KPIs PRINCIPAUX ============
    st.markdown("### 🎯 KPIs Clés")
    
    nb_clients = df['Customer ID'].nunique()
    ca_total = df['TotalPrice'].sum()
    panier_moyen = df['TotalPrice'].sum() / df['Invoice'].nunique() if df['Invoice'].nunique() > 0 else 0
    clv_hist = rfm_df['Monetary'].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "👥 Clients Actifs",
            f"{nb_clients:,}",
            help=f"{get_kpi_help('clients_actifs')}"
        )
    
    with col2:
        st.metric(
            "💰 Chiffre d'Affaires",
            f"{ca_total:,.0f} £",
            help=f"{get_kpi_help('ca_total')}"
        )
    
    with col3:
        st.metric(
            "🛒 Panier Moyen",
            f"{panier_moyen:.1f} £",
            help=f"{get_kpi_help('panier_moyen')}"
        )
    
    with col4:
        st.metric(
            "📈 CLV Empirique",
            f"{clv_hist:.1f} £",
            help=f"{get_kpi_help('clv_historique')}"
        )

    st.markdown("###")
    
    # ============ GRAPHIQUES PRINCIPAUX ============
    st.markdown("### 📈 Vue d'Ensemble")
    
    col1, col2 = st.columns([3, 2])

    with col1:
        # Top pays
        top_countries = df.groupby('Country')['TotalPrice'].sum().reset_index().sort_values('TotalPrice', ascending=False).head(8)
        fig_country = px.bar(
            top_countries, 
            x='TotalPrice', 
            y='Country', 
            orientation='h', 
            text_auto='.2s',
            color='TotalPrice', 
            color_continuous_scale='Purples',
            labels={'TotalPrice': 'CA (£)', 'Country': 'Pays'}
        )
        fig_country.update_layout(yaxis={'categoryorder': 'total ascending'})
        fig_country.update_xaxes(title_text="Chiffre d'Affaires (£)")
        fig_country.update_yaxes(title_text="Pays")
        st.plotly_chart(style_plot(fig_country, "🌍 Top 8 Marchés par CA"), use_container_width=True)

    with col2:
        # Répartition segments
        seg_counts = rfm_df['Segment_Label'].value_counts().reset_index()
        seg_counts.columns = ['Segment', 'Count']
        fig_pie = px.pie(
            seg_counts, 
            names='Segment', 
            values='Count', 
            hole=0.6,
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(style_plot(fig_pie, "📊 Répartition Segments RFM"), use_container_width=True)

    # ============ ÉVOLUTION TEMPORELLE ============
    st.markdown("---")
    st.markdown("### 📉 Saisonnalité & Tendances")
    
    df['YearMonth'] = df['InvoiceDate'].dt.to_period('M')
    monthly_ca = df.groupby('YearMonth').agg({
        'TotalPrice': 'sum',
        'Customer ID': 'nunique'
    }).reset_index()
    monthly_ca['YearMonth'] = monthly_ca['YearMonth'].astype(str)
    
    # Graphique double axe CA et clients
    fig_time = make_subplots(specs=[[{"secondary_y": True}]])
    fig_time.add_trace(
        go.Bar(
            x=monthly_ca['YearMonth'], 
            y=monthly_ca['TotalPrice'], 
            name="CA",
            marker_color='#4F46E5'
        ), 
        secondary_y=False
    )
    fig_time.add_trace(
        go.Scatter(
            x=monthly_ca['YearMonth'], 
            y=monthly_ca['Customer ID'], 
            name="Clients Actifs",
            mode='lines+markers', 
            marker_color='#10B981',
            line=dict(width=3)
        ), 
        secondary_y=True
    )
    fig_time.update_xaxes(title_text="Mois", tickangle=-45)
    fig_time.update_yaxes(title_text="CA (£)", secondary_y=False)
    fig_time.update_yaxes(title_text="Clients Actifs", secondary_y=True)
    fig_time.update_layout(
        hovermode='x unified',
        height=450,
        title_text="📊 CA Mensuel & Clients Actifs"
    )
    st.plotly_chart(style_plot(fig_time), use_container_width=True)
    
    st.markdown("""
    💡 **Lecture** : Les pics de CA correspondent-ils aux périodes de forte acquisition (Noël, Black Friday)? 
    La courbe clients chute-t-elle avec le temps (indication d'une mauvaise rétention)?
    """)

    # ============ RÉTENTION & CLV ============
    st.markdown("---")
    st.markdown("### 📊 Rétention & CLV par Cohorte")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Calcul rétention moyen
        retention_matrix, cohort_size = compute_cohorts(df)
        
        # Rétention moyenne par période
        avg_retention_by_period = {}
        for col in retention_matrix.columns:
            if col <= 12:  # Jusqu'à M+12
                avg_ret = retention_matrix[col].mean()
                if not pd.isna(avg_ret):
                    avg_retention_by_period[f"M+{col}"] = avg_ret
        
        if avg_retention_by_period:
            df_ret = pd.DataFrame(list(avg_retention_by_period.items()), columns=['Période', 'Rétention'])
            fig_ret = px.bar(
                df_ret, 
                x='Période', 
                y='Rétention',
                text_auto='.0%',
                color='Rétention',
                color_continuous_scale='Greens'
            )
            fig_ret.update_yaxes(tickformat='.0%')
            st.plotly_chart(style_plot(fig_ret, "📈 Rétention Moyenne par Période"), use_container_width=True)
    
    with col2:
        # CLV empirique par cohorte
        clv_by_cohort = df.copy()
        clv_by_cohort['CohortMonth'] = clv_by_cohort.groupby('Customer ID')['InvoiceDate'].transform('min').dt.to_period('M')
        
        clv_data = clv_by_cohort.groupby('CohortMonth').agg({
            'TotalPrice': 'sum',
            'Customer ID': 'nunique'
        }).reset_index()
        
        clv_data['CLV'] = clv_data['TotalPrice'] / clv_data['Customer ID']
        clv_data['CohortMonth'] = clv_data['CohortMonth'].astype(str)
        
        fig_clv = px.bar(
            clv_data, 
            x='CohortMonth', 
            y='CLV',
            text_auto='.0f',
            color='CLV',
            color_continuous_scale='Blues'
        )
        fig_clv.update_xaxes(tickangle=-45, title_text="Cohorte")
        fig_clv.update_yaxes(title_text="CLV (£)")
        st.plotly_chart(style_plot(fig_clv, "💵 CLV Empirique par Cohorte"), use_container_width=True)

    # ============ RFM SCORE DISTRIBUTION ============
    st.markdown("---")
    st.markdown("### 🎯 Distribution des Scores RFM")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        r_dist = pd.Series(rfm_df['R_Score'].value_counts().sort_index())
        fig_r = px.bar(r_dist, labels={'index': 'R Score', 'value': 'Clients'}, color=r_dist.index)
        fig_r.update_xaxes(title_text="Récence Score")
        fig_r.update_yaxes(title_text="Nombre de Clients")
        st.plotly_chart(style_plot(fig_r, "📍 Récence"), use_container_width=True)
    
    with col2:
        f_dist = pd.Series(rfm_df['F_Score'].value_counts().sort_index())
        fig_f = px.bar(f_dist, labels={'index': 'F Score', 'value': 'Clients'}, color=f_dist.index)
        fig_f.update_xaxes(title_text="Fréquence Score")
        fig_f.update_yaxes(title_text="Nombre de Clients")
        st.plotly_chart(style_plot(fig_f, "🔄 Fréquence"), use_container_width=True)
    
    with col3:
        m_dist = pd.Series(rfm_df['M_Score'].value_counts().sort_index())
        fig_m = px.bar(m_dist, labels={'index': 'M Score', 'value': 'Clients'}, color=m_dist.index)
        fig_m.update_xaxes(title_text="Montant Score")
        fig_m.update_yaxes(title_text="Nombre de Clients")
        st.plotly_chart(style_plot(fig_m, "💰 Montant"), use_container_width=True)
    
    st.markdown("""
    📌 **Interprétation** : 
    - Score 4 = clients excellents (récents, fréquents, haut montant)
    - Score 1 = clients critiques (anciens, peu fréquents, bas montant)
    """)
