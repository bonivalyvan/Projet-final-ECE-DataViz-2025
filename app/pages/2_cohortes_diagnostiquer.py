import streamlit as st

st.set_page_config(
    page_title="Cohortes",
    page_icon="chart_with_upwards_trend",
    layout="wide"
)
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.cohort_calculator import compute_cohorts, compute_clv_empirique
from utils.visualization import style_plot
from utils.data_loader import sidebar_filters

df, _ = sidebar_filters()

if df is not None:
    st.title("Diagnostic des Cohortes")
    
    st.markdown("""
        ### Comprendre la rétention
        L'analyse de cohorte permet de suivre le comportement des clients dans le temps.
        
        Exemple : Si la cohorte 2010-01 affiche 45% à M+1, cela signifie que 45% des clients 
        acquis en janvier 2010 ont fait un nouvel achat en février 2010.
        """)

    # heatmap de retention
    retention_matrix, cohort_size = compute_cohorts(df)
    fig_cohort = go.Figure(data=go.Heatmap(
        z=retention_matrix.values, 
        x=retention_matrix.columns, 
        y=retention_matrix.index.astype(str),
        colorscale='RdYlGn_r', 
        text=retention_matrix.applymap(lambda x: f"{x:.0%}" if not pd.isna(x) else "").values,
        texttemplate="%{text}", 
        xgap=2, 
        ygap=2,
        colorbar=dict(title="Rétention")
    ))
    fig = style_plot(fig_cohort, "Matrice de Rétention par Cohorte d'Acquisition")
    fig.update_layout(height=700, yaxis_autorange="reversed")
    fig.update_xaxes(title="Mois depuis l'acquisition")
    fig.update_yaxes(title="Cohorte")
    st.plotly_chart(fig, use_container_width=True)

    # correlation retention type client - ajout pour comparer b2b vs b2c
    st.markdown("---")
    st.subheader("Corrélation Rétention et Type Client : Grossiste vs Détail")
    
    # definir le type de client selon quantite
    df['ClientType'] = df['Quantity'].apply(lambda x: 'grossiste b2b' if abs(x) > 50 else 'detail b2c')
    
    # calculer la retention par type de client
    df_c = df[['Customer ID', 'InvoiceDate', 'ClientType']].drop_duplicates()
    df_c['OrderMonth'] = df_c['InvoiceDate'].dt.to_period('M')
    df_c['CohortMonth'] = df_c.groupby('Customer ID')['InvoiceDate'].transform('min').dt.to_period('M')
    
    # type client principal pour chaque client
    client_type_main = df.groupby('Customer ID')['ClientType'].agg(lambda x: x.value_counts().index[0]).reset_index()
    client_type_main.columns = ['Customer ID', 'MainClientType']
    df_c = df_c.merge(client_type_main, on='Customer ID', how='left')
    
    df_cohort_type = df_c.groupby(['CohortMonth', 'OrderMonth', 'MainClientType']).agg(
        n_customers=('Customer ID', 'nunique')
    ).reset_index()
    df_cohort_type['PeriodNumber'] = (df_cohort_type.OrderMonth - df_cohort_type.CohortMonth).apply(lambda x: x.n)
    
    # calcul taux retention moyens par type
    retention_by_type = []
    for client_type in df_cohort_type['MainClientType'].unique():
        df_type = df_cohort_type[df_cohort_type['MainClientType'] == client_type]
        cohort_pivot = df_type.pivot_table(index='CohortMonth', columns='PeriodNumber', values='n_customers')
        if not cohort_pivot.empty and cohort_pivot.shape[1] > 0:
            cohort_size = cohort_pivot.iloc[:, 0]
            retention_matrix_type = cohort_pivot.divide(cohort_size, axis=0)
            avg_retention = retention_matrix_type.mean(axis=0)
            for period, rate in avg_retention.items():
                if period <= 12:
                    retention_by_type.append({
                        'type': client_type,
                        'mois': f"m+{period}",
                        'retention': rate
                    })
    
    if retention_by_type:
        df_ret_type = pd.DataFrame(retention_by_type)
        fig_ret_type = px.line(df_ret_type, x='mois', y='retention', color='type',
                               markers=True, line_shape='spline',
                               color_discrete_map={'grossiste b2b': '#4F46E5', 'detail b2c': '#10B981'})
        fig_ret_type.update_layout(yaxis_tickformat='.0%')
        st.plotly_chart(style_plot(fig_ret_type, "Taux de Rétention Moyen : Grossistes vs Détail"), use_container_width=True)
        
        st.markdown("""
        Interprétation : Si la courbe grossiste est au-dessus, cela signifie que les clients B2B reviennent plus souvent acheter.
        Si la courbe détail décroche rapidement, nous devons investir dans des programmes de fidélisation B2C.
        """)
    else:
        st.info("Pas assez de données pour calculer la corrélation rétention/type client.")

    # clv empirique par cohorte - ajout pour avoir la vraie valeur historique
    st.markdown("---")
    st.subheader("CLV Empirique par Cohorte")
    
    clv_cohort = compute_clv_empirique(df)
    clv_cohort['Cohorte'] = clv_cohort['Cohorte'].astype(str)
    
    fig_clv = px.bar(clv_cohort, x='Cohorte', y='CLV Empirique', 
                    text_auto='.1f', color='CLV Empirique', color_continuous_scale='RdYlGn_r')
    fig_clv.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(style_plot(fig_clv, "CLV Empirique Moyenne par Cohorte"), use_container_width=True)
    
    st.dataframe(clv_cohort, use_container_width=True)
    
    st.markdown("""
    La CLV empirique représente la valeur réelle moyenne générée par chaque cohorte.
    Les cohortes anciennes ont une CLV plus élevée car elles ont eu plus de temps pour générer du CA.
    Comparer avec la CLV théorique (page scénarios) pour valider les hypothèses.
    """)