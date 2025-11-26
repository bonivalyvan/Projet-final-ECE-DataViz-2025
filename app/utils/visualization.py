import streamlit as st
import plotly.graph_objects as go

# Palette de couleurs
COLOR_PRIMARY = "#4F46E5"
BG_COLOR = "#F3F4F6"
SIDEBAR_BG = "#0F172A"
TEXT_COLOR = "#1E293B"


def load_css():
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

            /* --- GLOBAL --- */
            .stApp {{ background-color: {BG_COLOR}; font-family: 'Inter', sans-serif; color: {TEXT_COLOR}; }}

            /* --- SIDEBAR --- */
            section[data-testid="stSidebar"] {{ background-color: {SIDEBAR_BG}; }}
            section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, 
            section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] p,
            section[data-testid="stSidebar"] div, section[data-testid="stSidebar"] span {{ 
                color: #F1F5F9 !important; 
            }}
            section[data-testid="stSidebar"] label {{ color: #F8FAFC !important; }}

            /* --- BOUTONS --- */
            div.stButton > button, div.stDownloadButton > button {{
                background-color: {COLOR_PRIMARY} !important;
                color: #FFFFFF !important;
                border: none !important;
                border-radius: 8px !important;
                font-weight: 600 !important;
            }}

            /* --- CARTES METRICS (Le correctif est ici 👇) --- */
            div[data-testid="stMetric"] {{
                background-color: #FFFFFF; 
                padding: 15px; 
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
                border-left: 4px solid {COLOR_PRIMARY};
            }}
            /* Force la couleur du petit label (ex: 'Clients Actifs') en gris foncé */
            div[data-testid="stMetric"] label {{ color: #64748B !important; }}

            /* Force la couleur de la valeur (ex: '3,971') en noir/bleu nuit */
            div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{ color: #0F172A !important; }}

            /* --- ALERTES --- */
            .custom-alert {{ padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; font-weight: 500; }}
            .alert-green {{ background-color: #ECFDF5; color: #065F46; border: 1px solid #A7F3D0; }}
            .alert-yellow {{ background-color: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; }}
            .alert-red {{ background-color: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; }}
        </style>
    """, unsafe_allow_html=True)


def style_plot(fig, title=""):
    fig.update_layout(
        template="plotly_white",
        title=dict(text=title, font=dict(size=18, color="#1E293B", family="Inter")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1E293B", family="Inter"),
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(showgrid=False, color="#1E293B", title_font=dict(color="#1E293B"), tickfont=dict(color="#1E293B")),
        yaxis=dict(showgrid=True, gridcolor="#E2E8F0", color="#1E293B", title_font=dict(color="#1E293B"),
                   tickfont=dict(color="#1E293B")),
        legend=dict(font=dict(color="#1E293B"), bgcolor="rgba(255,255,255,0.5)"),
    )
    return fig