import streamlit as st
import sys
import os
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from utils.visualization import load_css, style_plot
from utils.data_loader import sidebar_filters
from utils.rfm_calculator import compute_rfm
from utils.kpi_helpers import get_kpi_help

load_css()
df, analysis_date = sidebar_filters()

if df is not None:
    st.title("🎮 Simulateur d'Impact Business")
    rfm_df = compute_rfm(df, analysis_date)

    st.markdown("""
    Ajustez les paramètres ci-dessous pour simuler l'impact sur la **CLV**, le **CA** et la **Rétention**.
    Cette analyse aide à **prioriser les investissements marketing** et **quantifier le ROI** des initiatives.
    """)

    # ============ PARAMÈTRES DE SIMULATION ============
    st.markdown("### ⚙️ Paramètres de Simulation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sim_margin = st.slider(
            "💰 Marge (%)",
            min_value=0.05,
            max_value=0.50,
            value=0.20,
            step=0.01,
            help=f"{get_kpi_help('clv_formule')}"
        )
    
    with col2:
        sim_retention = st.slider(
            "🔄 Rétention cible (r)",
            min_value=0.1,
            max_value=0.95,
            value=0.60,
            step=0.05,
            help="Probabilité qu'un client revienne acheter le mois suivant (60% = 0,6)"
        )
    
    with col3:
        discount_rate = st.number_input(
            "📊 Taux d'actualisation (d)",
            min_value=0.05,
            max_value=0.20,
            value=0.10,
            step=0.01,
            help="Coût du capital / préférence temporelle (10% = coût d'un euro emprunté)"
        )

    # ============ CALCULS CLV ============
    avg_spend = rfm_df['Monetary'].mean()
    
    # CLV Baseline (défaut: marge 20%, rétention 60%, d=10%)
    baseline_margin = 0.20
    baseline_retention = 0.60
    baseline_discount = 0.10
    
    denom_baseline = (1 + baseline_discount - baseline_retention)
    denom_sim = (1 + discount_rate - sim_retention)
    
    clv_baseline = (avg_spend * baseline_margin * baseline_retention) / denom_baseline if denom_baseline != 0 else 0
    clv_sim = (avg_spend * sim_margin * sim_retention) / denom_sim if denom_sim != 0 else 0
    
    delta_clv = clv_sim - clv_baseline
    delta_clv_pct = (delta_clv / clv_baseline * 100) if clv_baseline != 0 else 0
    
    # ============ AFFICHAGE DES KPIs ============
    st.markdown("### 📊 Comparaison Baseline vs Scénario")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💵 CLV Baseline",
            f"{clv_baseline:.2f} £",
            help="Référence : marge 20%, rétention 60%, d=10%"
        )
    
    with col2:
        st.metric(
            "🎯 CLV Scénario simulé",
            f"{clv_sim:.2f} £",
            delta=f"{delta_clv:.2f} £ ({delta_clv_pct:+.1f}%)",
            delta_color="normal" if delta_clv >= 0 else "inverse"
        )
    
    with col3:
        st.metric(
            "👥 Parc Client",
            f"{df['Customer ID'].nunique():,}",
            help="Nombre de clients actifs dans la période"
        )
    
    with col4:
        total_value_scenario = clv_sim * df['Customer ID'].nunique()
        total_value_baseline = clv_baseline * df['Customer ID'].nunique()
        delta_value = total_value_scenario - total_value_baseline
        
        st.metric(
            "💰 Valeur Parc (Scénario simulé)",
            f"{total_value_scenario:,.0f} £",
            delta=f"{delta_value:,.0f} £",
            delta_color="normal" if delta_value >= 0 else "inverse"
        )

    # ============ GRAPHIQUES COMPARATIFS ============
    st.markdown("---")
    st.markdown("### 📈 Visualisations de l'Impact")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Comparaison simple baseline vs scénario
        comparison_df = pd.DataFrame({
            'Scénario': ['Baseline', 'Simulation'],
            'CLV': [clv_baseline, clv_sim]
        })
        
        fig_comp = px.bar(
            comparison_df,
            x='Scénario',
            y='CLV',
            text_auto='.2f',
            color='Scénario',
            color_discrete_map={'Baseline': '#94A3B8', 'Simulation': '#4F46E5'}
        )
        fig_comp.update_yaxes(title_text="CLV (£)")
        fig_comp.update_xaxes(title_text="")
        
        st.plotly_chart(style_plot(fig_comp, "📊 CLV : Baseline vs Simulation"), use_container_width=True)
    
    with col2:
        # Impact par segment
        avg_spend_by_seg = rfm_df.groupby('Segment_Label')['Monetary'].mean().reset_index()
        avg_spend_by_seg.columns = ['Segment', 'CA Historique']
        avg_spend_by_seg['CLV Baseline'] = (avg_spend_by_seg['CA Historique'] * baseline_margin * baseline_retention) / denom_baseline
        avg_spend_by_seg['CLV Simulation'] = (avg_spend_by_seg['CA Historique'] * sim_margin * sim_retention) / denom_sim
        
        fig_seg = go.Figure()
        fig_seg.add_trace(go.Bar(
            x=avg_spend_by_seg['Segment'],
            y=avg_spend_by_seg['CLV Baseline'],
            name='Baseline',
            marker_color='#94A3B8'
        ))
        fig_seg.add_trace(go.Bar(
            x=avg_spend_by_seg['Segment'],
            y=avg_spend_by_seg['CLV Simulation'],
            name='Scénario simulé',
            marker_color='#4F46E5'
        ))
        fig_seg.update_layout(barmode='group', xaxis_title="Segment", yaxis_title="CLV (£)")
        
        st.plotly_chart(style_plot(fig_seg, "📊 Par Segment (Baseline vs Simulation)"), use_container_width=True)

    # ============ ANALYSE DE SENSIBILITÉ ============
    st.markdown("---")
    st.markdown("### 🔬 Analyse de Sensibilité (Marge × Rétention)")
    
    st.markdown("""
    Ces graphiques montrent comment la CLV varie en fonction des changements de **marge** et de **rétention**.
    Utilisez-les pour voir si une hausse de rétention ou de marge est la plus rentable.
    """)

    # Surface 3D
    r_range = np.linspace(0.3, 0.9, 15)
    m_range = np.linspace(0.1, 0.4, 15)
    z = [[
        (avg_spend * m * r) / (1 + discount_rate - r) if (1 + discount_rate - r) != 0 else 0
        for r in r_range
    ] for m in m_range]
    
    fig_3d = go.Figure(data=[go.Surface(
        z=z,
        x=r_range,
        y=m_range,
        colorscale='Purples',
        colorbar=dict(title="CLV (£)")
    )])
    fig_3d.update_layout(
        scene=dict(
            xaxis_title='Rétention (r)',
            yaxis_title='Marge (%)',
            zaxis_title='CLV (£)',
            xaxis=dict(backgroundcolor="rgb(240, 240, 240)", gridcolor="white"),
            yaxis=dict(backgroundcolor="rgb(240, 240, 240)", gridcolor="white"),
            zaxis=dict(backgroundcolor="rgb(240, 240, 240)", gridcolor="white")
        ),
        height=600,
        title_text="🔬 Surface de Sensibilité CLV"
    )
    
    st.plotly_chart(fig_3d, use_container_width=True)

    # Courbe 2D : CLV en fonction de la rétention pour une marge fixée (marge simulée)
    clv_vs_r = []
    for r in r_range:
        denom_r = (1 + discount_rate - r)
        clv_r = (avg_spend * sim_margin * r) / denom_r if denom_r != 0 else 0
        clv_vs_r.append(clv_r)

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=r_range,
        y=clv_vs_r,
        mode='lines+markers',
        name='CLV vs Rétention',
        line=dict(color='#4F46E5')
    ))
    fig_line.update_layout(
        xaxis_title='Rétention (r)',
        yaxis_title='CLV (£)',
        title='📉 Sensibilité CLV à la Rétention (marge fixée)'
    )

    st.plotly_chart(style_plot(fig_line, "📉 Sensibilité CLV à la Rétention"), use_container_width=True)
    
    st.markdown("""
    💡 **Lecture** :
    - La surface 3D montre toutes les combinaisons Marge × Rétention.
    - La courbe 2D montre l'effet marginal d'un gain de rétention à marge fixée.
    """)

    # ============ SCENARIOS SPÉDÉFINIS ============
    st.markdown("---")
    st.markdown("### 🎯 Scénarios Pré-définis")
    
    scenarios = {
        "Optimiste (+10% rétention)": {"retention": baseline_retention + 0.10, "margin": baseline_margin, "name": "Optimiste"},
        "Agressif (+10% marge)": {"retention": baseline_retention, "margin": baseline_margin + 0.10, "name": "Agressif"},
        "Conservateur (-5% retours)": {"retention": baseline_retention - 0.05, "margin": baseline_margin, "name": "Conservateur"},
    }
    
    scenario_results = []
    for scenario_name, params in scenarios.items():
        denom_sc = (1 + discount_rate - params["retention"])
        clv_sc = (avg_spend * params["margin"] * params["retention"]) / denom_sc if denom_sc != 0 else 0
        scenario_results.append({
            "Scénario": params["name"],
            "CLV": clv_sc,
            "Delta vs Baseline": clv_sc - clv_baseline,
            "Delta %": (clv_sc - clv_baseline) / clv_baseline * 100 if clv_baseline != 0 else 0
        })
    
    df_scenarios = pd.DataFrame(scenario_results)

    col_s1, col_s2, col_s3 = st.columns(3)
    scenario_cols = [col_s1, col_s2, col_s3]
    
    for i, scenario in enumerate(df_scenarios.to_dict('records')):
        with scenario_cols[i]:
            delta_val = scenario["Delta vs Baseline"]
            delta_color = "normal" if scenario["Delta %"] >= 0 else "inverse"
            st.metric(
                f"📊 {scenario['Scénario']}",
                f"{scenario['CLV']:.2f} £",
                delta=f"{delta_val:+.2f} £ ({scenario['Delta %']:+.1f}%)",
                delta_color=delta_color
            )

    # ============ IMPACT ROI ============
    st.markdown("---")
    st.markdown("### 💹 Calcul du ROI")
    
    st.write("**Exemple de ROI pour une initiative** :")
    
    col1, col2 = st.columns(2)
    
    with col1:
        initiative_cost = st.number_input(
            "💸 Coût de l'initiative (£)",
            min_value=0.0,
            value=5000.0,
            step=100.0,
            help="Budget marketing pour une campagne de rétention / acquisition"
        )
    
    with col2:
        affected_customers = st.number_input(
            "👥 Clients affectés",
            min_value=0,
            value=int(df['Customer ID'].nunique() / 10),
            step=100,
            help="Nombre de clients atteints par cette initiative"
        )
    
    if affected_customers > 0:
        value_created = (clv_sim - clv_baseline) * affected_customers
        roi = ((value_created - initiative_cost) / initiative_cost * 100) if initiative_cost > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("📈 Valeur Créée", f"{value_created:,.0f} £")
        col2.metric("💰 ROI", f"{roi:+.1f}%", delta_color="normal" if roi >= 0 else "inverse")
        col3.metric("⏱️ Payback", f"{initiative_cost / (value_created / 365) if value_created > 0 else float('inf'):.0f} jours")
        
        if roi >= 0:
            st.success(f"✅ Initiative rentable ! ROI positif de {roi:.1f}%")
        else:
            st.error(f"❌ Initiative non rentable. ROI négatif de {roi:.1f}%")
