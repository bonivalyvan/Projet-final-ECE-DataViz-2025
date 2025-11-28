import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime

from utils.visualization import load_css
from utils.data_loader import sidebar_filters, date_range, selected_countries, return_mode
from utils.rfm_calculator import compute_rfm

load_css()
df, analysis_date = sidebar_filters()

if df is not None:
    st.title("📥 Plan d'Action & Exports")
    rfm_df = compute_rfm(df, analysis_date)

    st.markdown("""
    Cette page vous permet de **créer des listes activables** pour vos outils CRM, d'emailing ou d'automation.
    Chaque export inclut les **CustomerID**, **segment RFM**, et **métriques clés** pour piloter vos campagnes.
    """)

    # ============ SÉLECTION DES SEGMENTS ============
    st.markdown("### 🎯 Sélectionner les Segments à Exporter")
    
    all_segments = sorted(rfm_df['Segment_Label'].unique().tolist())
    
    # Prédéfinitions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏆 Champions", key="btn_champs"):
            st.session_state.selected_segs = ['Champions 🏆']
    
    with col2:
        if st.button("⚠️ À Risque", key="btn_risk"):
            st.session_state.selected_segs = ['À Risque ⚠️']
    
    with col3:
        if st.button("✅ Tous", key="btn_all"):
            st.session_state.selected_segs = all_segments

    # Sélection manuelle
    target_segs = st.multiselect(
        "Ou sélectionner manuellement",
        options=all_segments,
        default=['Champions 🏆', 'À Risque ⚠️'] if 'selected_segs' not in st.session_state else st.session_state.get('selected_segs', []),
        help="Choisissez un ou plusieurs segments pour exporter les listes"
    )

    if target_segs:
        export_df = rfm_df[rfm_df['Segment_Label'].isin(target_segs)].copy()
        
        # ============ STATISTIQUES ============
        st.markdown("---")
        st.markdown("### 📊 Résumé de l'Export")
        
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric(
            "👥 Clients à Contacter",
            f"{len(export_df):,}",
            help=f"{len(export_df)/len(rfm_df)*100:.1f}% de la base"
        )
        
        col2.metric(
            "💰 CA Potentiel",
            f"{export_df['Monetary'].sum():,.0f} £",
            help=f"{export_df['Monetary'].sum()/rfm_df['Monetary'].sum()*100:.1f}% du CA total"
        )
        
        col3.metric(
            "📈 Panier Moyen",
            f"{export_df['Monetary'].mean():.1f} £",
            help="Valeur moyenne par client du segment"
        )
        
        col4.metric(
            "🔄 Fréquence Moy.",
            f"{export_df['Frequency'].mean():.1f}",
            help="Nombre moyen d'achats par client"
        )

        # ============ PRÉVISUALISATION ============
        st.markdown("---")
        st.markdown("### 👁️ Prévisualisation des Données")
        
        # Préparer les colonnes pour l'export
        export_display = export_df[[
            'CustomerID', 'Segment_Label', 'Monetary', 'Frequency', 'Recency', 'R_Score', 'F_Score', 'M_Score'
        ]].copy()
        export_display.columns = ['Customer ID', 'Segment', 'CLV (£)', 'Fréquence', 'Récence (j)', 'R Score', 'F Score', 'M Score']
        
        # Formater pour affichage
        display_cols = export_display.head(20).copy()
        display_cols['CLV (£)'] = display_cols['CLV (£)'].apply(lambda x: f"{x:.1f}")
        display_cols['Fréquence'] = display_cols['Fréquence'].apply(lambda x: f"{int(x)}")
        display_cols['Récence (j)'] = display_cols['Récence (j)'].apply(lambda x: f"{int(x)}")
        
        st.dataframe(display_cols, use_container_width=True, hide_index=True)
        
        if len(export_df) > 20:
            st.caption(f"Affichage des 20 premiers clients. Total : {len(export_df):,} clients")
        
                # ============ VUE GRAPHIQUE EXPORTABLE ============
        st.markdown("---")
        st.markdown("### 📊 Vue Graphique des Segments (Exportable en PNG)")

        # Exemple : répartition des segments dans la liste activable
        seg_counts = export_df['Segment_Label'].value_counts().reset_index()
        seg_counts.columns = ['Segment', 'Nombre de clients']

        import plotly.express as px

        fig_seg_export = px.bar(
            seg_counts,
            x='Segment',
            y='Nombre de clients',
            text='Nombre de clients',
            title='Répartition des segments dans la liste activable'
        )
        fig_seg_export.update_traces(textposition='outside')

        # Activation du bouton de téléchargement PNG dans la toolbar Plotly
        config = {
            "toImageButtonOptions": {
                "format": "png",
                "filename": f"segments_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "height": 600,
                "width": 1000,
                "scale": 2
            },
            "displaylogo": False
        }

        st.plotly_chart(fig_seg_export, use_container_width=True, config=config)

        # ============ TÉLÉCHARGEMENTS ============
        st.markdown("---")
        st.markdown("### 📥 Téléchargements")
        
        # CSV Export
        csv_data = export_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Télécharger CSV (Liste Complète)",
            data=csv_data,
            file_name=f"CRM_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            help="Fichier à importer dans votre CRM ou outil d'emailing (Mailchimp, Sendinblue, etc.)"
        )
        
        # Excel Export (si openpyxl disponible)
        try:
            import openpyxl
            from openpyxl.utils import get_column_letter
            
            # Créer un fichier Excel avec styles
            from io import BytesIO
            
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                export_display.to_excel(writer, index=False, sheet_name='Clients')
                
                # Format des colonnes
                workbook = writer.book
                worksheet = writer.sheets['Clients']
                for idx, column in enumerate(export_display.columns, 1):
                    worksheet.column_dimensions[get_column_letter(idx)].width = 18
            
            excel_buffer.seek(0)
            st.download_button(
                label="📊 Télécharger Excel",
                data=excel_buffer.getvalue(),
                file_name=f"CRM_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.ms-excel"
            )
        except ImportError:
            st.info("Excel non disponible. Utilisez le CSV.")

        # ============ GUIDES D'UTILISATION ============
        st.markdown("---")
        st.markdown("### 📋 Guides d'Utilisation par Segment")
        
        guides = {
            "Champions 🏆": {
                "objectives": "Conserver, augmenter panier moyen, transformer en ambassadeurs",
                "actions": [
                    "✅ Accès VIP à nos nouveautés (early access)",
                    "✅ Programme de parrainage (bonus pour chaque ami recruté)",
                    "✅ Remises progressives ou points fidélité",
                    "✅ Personal shopping, consultation privée"
                ],
                "channels": "Email personnalisé, SMS, téléphone",
                "frequency": "Mensuel ou bi-mensuel"
            },
            "À Risque ⚠️": {
                "objectives": "Réactiver rapidement, comprendre les raisons du départ",
                "actions": [
                    "🔥 Win-back campaign avec offre spéciale (10-15% remise)",
                    "🔥 Sondage de satisfaction : pourquoi absent?",
                    "🔥 Exclusivité temporaire (offre réservée aux clients à risque)",
                    "🔥 Nouvelle collection / produit pertinent"
                ],
                "channels": "Email, SMS, Retargeting display",
                "frequency": "Immédiat puis hebdomadaire pendant 4-6 semaines"
            },
            "Hibernants 💤": {
                "objectives": "Coût faible, tester réactivation avant suppression",
                "actions": [
                    "⚪ Email de réactivation simple (sans offre coûteuse)",
                    "⚪ Après 30j sans réponse → Supprimer de la BDD",
                    "⚪ Alternative : Les conserver mais segmenter à part (coûts BDD/spam)"
                ],
                "channels": "Email automatisé",
                "frequency": "Unique"
            },
            "Loyaux Potentiels 🌱": {
                "objectives": "Cross-selling, développement du panier moyen",
                "actions": [
                    "💚 Bundle de produits complémentaires",
                    "💚 Offre multi-achat (ex: 2 produits = -10%)",
                    "💚 Contenu éducatif (utilisation, combinaisons)",
                    "💚 Réductions limitées pour créer urgence"
                ],
                "channels": "Email, newsletter, contenu digital",
                "frequency": "Bi-mensuel"
            },
            "Nouveaux Prometteurs 👋": {
                "objectives": "Fixer le client, transformer en régulier",
                "actions": [
                    "🌟 Welcome email + guide produit",
                    "🌟 Remise fidélité (5-10%) sur 2e achat",
                    "🌟 Quiz/sondage pour comprendre besoins",
                    "🌟 Suivi post-achat (satisfaction, conseils)"
                ],
                "channels": "Email automation, SMS",
                "frequency": "J+1, J+7, J+30"
            }
        }
        
        for segment in target_segs:
            if segment in guides:
                with st.expander(f"📖 Guide pour {segment}"):
                    guide = guides[segment]
                    st.markdown(f"**Objectifs** : {guide['objectives']}")
                    st.markdown("**Actions Recommandées** :")
                    for action in guide['actions']:
                        st.markdown(f"- {action}")
                    st.markdown(f"**Canaux** : {guide['channels']}")
                    st.markdown(f"**Fréquence de Contact** : {guide['frequency']}")

        # ============ FILTRES APPLIQUÉS ============
        st.markdown("---")
        st.markdown("### ℹ️ Contexte de l'Export")
        
        # Formater les filtres avec valeurs par défaut
        periode_text = f"{date_range[0].strftime('%d/%m/%Y')} → {date_range[1].strftime('%d/%m/%Y')}" if date_range else "Toute période"
        pays_text = ', '.join(selected_countries) if selected_countries else "Tous les pays"
        retours_text = 'Exclus' if return_mode == 'Exclure les retours' else ('Uniquement' if return_mode == 'Uniquement les retours' else 'Inclus')
        
        with st.container():
            st.markdown(f"""
**Filtres Appliqués** :
- 📅 **Période** : {periode_text}
- 🌍 **Pays** : {pays_text}
- 📦 **Retours** : {retours_text}

**Recommandations d'Utilisation** :
1. ✅ Tester sur petit échantillon (1000 clients) avant déploiement massif
2. ✅ Segmenter vos messages par segment RFM
3. ✅ Mesurer KPIs (taux d'ouverture, conversion, ROI)
4. ✅ Revenir ici chaque mois pour mettre à jour les listes
            """)


    else:
        st.info("📌 Sélectionnez au moins un segment pour afficher les données et créer un export.")
