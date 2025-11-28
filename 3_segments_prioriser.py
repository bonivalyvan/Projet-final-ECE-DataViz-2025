import streamlit as st
import sys
import os
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from utils.visualization import load_css, style_plot, add_export_button
from utils.data_loader import sidebar_filters, date_range, selected_countries, return_mode
from utils.rfm_calculator import compute_rfm

load_css()
df, analysis_date = sidebar_filters()

if df is not None:
    st.title("🎯 Segmentation & Priorisation RFM")
    rfm_df = compute_rfm(df, analysis_date)

    # ============ GUIDE DES SEGMENTS ============
    with st.expander("📘 Comprendre les Segments RFM", expanded=False):
        st.markdown("""
        La segmentation RFM identifie 5 groupes de clients basés sur leurs comportements d'achat.
        
        | Segment | Caractéristique | Action |
        |---------|-----------------|--------|
        | **🏆 Champions** | Achètent récemment, souvent et cher | **VIP & Upselling** |
        | **🌱 Loyaux Potentiels** | Bons clients récents | **Cross-selling** |
        | **👋 Nouveaux Prometteurs** | Premiers achats récents | **Welcome Program** |
        | **⚠️ À Risque** | Anciens clients inactifs avec forte valeur | **Win-back urgent** |
        | **💤 Hibernants** | Inactifs depuis longtemps | **Nettoyage/Réactivation** |
        
        **Formule** : Chaque client reçoit un score 1-4 pour :
        - **R (Récence)** : Jours depuis dernier achat (4=aujourd'hui, 1=longtemps)
        - **F (Fréquence)** : Nombre d'achats (4=très actif, 1=peu actif)
        - **M (Montant)** : Total dépensé (4=haut montant, 1=bas montant)
        """)

    # ============ TABLE RFM COMPLÈTE ============
    st.markdown("### 📊 Table RFM Complète (Codes, Labels, Volumes, CA, Marge, Panier)")
    
    # Convertir les colonnes score en numériques (au cas où elles seraient catégories)
    rfm_df['R_Score'] = pd.to_numeric(rfm_df['R_Score'], errors='coerce')
    rfm_df['F_Score'] = pd.to_numeric(rfm_df['F_Score'], errors='coerce')
    rfm_df['M_Score'] = pd.to_numeric(rfm_df['M_Score'], errors='coerce')
    rfm_df['Recency'] = pd.to_numeric(rfm_df['Recency'], errors='coerce')
    rfm_df['Frequency'] = pd.to_numeric(rfm_df['Frequency'], errors='coerce')
    rfm_df['Monetary'] = pd.to_numeric(rfm_df['Monetary'], errors='coerce')
    
    # Créer codes RFM (ex: "444" = R4+F4+M4)
    rfm_df['RFM_Code'] = (
        rfm_df['R_Score'].astype(int).astype(str) + 
        rfm_df['F_Score'].astype(int).astype(str) + 
        rfm_df['M_Score'].astype(int).astype(str)
    )
    
    # Estimer marge (hypothèse: 25% de marge moyenne par transaction)
    margin_rate = 0.25  # 25% marge hypothétique
    rfm_df['Marge_Estimée'] = rfm_df['Monetary'] * margin_rate
    
    # Construire table RFM détaillée - SANS 'first' sur RFM_Code (qui est string)
    rfm_table = rfm_df.groupby('Segment_Label').agg({
        'CustomerID': 'count',
        'Monetary': ['sum', 'mean'],
        'Marge_Estimée': ['sum', 'mean'],
        'Recency': 'mean',
        'Frequency': 'mean',
        'R_Score': 'mean',
        'F_Score': 'mean',
        'M_Score': 'mean'
    }).reset_index()
    
    # Aplatir les colonnes multi-niveaux
    rfm_table.columns = ['Segment', 'Volume (Clients)', 'CA_Total', 'Panier_Moyen', 
                         'Marge_Total', 'Marge_Moyen', 'Récence_Moy', 'Fréquence_Moy',
                         'R_Avg', 'F_Avg', 'M_Avg']
    rfm_table = rfm_table.sort_values('CA_Total', ascending=False)
    
    # Ajouter code RFM représentatif (ex: "444" pour Champions)
    code_map = {
        'Champions': '444',
        'Loyaux Potentiels': '343',
        'Nouveaux Prometteurs': '441',
        'À Risque': '244',
        'Hibernants': '111'
    }
    rfm_table['Code_RFM'] = rfm_table['Segment'].map(code_map).fillna('---')
    
    # Formater pour affichage
    rfm_table_display = rfm_table.copy()
    rfm_table_display['Volume (Clients)'] = rfm_table_display['Volume (Clients)'].astype(int).apply(lambda x: f"{x:,}")
    rfm_table_display['CA_Total'] = rfm_table_display['CA_Total'].apply(lambda x: f"£{x:,.0f}")
    rfm_table_display['Panier_Moyen'] = rfm_table_display['Panier_Moyen'].apply(lambda x: f"£{x:.1f}")
    rfm_table_display['Marge_Total'] = rfm_table_display['Marge_Total'].apply(lambda x: f"£{x:,.0f}")
    rfm_table_display['Marge_Moyen'] = rfm_table_display['Marge_Moyen'].apply(lambda x: f"£{x:.1f}")
    rfm_table_display['Récence_Moy'] = rfm_table_display['Récence_Moy'].apply(lambda x: f"{int(x)} j")
    rfm_table_display['Fréquence_Moy'] = rfm_table_display['Fréquence_Moy'].apply(lambda x: f"{x:.1f}")
    rfm_table_display['Priorité'] = ['🔴 CRITIQUE', '🟠 HAUTE', '🟡 MOYEN', '🟢 BASSE', '⚪ MINIMAL'][:len(rfm_table_display)]
    
    # Afficher table
    display_cols = ['Segment', 'Code_RFM', 'Volume (Clients)', 'CA_Total', 'Panier_Moyen', 
                    'Marge_Total', 'Priorité']
    st.dataframe(rfm_table_display[display_cols], use_container_width=True, hide_index=True)
    
    st.markdown("""
    **Légende** :
    - **Code RFM** : Combinaison scores Récence-Fréquence-Montant (ex: 444 = excellent, 111 = critique)
    - **Volume** : Nombre de clients dans le segment
    - **CA Total** : Chiffre d'affaires total généré (CA = Quantity × Price)
    - **Panier Moyen** : CA Total ÷ Volume
    - **Marge Total** : Profit estimé (CA × 25% marge hypothétique)
    - **Priorité** : Urgence d'activation CRM
    """)

    # ============ RÉSUMÉ PAR SEGMENT ============
    st.markdown("---")
    st.markdown("### 📊 Vue d'Ensemble des Segments")
    
    summary = rfm_table.copy()
    summary = summary.rename(columns={
        'Volume (Clients)': 'Clients',
        'CA_Total': 'CA Total',
        'Panier_Moyen': 'Panier Moyen'
    })
    summary = summary.sort_values('CA Total', ascending=False)
    
    # Ajouter le % du total
    summary['% Clients'] = (summary['Clients'] / summary['Clients'].sum() * 100).round(1)
    
    # Formater pour affichage
    display_summary = summary.copy()
    display_summary['Clients'] = display_summary['Clients'].astype(int).apply(lambda x: f"{x:,}")
    display_summary['CA Total'] = display_summary['CA Total'].apply(lambda x: f"{x:,.0f} £")
    display_summary['Panier Moyen'] = display_summary['Panier Moyen'].apply(lambda x: f"{x:.1f} £")
    display_summary['Récence_Moy'] = display_summary['Récence_Moy'].apply(lambda x: f"{int(x)} j")
    display_summary['Fréquence_Moy'] = display_summary['Fréquence_Moy'].apply(lambda x: f"{x:.1f}")
    
    st.dataframe(display_summary, use_container_width=True, hide_index=True)

    st.markdown("###")
    
        # ============ TABLEAUX DÉTAILLÉS ET MATRICE ============
    st.markdown("---")
    st.markdown("### 💼 Analyse Détail & Positionnement")
    
    # Tableau de détail - EN HAUT
    st.markdown("#### 🔍 Tableau de Détail par Segment")
    
    # Permettre le tri par segment
    selected_segment = st.selectbox(
        "Sélectionner un segment pour voir les détails",
        options=rfm_df['Segment_Label'].unique(),
        index=0,
        help="Affiche les KPIs détaillés du segment sélectionné"
    )
    
    segment_data = rfm_df[rfm_df['Segment_Label'] == selected_segment]
    
    # Afficher les métriques détaillées
    col_s1, col_s2, col_s3 = st.columns(3)
    col_s1.metric("👥 Clients", f"{len(segment_data):,}", 
                 help=f"{len(segment_data)/len(rfm_df)*100:.1f}% de la base")
    col_s2.metric("💰 CA Total", f"{segment_data['Monetary'].sum():,.0f} £",
                 help=f"Génère {segment_data['Monetary'].sum()/rfm_df['Monetary'].sum()*100:.1f}% du CA")
    col_s3.metric("📈 Panier Moyen", f"{segment_data['Monetary'].mean():.1f} £",
                 help=f"Valeur moyenne par client")
    
    # Ajouter d'autres métriques
    col_s4, col_s5, col_s6 = st.columns(3)
    col_s4.metric("📅 Récence Moy", f"{segment_data['Recency'].mean():.0f} j",
                 help="Dernier achat moyen (jours)")
    col_s5.metric("🔄 Fréquence Moy", f"{segment_data['Frequency'].mean():.1f}",
                 help="Nombre moyen d'achats")
    col_s6.metric("💎 Marge Estimée", f"{segment_data['Marge_Estimée'].sum():,.0f} £",
                 help="Marge totale estimée (25%)")
    
    # Espacement
    st.markdown("###")
    
    # Matrice Valeur / Risque - EN BAS
    st.markdown("#### 🎯 Matrice Valeur / Risque")
    
    # Utiliser les données de summary pour le scatter
    scatter_data = summary[['Segment', 'Récence_Moy', 'CA Total', 'Panier Moyen', 'Clients']].copy()
    scatter_data = scatter_data.rename(columns={'Panier Moyen': 'Panier_Moyen'})
    
    fig_scat = px.scatter(
        scatter_data,
        x='Récence_Moy',
        y='CA Total',
        size='Clients',
        color='Segment',
        size_max=50,
        color_discrete_sequence=px.colors.qualitative.Bold,
        hover_data={'Clients': True, 'Panier_Moyen': ':.1f'}
    )
    fig_scat.update_layout(
        xaxis_autorange="reversed",
        height=400,
        title_text="",
        xaxis_title="Récence (j) ←Recent | Ancien→",
        yaxis_title="CA Total (£)"
    )
    fig_scat.update_xaxes(showgrid=True, gridcolor="#E2E8F0")
    fig_scat.update_yaxes(showgrid=True, gridcolor="#E2E8F0")
    st.plotly_chart(fig_scat, use_container_width=True)
    
    st.markdown("""
    💡 **Lecture du graphique** :
    - **Bas-Gauche (Meilleur)** : Champions - Récents, haute valeur
    - **Bas-Droite (Risque)** : À Risque - Anciens mais valeur élevée
    - **Haut-Gauche (Potentiel)** : Nouveaux - Récents, à cultiver
    - **Haut-Droite (Critique)** : Hibernants - Anciens, basse valeur
    """)
    # ============ CLV PAR SEGMENT ============
    st.markdown("---")
    st.markdown("### 💵 Valeur & Potentiel par Segment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        clv_by_segment = rfm_table[['Segment', 'Panier_Moyen', 'CA_Total']].copy()
        clv_by_segment = clv_by_segment.sort_values('Panier_Moyen', ascending=True)
        clv_by_segment.columns = ['Segment', 'CLV Moyenne', 'CLV Totale']
        
        fig_clv = px.bar(
            clv_by_segment,
            x='CLV Moyenne',
            y='Segment',
            orientation='h',
            text_auto='.1f',
            color='CLV Moyenne',
            color_continuous_scale='Greens'
        )
        fig_clv.update_xaxes(title_text="CLV Moyenne (£)")
        fig_clv.update_yaxes(title_text="")
        st.plotly_chart(style_plot(fig_clv, "💵 CLV Moyenne par Segment"), use_container_width=True)
    
    with col2:
        clv_total_data = rfm_table[['Segment', 'CA_Total']].copy()
        clv_total_data = clv_total_data.sort_values('CA_Total', ascending=True)
        clv_total_data.columns = ['Segment', 'CLV Totale']
        
        fig_clv_total = px.bar(
            clv_total_data,
            x='CLV Totale',
            y='Segment',
            orientation='h',
            text_auto=',.0f',
            color='CLV Totale',
            color_continuous_scale='Blues'
        )
        fig_clv_total.update_xaxes(title_text="CLV Totale (£)")
        fig_clv_total.update_yaxes(title_text="")
        st.plotly_chart(style_plot(fig_clv_total, "💰 Contribution Totale au CA"), use_container_width=True)

    # ============ ACTIONS RECOMMANDÉES ============
    st.markdown("---")
    st.markdown("### ⚡ Plan d'Action Recommandé")
    
    action_map = {
        "Champions 🏆": {
            "color": "alert-green",
            "title": "🏆 Champions",
            "action": "**Chouchouter** - Programme VIP, accès prioritaire, personal shopping"
        },
        "Loyaux Potentiels 🌱": {
            "color": "alert-green",
            "title": "🌱 Loyaux Potentiels",
            "action": "**Cross-Selling** - Proposer produits complémentaires, bundle deals"
        },
        "Nouveaux Prometteurs 👋": {
            "color": "alert-yellow",
            "title": "👋 Nouveaux",
            "action": "**Welcome Program** - Follow-up personnalisé, remise fidélité, nurturing"
        },
        "À Risque ⚠️": {
            "color": "alert-yellow",
            "title": "⚠️ À Risque",
            "action": "**Win-back Campaign** - Offre spéciale (10-15%), raison absence, reconquête"
        },
        "Hibernants 💤": {
            "color": "alert-red",
            "title": "💤 Hibernants",
            "action": "**Nettoyage/Réactivation** - Campagne de réactivation légère ou suppression BDD"
        }
    }
    
    cols = st.columns(len(action_map))
    for i, (segment, action_info) in enumerate(action_map.items()):
        with cols[i % len(cols)]:
            st.markdown(
                f'<div class="custom-alert {action_info["color"]}"><strong>{action_info["title"]}</strong><br>{action_info["action"]}</div>',
                unsafe_allow_html=True
            )

    # ============ STATISTIQUES DÉTAILLÉES ============
    st.markdown("---")
    st.markdown("### 📋 Statistiques Détaillées par Segment")
    
    for segment in rfm_df['Segment_Label'].unique():
        with st.expander(f"Détails : {segment}"):
            seg_data = rfm_df[rfm_df['Segment_Label'] == segment]
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Clients", f"{len(seg_data):,}")
            col2.metric("CA Total", f"{seg_data['Monetary'].sum():,.0f} £")
            col3.metric("Panier Moyen", f"{seg_data['Monetary'].mean():.1f} £")
            col4.metric("Valeur Parc", f"{seg_data['Monetary'].sum():,.0f} £")
            
            col5, col6, col7 = st.columns(3)
            col5.metric("Récence Moy", f"{seg_data['Recency'].mean():.0f} jours")
            col6.metric("Fréquence Moy", f"{seg_data['Frequency'].mean():.1f} achats")
            col7.metric("% du Total", f"{len(seg_data)/len(rfm_df)*100:.1f}%")
