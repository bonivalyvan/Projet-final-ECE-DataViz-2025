import streamlit as st

# Theme Colors
COLOR_PRIMARY = "#4F46E5"
BG_COLOR = "#F8FAFC"
TEXT_COLOR = "#1E293B"
SIDEBAR_BG = "#FFFFFF"

def load_css():
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        .stApp {{ background-color: {BG_COLOR}; font-family: 'Inter', sans-serif; color: {TEXT_COLOR}; }}
        
        .block-container {{
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
            max-width: 95% !important;
        }}
        
        section[data-testid="stSidebar"] {{ background-color: {SIDEBAR_BG}; border-right: 1px solid #E2E8F0; }}
        section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] div, section[data-testid="stSidebar"] span {{ 
            color: #1E293B !important; 
        }}
        section[data-testid="stSidebar"] label {{ color: #1E293B !important; }}
        section[data-testid="stSidebar"] input, section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
            background-color: #FFFFFF !important; color: #1E293B !important; border: 1px solid #E2E8F0 !important;
        }}

        div[data-testid="stVerticalBlock"] > div:not([data-testid="stSidebar"]) label {{ color: #1E293B !important; }}
        div.stNumberInput input {{ background-color: #FFFFFF !important; color: #000000 !important; border: 1px solid #E2E8F0 !important; }}
        
        div.stButton > button, div.stDownloadButton > button {{
            background-color: {COLOR_PRIMARY} !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 0.5rem 1rem !important;
            transition: all 0.3s ease !important;
        }}
        div.stButton > button:hover, div.stDownloadButton > button:hover {{
            background-color: #4338CA !important;
            box-shadow: 0 4px 6px rgba(79, 70, 229, 0.4) !important;
        }}
        
        div[data-testid="stDataFrame"] {{ border: 1px solid #E2E8F0; border-radius: 8px; }}
        div[data-testid="stDataFrame"] th {{ background-color: #F1F5F9 !important; color: #1E293B !important; font-weight: 600 !important; }}

        div[data-testid="stMetric"] {{
            background-color: #FFFFFF; padding: 15px; border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 4px solid {COLOR_PRIMARY};
        }}

        .custom-alert {{ padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; font-weight: 500; }}
        .alert-green {{ background-color: #ECFDF5; color: #065F46; border: 1px solid #A7F3D0; }}
        .alert-yellow {{ background-color: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; }}
        .alert-red {{ background-color: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; }}
    </style>
""", unsafe_allow_html=True)


def style_plot(fig, title=""):
    """applique le style uniforme aux graphiques plotly"""
    fig.update_layout(
        template="plotly_white",
        title=dict(text=title, font=dict(size=18, color="#1E293B", family="Inter")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1E293B", family="Inter"),
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(showgrid=False, color="#1E293B"),
        yaxis=dict(showgrid=True, gridcolor="#E2E8F0", color="#1E293B"),
        hoverlabel=dict(bgcolor="white", font_size=14, font_family="Inter")
    )
    return fig