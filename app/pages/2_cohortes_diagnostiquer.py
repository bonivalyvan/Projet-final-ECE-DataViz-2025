import streamlit as st
import sys
import os
import plotly.graph_objects as go
import pandas as pd

from utils.visualization import load_css, style_plot
from utils.data_loader import sidebar_filters
from utils.cohort_calculator import compute_cohorts

load_css()
df, _ = sidebar_filters()

if df is not None:
    st.title("Analyse de Rétention")

    with st.expander("ℹ️ Comprendre la Heatmap de Rétention"):
        st.write("Graphique de rétention : pourcentage de clients revenant acheter mois après mois.")

    retention_matrix, cohort_size = compute_cohorts(df)

    fig_cohort = go.Figure(data=go.Heatmap(
        z=retention_matrix.values, x=retention_matrix.columns, y=retention_matrix.index.astype(str),
        colorscale='Purples', text=retention_matrix.map(lambda x: f"{x:.0%}" if not pd.isna(x) else "").values,
        texttemplate="%{text}", xgap=2, ygap=2
    ))
    fig = style_plot(fig_cohort, "Matrice de Rétention")
    fig.update_layout(height=700, yaxis_autorange="reversed")

    # CORRECTION ICI : width="stretch"
    st.plotly_chart(fig, width="stretch")