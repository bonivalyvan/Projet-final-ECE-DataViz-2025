import streamlit as st

st.set_page_config(
    page_title="Segmentation",
    page_icon="people",
    layout="wide"
)
import sys
import os
import plotly.express as px

from utils.visualization import load_css, style_plot
from utils.data_loader import sidebar_filters
from utils.rfm_calculator import compute_rfm

load_css()
df, analysis_date = sidebar_filters()

if df is not None:
    st.title("Segmentation RFM et Priorisation")
    rfm_df = compute_rfm(df, analysis_date)

    # guide des segments - ajout pour expliquer les categories
    with st.expander("Guide des segments RFM : Qui sont-ils ?", expanded=False):
        st.markdown("""
        La segmentation est basée sur les scores Récence (R) et Fréquence/Montant (FM).
        
        - **Champions** : Ont acheté très récemment, achètent souvent et pour cher | Action : Chouchouter
        - **Loyaux Potentiels** : Clients récents avec une bonne fréquence | Action : Cross-selling
        - **Nouveaux Prometteurs** : Viennent de faire leur premier achat récent | Action : Welcome Pack
        - **À Risque** : Gros clients passés qui n'ont pas acheté depuis longtemps | Action : Réactivation urgente
        - **Hibernants** : Anciens petits clients inactifs | Action : Automatisation ou nettoyage
        
        **Formule des scores :**
        - R (Récence) : Plus récent = score élevé (1 à 4)
        - F (Fréquence) : Plus souvent = score élevé (1 à 4)
        - M (Montant) : Plus dépensé = score élevé (1 à 4)
        """)

    # table rfm
    summary = rfm_df.groupby('Segment_Label').agg({
        'CustomerID': 'count', 
        'Monetary': 'sum', 
        'Recency': 'mean',
        'Frequency': 'mean'
    }).reset_index()
    summary.columns = ['Segment', 'Nb Clients', 'CA Total', 'Récence Moy. (Jours)', 'Fréquence Moy.']
    summary['CA Total'] = summary['CA Total'].round(0).astype(int)
    summary['Récence Moy. (Jours)'] = summary['Récence Moy. (Jours)'].round(0).astype(int)
    summary['Fréquence Moy.'] = summary['Fréquence Moy.'].round(1)
    
    c1, c2 = st.columns([5, 4])
    
    with c1:
        st.subheader("Détails des Segments")
        st.dataframe(summary, use_container_width=True)
    
    with c2:
        st.subheader("Matrice Valeur / Risque")
        fig_scat = px.scatter(summary, x='Récence Moy. (Jours)', y='CA Total', 
                            size='Nb Clients', color='Segment', size_max=50, 
                            color_discrete_sequence=px.colors.qualitative.Bold,
                            hover_data=['Fréquence Moy.'])
        fig_scat.update_layout(xaxis_autorange="reversed")
        st.plotly_chart(style_plot(fig_scat, ""), use_container_width=True)

    # clv par segment rfm - ajout pour montrer la valeur de chaque segment
    st.markdown("---")
    st.subheader("CLV Moyenne par Segment RFM")
    
    clv_by_segment = rfm_df.groupby('Segment_Label')['Monetary'].mean().reset_index()
    clv_by_segment.columns = ['Segment', 'CLV Moyenne']
    clv_by_segment = clv_by_segment.sort_values('CLV Moyenne', ascending=False)
    
    fig_clv_seg = px.bar(clv_by_segment, x='Segment', y='CLV Moyenne', 
                        text_auto='.1f', color='CLV Moyenne', color_continuous_scale='Greens')
    st.plotly_chart(style_plot(fig_clv_seg, "Valeur Vie Client Moyenne par Segment"), use_container_width=True)
    
    st.dataframe(clv_by_segment, use_container_width=True)
    
    st.markdown("""
    Interprétation : Un Champion vaut en moyenne X fois plus qu'un Hibernant.
    Utiliser cette information pour calibrer les budgets d'acquisition et de rétention.
    ROI d'une campagne de réactivation = CLV Segment x Taux de succès - Coût campagne
    """)
        
    # actions recommandees
    st.markdown("---")
    st.subheader("Actions Recommandées par Segment")
    a1, a2, a3 = st.columns(3)
    with a1: 
        st.markdown('<div class="custom-alert alert-green"><strong>Champions</strong><br>Programme VIP, accès anticipé</div>', unsafe_allow_html=True)
    with a2: 
        st.markdown('<div class="custom-alert alert-yellow"><strong>À Risque</strong><br>Offre "Reviens", remise 10-15%</div>', unsafe_allow_html=True)
    with a3: 
        st.markdown('<div class="custom-alert alert-red"><strong>Hibernants</strong><br>Email de réactivation ou nettoyage BDD</div>', unsafe_allow_html=True)