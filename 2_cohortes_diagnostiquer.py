import streamlit as st
import sys
import os
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from utils.visualization import load_css, style_plot
from utils.data_loader import sidebar_filters
from utils.cohort_calculator import compute_cohorts

load_css()
df, _ = sidebar_filters()

if df is not None:
    st.title("📊 Analyse de Rétention par Cohortes")

    # ============ GUIDE DES COHORTES ============
    with st.expander("ℹ️ Comprendre la Heatmap de Rétention", expanded=False):
        st.markdown("""
        ### Qu'est-ce qu'une Cohorte?
        Une cohorte = groupe de clients ayant effectué leur **première achat le même mois**.
        
        ### Qu'est-ce que la Rétention?
        Le **% de clients qui reviennent acheter** au mois suivant, puis au mois d'après, etc.
        
        ### Comment Lire la Heatmap?
        
        | Axe | Signification |
        |-----|---------------|
        | **Vertical (Lignes)** | Mois d'acquisition (première commande) |
        | **Horizontal (Colonnes)** | Nombre de mois écoulés depuis l'acquisition (M+0, M+1, M+2, ...) |
        | **Couleur (Intensité)** | % de rétention (Purple foncé = Bon, Clair = Mauvais) |
        
        ### Exemple Pratique
        **Cohorte 2009-12** (clients acquis déc 2009):
        - M+0 = 100% (par définition, c'est leur premier achat)
        - M+1 = 45% (45% ont acheté à nouveau en janv 2010)
        - M+3 = 25% (25% ont acheté à nouveau en mars 2010)
        - **Insight** : Cette cohorte "décroche" rapidement (chute de 45% à 25%) → Mauvaise fidélisation
        
        ### Patterns à Observer
        - ⚠️ **Colonnes claires** : Mauvaise rétention globale (problème produit/service?)
        - 🏆 **Lignes foncées** : Cohorte fidèle (bon timing d'acquisition?)
        - 📉 **Décroissance progressive** : Normal, mais vitesse importante
        """)

    # ============ HEATMAP DE RÉTENTION ============
    st.markdown("### 🔥 HEATMAP de Rétention")
    
    retention_matrix, cohort_size = compute_cohorts(df)

    fig_cohort = go.Figure(data=go.Heatmap(
        z=retention_matrix.values,
        x=retention_matrix.columns,
        y=retention_matrix.index.astype(str),
        colorscale='Purples',
        text=retention_matrix.applymap(lambda x: f"{x:.0%}" if not pd.isna(x) else "").values,
        texttemplate="%{text}",
        xgap=2,
        ygap=2,
        colorbar=dict(title="Rétention %"),
        hovertemplate="Cohorte: %{y}<br>M+%{x}<br>Rétention: %{z:.0%}<extra></extra>"
    ))
    
    fig_cohort.update_layout(
        height=700,
        yaxis_autorange="reversed",
        xaxis_title="Mois depuis Acquisition",
        yaxis_title="Cohorte",
        title_text="📊 Heatmap de Rétention par Cohorte d'Acquisition"
    )
    
    st.plotly_chart(style_plot(fig_cohort), use_container_width=True)

    # ============ COURBES DE CA PAR ÂGE DE COHORTE ============
    st.markdown("---")
    st.markdown("### 💰 Revenu CA par Âge de Cohorte (Densité)")
    
    # Calculer CA par cohorte et âge
    df_ca = df[['Customer ID', 'InvoiceDate', 'TotalPrice']].copy()
    df_ca['OrderMonth'] = df_ca['InvoiceDate'].dt.to_period('M')
    df_ca['CohortMonth'] = df_ca.groupby('Customer ID')['InvoiceDate'].transform('min').dt.to_period('M')
    df_ca['CohortAge'] = (df_ca['OrderMonth'] - df_ca['CohortMonth']).apply(lambda x: x.n)
    
    # CA par âge de cohorte (moyenné)
    ca_by_age = df_ca.groupby('CohortAge')['TotalPrice'].agg(['sum', 'mean', 'count']).reset_index()
    ca_by_age = ca_by_age[ca_by_age['CohortAge'] <= 12]  # Limiter à M+12
    
    if not ca_by_age.empty:
        fig_ca_age = px.bar(
            ca_by_age,
            x='CohortAge',
            y='mean',
            color='count',
            labels={'CohortAge': 'Âge de Cohorte (Mois)', 'mean': 'CA Moyen par Transaction (£)', 'count': 'Nombre de Transactions'},
            title='💰 CA Moyen par Âge de Cohorte',
            color_continuous_scale='Viridis'
        )
        fig_ca_age.update_xaxes(title_text="Mois depuis Acquisition (M+0 à M+12)")
        fig_ca_age.update_yaxes(title_text="CA Moyen par Transaction (£)")
        fig_ca_age.update_layout(height=400)
        
        st.plotly_chart(style_plot(fig_ca_age), use_container_width=True)
        
        st.markdown("""
        💡 **Insights CA par Âge** :
        - **M+0 vs M+1** : Le panier moyen chute-t-il? (Signal de mauvaise satisfaction?)
        - **M+2 à M+6** : Plateau ou décroissance? (Fidèles vs Churn)
        - **Couleur (Nombre transactions)** : Indique le volume à chaque âge
        - **Utilité** : Identifier quel âge génère le moins de CA pour cibler onboarding
        """)

    # ============ COURBES DE RÉTENTION MOYENNE ============
    st.markdown("---")
    st.markdown("### 📈 Taux de Rétention Moyen par Période")
    
    avg_retention = {}
    for col in retention_matrix.columns:
        if col <= 12:  # Jusqu'à M+12
            avg_ret = retention_matrix[col].mean()
            if not pd.isna(avg_ret):
                avg_retention[f"M+{col}"] = avg_ret
    
    if avg_retention:
        df_avg = pd.DataFrame(list(avg_retention.items()), columns=['Période', 'Rétention Moyenne'])
        
        fig_avg = px.line(
            df_avg,
            x='Période',
            y='Rétention Moyenne',
            markers=True,
            line_shape='spline',
            color_discrete_sequence=['#4F46E5']
        )
        fig_avg.update_yaxes(tickformat='.0%', title_text="Taux de Rétention")
        fig_avg.update_xaxes(title_text="Période")
        fig_avg.update_traces(line=dict(width=3), marker=dict(size=8))
        
        st.plotly_chart(style_plot(fig_avg, "📈 Rétention Moyenne Toutes Cohortes"), use_container_width=True)
        
        st.markdown("""
        💡 **Insights Clés** :
        - Quelle est la pente du déclin de rétention (M+1 vs M+3 vs M+6)?
        - Y a-t-il un palier (stagnation du taux de départ)?
        - Est-ce que la rétention M+1 est inférieure à 40%? (Problème d'onboarding potentiel)
        """)

    # ============ FOCUS SUR UNE COHORTE ============
    st.markdown("---")
    st.markdown("### 🔍 Analyse d'une Cohorte Spécifique")
    
    cohorts_list = retention_matrix.index.astype(str).tolist()
    selected_cohort = st.selectbox(
        "Sélectionner une cohorte pour analyser",
        options=cohorts_list,
        index=len(cohorts_list) - 1 if len(cohorts_list) > 0 else 0,
        help="Affiche la courbe de rétention d'une cohorte particulière"
    )
    
    if selected_cohort in retention_matrix.index.astype(str).values:
        cohort_retention = retention_matrix.loc[selected_cohort]
        cohort_retention = cohort_retention.dropna()
        
        if not cohort_retention.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    f"Taille de la Cohorte {selected_cohort}",
                    f"{int(cohort_size.get(selected_cohort, 0)):,} clients",
                    help="Nombre de clients acquis ce mois-là"
                )
            
            with col2:
                first_month_ret = cohort_retention.iloc[0] if len(cohort_retention) > 0 else 0
                st.metric(
                    "Rétention M+1",
                    f"{first_month_ret:.0%}",
                    help=f"% des {int(cohort_size.get(selected_cohort, 0)):,} clients qui ont acheté le mois suivant"
                )
        
        # Graphique de la cohorte sélectionnée (EN DEHORS DES COLONNES)
        if not cohort_retention.empty:
            cohort_ret_df = pd.DataFrame({
                'Période': [f"M+{i}" for i in cohort_retention.index],
                'Rétention': cohort_retention.values
            })
            
            fig_cohort_detail = px.bar(
                cohort_ret_df,
                x='Période',
                y='Rétention',
                color='Rétention',
                color_continuous_scale='Greens',
                text_auto='.0%'
            )
            fig_cohort_detail.update_yaxes(tickformat='.0%')
            fig_cohort_detail.update_layout(height=400)
            
            st.plotly_chart(style_plot(fig_cohort_detail, f"📊 Courbe de Rétention Cohorte {selected_cohort}"), 
                           use_container_width=True)
            
            # Analyse textuelle
            ret_m1 = f"{cohort_retention.iloc[0]:.0%}" if len(cohort_retention) > 0 else 'N/A'
            ret_m3 = f"{cohort_retention.iloc[3]:.0%}" if len(cohort_retention) > 3 else 'N/A'
            ret_m6 = f"{cohort_retention.iloc[6]:.0%}" if len(cohort_retention) > 6 else 'N/A'
            
            st.markdown(f"""**Analyse pour {selected_cohort}** :
- Taille initiale : {int(cohort_size.get(selected_cohort, 0)):,} clients
- Rétention M+1 : {ret_m1}
- Rétention M+3 : {ret_m3}
- Rétention M+6 : {ret_m6}""")

    # ============ COMPARAISON PAR TYPE DE CLIENT ============
    st.markdown("---")
    st.markdown("### 🏪 Rétention par Type de Client (B2B vs B2C)")
    
    # Identifier type client selon quantité
    df['ClientType'] = df['Quantity'].apply(lambda x: 'B2B (Grossiste)' if abs(x) > 50 else 'B2C (Détail)')
    
    df_c = df[['Customer ID', 'InvoiceDate', 'ClientType']].drop_duplicates()
    df_c['OrderMonth'] = df_c['InvoiceDate'].dt.to_period('M')
    df_c['CohortMonth'] = df_c.groupby('Customer ID')['InvoiceDate'].transform('min').dt.to_period('M')
    
    # Type client dominant pour chaque client
    client_type_map = df.groupby('Customer ID')['ClientType'].agg(lambda x: x.value_counts().index[0]).reset_index()
    client_type_map.columns = ['Customer ID', 'PrimaryType']
    df_c = df_c.merge(client_type_map, on='Customer ID', how='left')
    
    df_cohort_type = df_c.groupby(['CohortMonth', 'OrderMonth', 'PrimaryType']).agg(
        n_customers=('Customer ID', 'nunique')
    ).reset_index()
    df_cohort_type['PeriodNumber'] = (df_cohort_type.OrderMonth - df_cohort_type.CohortMonth).apply(lambda x: x.n)
    
    retention_by_type = []
    for client_type in df_cohort_type['PrimaryType'].unique():
        df_type = df_cohort_type[df_cohort_type['PrimaryType'] == client_type]
        cohort_pivot = df_type.pivot_table(index='CohortMonth', columns='PeriodNumber', values='n_customers')
        
        if not cohort_pivot.empty and cohort_pivot.shape[1] > 0:
            cohort_size_type = cohort_pivot.iloc[:, 0]
            retention_matrix_type = cohort_pivot.divide(cohort_size_type, axis=0)
            avg_retention = retention_matrix_type.mean(axis=0)
            
            for period, rate in avg_retention.items():
                if period <= 12 and not pd.isna(rate):
                    retention_by_type.append({
                        'Type': client_type,
                        'Période': f"M+{period}",
                        'Rétention': rate
                    })
    
    if retention_by_type:
        df_ret_type = pd.DataFrame(retention_by_type)
        
        fig_ret_type = px.line(
            df_ret_type,
            x='Période',
            y='Rétention',
            color='Type',
            markers=True,
            line_shape='spline'
        )
        fig_ret_type.update_yaxes(tickformat='.0%')
        fig_ret_type.update_layout(height=400)
        
        st.plotly_chart(style_plot(fig_ret_type, "📈 Rétention Moyenne B2B vs B2C"), use_container_width=True)
        
        st.markdown("""
        💡 **Interprétation** :
        - Si la courbe **B2B** est au-dessus → Les grossistes reviennent plus régulièrement
        - Si la courbe **B2C** décroche rapidement → Problème de fidélisation détail (remises, emballage, etc.)
        - **Action** : Adapter la stratégie de rétention par type (B2B = contrats, B2C = programmes fidélité)
        """)
    else:
        st.info("Pas assez de données pour analyser la rétention par type de client.")
