import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# Palette de couleurs
COLOR_PRIMARY = "#4F46E5"
COLOR_SUCCESS = "#10B981"
COLOR_WARNING = "#F59E0B"
COLOR_DANGER = "#EF4444"
BG_COLOR = "#F3F4F6"
SIDEBAR_BG = "#0F172A"
TEXT_COLOR = "#1E293B"
LIGHT_GRAY = "#E2E8F0"


def load_css():
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

            /* --- GLOBAL --- */
            .stApp {{ 
                background-color: {BG_COLOR}; 
                font-family: 'Inter', sans-serif; 
                color: {TEXT_COLOR};
            }}
            
            /* Amélioration accessibilité : augmenter tailles de fonts */
            body {{ font-size: 16px; line-height: 1.6; }}
            h1 {{ font-size: 2.5rem !important; margin-bottom: 1.5rem !important; }}
            h2 {{ font-size: 2rem !important; margin-bottom: 1rem !important; }}
            h3 {{ font-size: 1.5rem !important; }}
            p {{ font-size: 1rem; }}

            /* --- SIDEBAR --- */
            section[data-testid="stSidebar"] {{ 
                background-color: {SIDEBAR_BG}; 
            }}
            section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, 
            section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] p,
            section[data-testid="stSidebar"] div, section[data-testid="stSidebar"] span {{ 
                color: #F1F5F9 !important; 
            }}
            section[data-testid="stSidebar"] label {{ 
                color: #F8FAFC !important; 
                font-weight: 500;
                font-size: 14px;
            }}

            /* --- BOUTONS --- */
            div.stButton > button, div.stDownloadButton > button {{
                background-color: {COLOR_PRIMARY} !important;
                color: #FFFFFF !important;
                border: none !important;
                border-radius: 8px !important;
                font-weight: 600 !important;
                padding: 0.75rem 1.5rem !important;
                font-size: 15px !important;
                transition: all 0.3s ease !important;
            }}
            div.stButton > button:hover, div.stDownloadButton > button:hover {{
                background-color: #4338CA !important;
                box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4) !important;
                transform: translateY(-2px) !important;
            }}

            /* --- CARTES METRICS --- */
            div[data-testid="stMetric"] {{
                background-color: #FFFFFF; 
                padding: 20px; 
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08); 
                border-left: 5px solid {COLOR_PRIMARY};
            }}
            div[data-testid="stMetric"] label {{ 
                color: #64748B !important; 
                font-size: 13px !important;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{ 
                color: #0F172A !important; 
                font-size: 32px !important;
                font-weight: 700;
            }}
            div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {{ 
                font-size: 14px !important;
                font-weight: 600;
            }}

            /* --- DATAFRAME --- */
            div[data-testid="stDataFrame"] {{ 
                border: 1px solid {LIGHT_GRAY}; 
                border-radius: 8px;
                overflow: hidden;
            }}
            div[data-testid="stDataFrame"] th {{ 
                background-color: #F1F5F9 !important; 
                color: #1E293B !important; 
                font-weight: 700 !important;
                font-size: 14px !important;
            }}

            /* --- ALERTES --- */
            .custom-alert {{ 
                padding: 1.25rem; 
                border-radius: 0.75rem; 
                margin-bottom: 1rem; 
                font-weight: 500;
                font-size: 15px;
            }}
            .alert-green {{ 
                background-color: #ECFDF5; 
                color: #065F46; 
                border: 1px solid #A7F3D0; 
            }}
            .alert-yellow {{ 
                background-color: #FFFBEB; 
                color: #92400E; 
                border: 1px solid #FDE68A; 
            }}
            .alert-red {{ 
                background-color: #FEF2F2; 
                color: #991B1B; 
                border: 1px solid #FECACA; 
            }}
            
            /* --- BADGE --- */
            .badge {{
                display: inline-block;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-size: 13px;
                font-weight: 600;
                margin-right: 0.5rem;
                margin-bottom: 0.5rem;
            }}
            .badge-excluded {{
                background-color: #FEE2E2;
                color: #991B1B;
                border: 1px solid #FECACA;
            }}
            .badge-included {{
                background-color: #DBEAFE;
                color: #1E40AF;
                border: 1px solid #93C5FD;
            }}
        </style>
    """, unsafe_allow_html=True)


def style_plot(fig, title="", height=None, show_grid=True):
    """
    Applique le style cohérent à tous les graphiques Plotly
    
    Args:
        fig: Figure Plotly
        title: Titre du graphique
        height: Hauteur personnalisée (optionnel)
        show_grid: Afficher la grille (défaut: True)
    
    Returns:
        Figure stylisée
    """
    layout_config = dict(
        template="plotly_white",
        title=dict(
            text=title, 
            font=dict(size=20, color="#1E293B", family="Inter"),
            x=0.5,
            xanchor='center'
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1E293B", family="Inter", size=13),
        margin=dict(l=50, r=30, t=70, b=50),
        xaxis=dict(
            showgrid=show_grid,
            gridcolor=LIGHT_GRAY,
            color="#1E293B", 
            title_font=dict(color="#1E293B", size=14),
            tickfont=dict(color="#1E293B", size=12)
        ),
        yaxis=dict(
            showgrid=show_grid,
            gridcolor=LIGHT_GRAY,
            color="#1E293B", 
            title_font=dict(color="#1E293B", size=14),
            tickfont=dict(color="#1E293B", size=12)
        ),
        legend=dict(
            font=dict(color="#1E293B", size=12),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#E2E8F0",
            borderwidth=1
        ),
        hovermode='x unified'
    )
    
    if height:
        layout_config['height'] = height
    
    fig.update_layout(**layout_config)
    return fig


def get_filter_badge_html(return_mode):
    """
    Génère un badge HTML pour afficher l'état des filtres retours
    """
    if return_mode == "Exclure les retours":
        return '<span class="badge badge-excluded">🚫 Retours Exclus</span>'
    elif return_mode == "Uniquement les retours":
        return '<span class="badge badge-excluded">📦 Retours Uniquement</span>'
    else:
        return '<span class="badge badge-included">✅ Retours Inclus</span>'


def display_active_filters(date_range, countries, return_mode):
    """
    Affiche un résumé visuel des filtres actifs
    """
    cols = st.columns(4)
    
    with cols[0]:
        st.metric("📅 Période", f"{date_range[0].strftime('%d/%m/%y')} à {date_range[1].strftime('%d/%m/%y')}")
    
    with cols[1]:
        st.metric("🌍 Pays", f"{len(countries)} sélectionné(s)")
    
    with cols[2]:
        badge = "✅ Inclus" if return_mode == "Inclure tout" else ("❌ Exclus" if return_mode == "Exclure les retours" else "📦 Uniquement")
        st.metric("📦 Retours", badge)
    
    with cols[3]:
        st.metric("🔄 Filtres", "Actifs", help="Cliquez pour modifier dans la barre latérale")


def add_export_button(fig, filename, button_label="📥 Télécharger PNG"):
    """
    Ajoute un bouton de téléchargement pour exporter un graphique en PNG
    """
    png_bytes = fig.to_image(format="png")
    st.download_button(
        label=button_label,
        data=png_bytes,
        file_name=f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
        mime="image/png"
    )