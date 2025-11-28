import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt

# -----------------------------------------------------------------------------
# 1. CONFIGURATION & STYLE
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Retail Analytics Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Palette
COLOR_PRIMARY = "#4F46E5"    
BG_COLOR = "#F3F4F6"         
SIDEBAR_BG = "#0F172A"       
TEXT_COLOR = "#1E293B"       

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
        section[data-testid="stSidebar"] input, section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
            background-color: #1E293B !important; color: white !important; border: 1px solid #334155 !important;
        }}

        /* --- INPUTS PAGE PRINCIPALE --- */
        div[data-testid="stVerticalBlock"] > div:not([data-testid="stSidebar"]) label {{ color: #1E293B !important; }}
        div.stNumberInput input {{ background-color: #FFFFFF !important; color: #000000 !important; border: 1px solid #E2E8F0 !important; }}
        
        /* --- BOUTONS (Violets et Texte Blanc) --- */
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
            color: #FFFFFF !important;
        }}
        div.stDownloadButton > button p {{ color: #FFFFFF !important; }}
        
        /* --- TABLEAUX --- */
        div[data-testid="stDataFrame"] {{ border: 1px solid #E2E8F0; border-radius: 8px; overflow: hidden; }}
        div[data-testid="stDataFrame"] th {{ background-color: #F1F5F9 !important; color: #1E293B !important; fill: #1E293B !important; font-weight: 600 !important; }}
        div[data-testid="stDataFrame"] td {{ color: #334155 !important; }}

        /* --- METRICS & ALERTS --- */
        div[data-testid="stMetric"] {{
            background-color: #FFFFFF; padding: 15px; border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 4px solid {COLOR_PRIMARY};
        }}
        div[data-testid="stMetric"] label {{ color: #64748B !important; }}
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{ color: #0F172A !important; }}

        .custom-alert {{ padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; font-weight: 500; font-size: 0.9rem; }}
        .alert-green {{ background-color: #ECFDF5; color: #065F46; border: 1px solid #A7F3D0; }}
        .alert-yellow {{ background-color: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; }}
        .alert-red {{ background-color: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; }}
        .alert-blue {{ background-color: #EFF6FF; color: #1E40AF; border: 1px solid #BFDBFE; }}

        /* --- EXPANDER (Guide) --- */
        .streamlit-expanderHeader {{ font-weight: 600; color: #1E293B !important; background-color: #FFFFFF; border-radius: 8px; }}
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. LOGIQUE MÉTIER
# -----------------------------------------------------------------------------
DATA_FILENAME = "online_retail_II.xlsx"

@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_excel(file_path, sheet_name=0)
        df = df.dropna(subset=['Customer ID'])
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
        df['TotalPrice'] = df['Quantity'] * df['Price']
        df['Customer ID'] = df['Customer ID'].astype(int).astype(str)
        return df
    except Exception as e:
        st.error(f"Erreur chargement: {e}")
        return None

def filter_data(df, date_range, countries, return_mode):
    mask = (df['InvoiceDate'].dt.date >= date_range[0]) & (df['InvoiceDate'].dt.date <= date_range[1])
    if countries: mask = mask & (df['Country'].isin(countries))
    df_filtered = df.loc[mask].copy()
    if return_mode == "Exclure les retours": df_filtered = df_filtered[df_filtered['Quantity'] > 0]
    elif return_mode == "Uniquement les retours": df_filtered = df_filtered[df_filtered['Quantity'] < 0]
    return df_filtered

def compute_rfm(df, analysis_date):
    rfm = df.groupby('Customer ID').agg({
        'InvoiceDate': lambda x: (analysis_date - x.max()).days,
        'Invoice': 'nunique',
        'TotalPrice': 'sum'
    }).reset_index()
    rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']
    rfm = rfm[rfm['Monetary'] > 0]
    
    labels = [1, 2, 3, 4]
    try:
        rfm['R_Score'] = pd.qcut(rfm['Recency'], q=4, labels=list(reversed(labels)))
        rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=4, labels=labels)
        rfm['M_Score'] = pd.qcut(rfm['Monetary'], q=4, labels=labels)
    except ValueError:
        rfm['R_Score'] = 1; rfm['F_Score'] = 1; rfm['M_Score'] = 1
    
    def categorize(row):
        r, f, m = int(row['R_Score']), int(row['F_Score']), int(row['M_Score'])
        fm_score = (f + m) / 2
        if r >= 4 and fm_score >= 3.5: return "Champions 🏆"
        if r >= 3 and fm_score >= 2: return "Loyaux Potentiels 🌱"
        if r >= 3 and fm_score < 2: return "Nouveaux Prometteurs 👋"
        if r <= 2 and fm_score >= 3: return "À Risque ⚠️"
        if r <= 2 and fm_score < 3: return "Hibernants 💤"
        return "Autres"

    rfm['Segment_Label'] = rfm.apply(categorize, axis=1)
    return rfm

def compute_cohorts(df):
    df_c = df[['Customer ID', 'InvoiceDate']].drop_duplicates()
    df_c['OrderMonth'] = df_c['InvoiceDate'].dt.to_period('M')
    df_c['CohortMonth'] = df_c.groupby('Customer ID')['InvoiceDate'].transform('min').dt.to_period('M')
    df_cohort = df_c.groupby(['CohortMonth', 'OrderMonth']).agg(n_customers=('Customer ID', 'nunique')).reset_index()
    df_cohort['PeriodNumber'] = (df_cohort.OrderMonth - df_cohort.CohortMonth).apply(lambda x: x.n)
    cohort_pivot = df_cohort.pivot_table(index='CohortMonth', columns='PeriodNumber', values='n_customers')
    cohort_size = cohort_pivot.iloc[:, 0]
    retention_matrix = cohort_pivot.divide(cohort_size, axis=0)
    return retention_matrix, cohort_size

def style_plot(fig, title=""):
    fig.update_layout(
        template="plotly_white",
        title=dict(text=title, font=dict(size=18, color="#1E293B", family="Inter")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1E293B", family="Inter"),
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(showgrid=False, color="#1E293B", title_font=dict(color="#1E293B"), tickfont=dict(color="#1E293B")),
        yaxis=dict(showgrid=True, gridcolor="#E2E8F0", color="#1E293B", title_font=dict(color="#1E293B"), tickfont=dict(color="#1E293B")),
        legend=dict(font=dict(color="#1E293B"), title=dict(font=dict(color="#1E293B")), bgcolor="rgba(255,255,255,0.5)"),
        coloraxis_colorbar=dict(title=dict(font=dict(color="#1E293B")), tickfont=dict(color="#1E293B")),
        hoverlabel=dict(bgcolor="white", font_size=14, font_family="Inter", font_color="#1E293B")
    )
    return fig

# -----------------------------------------------------------------------------
# 3. APP PRINCIPALE
# -----------------------------------------------------------------------------
st.sidebar.title("🛍️ Retail Analytics")
st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Filtres")

with st.spinner('Chargement des données...'):
    df_raw = load_data(DATA_FILENAME)

if df_raw is not None:
    min_date = df_raw['InvoiceDate'].min().date()
    max_date = df_raw['InvoiceDate'].max().date()
    
    date_range = st.sidebar.date_input("Période", [min_date, max_date], min_value=min_date, max_value=max_date)
    all_countries = sorted(df_raw['Country'].unique().tolist())
    selected_countries = st.sidebar.multiselect("Pays", all_countries, default=['United Kingdom'])
    return_mode = st.sidebar.radio("Mode Retours", ["Exclure les retours", "Inclure tout", "Uniquement les retours"])

    if len(date_range) == 2:
        df = filter_data(df_raw, date_range, selected_countries, return_mode)
        rfm_df = compute_rfm(df, pd.to_datetime(date_range[1]))
        
        st.sidebar.markdown("---")
        # Ajout de l'onglet "Accueil" dans le menu
        page = st.sidebar.radio("Navigation", ["🏠 Accueil", "KPIs (Overview)", "Cohortes (Diagnostiquer)", "Segments (Prioriser)", "Scénarios (Simuler)", "Plan d'Action (Exporter)"])
    else:
        st.stop()

    # --- PAGE D'ACCUEIL (NOUVEAU) ---
    if page == "🏠 Accueil":
        st.title("Bienvenue sur Retail Analytics")
        st.markdown(f"""
        <div style='background-color: white; padding: 25px; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 20px;'>
            <h3 style='color: #4F46E5; margin-top:0;'>👋 Votre assistant de pilotage CRM</h3>
            <p style='color: #475569; font-size: 1.1rem;'>
                Cette application permet à l'équipe marketing de diagnostiquer la rétention, segmenter la base client et simuler l'impact financier de vos campagnes.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            ### 🚀 Ce que vous pouvez faire
            - **Diagnostiquer** : Analysez la santé de vos cohortes clients.
            - **Segmenter** : Identifiez vos VIPs et vos clients à risque via la méthode RFM.
            - **Simuler** : Projetez l'impact d'une remise ou d'une hausse de rétention sur la CLV.
            - **Agir** : Exportez les listes de clients pour vos campagnes d'emailing.
            """)
        
        with col2:
            st.markdown("""
            ### 🧠 Méthodologie utilisée
            - **RFM (Récence, Fréquence, Montant)** : Score de 1 à 4 attribué à chaque client.
            - **CLV (Customer Lifetime Value)** : Valeur vie client estimée.
            - **Cohortes** : Suivi du comportement de rachat mois par mois.
            """)

        st.markdown("---")
        st.info("👈 **Commencez par utiliser le menu latéral** pour filtrer les données (Dates, Pays) et naviguer entre les vues.")

    # --- KPIS ---
    elif page == "KPIs (Overview)":
        st.title("Tableau de Bord Exécutif")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Clients Actifs", f"{df['Customer ID'].nunique():,}")
        c2.metric("Chiffre d'Affaires", f"{df['TotalPrice'].sum():,.0f} €")
        c3.metric("Panier Moyen", f"{df['TotalPrice'].sum() / df['Invoice'].nunique():.1f} €")
        c4.metric("CLV Hist. Moy.", f"{rfm_df['Monetary'].mean():.1f} €")
        
        st.markdown("###")
        
        col1, col2 = st.columns([3, 2])
        with col1:
            top_countries = df.groupby('Country')['TotalPrice'].sum().reset_index().sort_values('TotalPrice', ascending=False).head(8)
            fig_country = px.bar(top_countries, x='TotalPrice', y='Country', orientation='h', text_auto='.2s', color='TotalPrice', color_continuous_scale='Purples')
            st.plotly_chart(style_plot(fig_country, "Top Marchés (CA)"), use_container_width=True)
            
        with col2:
            seg_counts = rfm_df['Segment_Label'].value_counts().reset_index()
            seg_counts.columns = ['Segment', 'Count']
            fig_pie = px.pie(seg_counts, names='Segment', values='Count', hole=0.6, color_discrete_sequence=px.colors.qualitative.Prism)
            fig_pie.update_traces(textposition='inside', textinfo='percent')
            fig_pie.update_layout(legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.0))
            st.plotly_chart(style_plot(fig_pie, "Répartition Segments"), use_container_width=True)

    # --- COHORTES ---
    elif page == "Cohortes (Diagnostiquer)":
        st.title("Analyse de Rétention")
        
        with st.expander("ℹ️ Comprendre la Heatmap de Rétention"):
            st.markdown("""
            Ce graphique montre le **pourcentage de clients qui reviennent acheter** après leur premier achat.
            - **Axe Vertical (Y)** : Le mois où les clients ont fait leur *toute première* commande (Cohorte).
            - **Axe Horizontal (X)** : Le nombre de mois écoulés depuis cette première commande.
            - **Cases Foncées** : Une forte rétention (beaucoup de clients reviennent).
            """)

        retention_matrix, cohort_size = compute_cohorts(df)
        fig_cohort = go.Figure(data=go.Heatmap(
            z=retention_matrix.values, x=retention_matrix.columns, y=retention_matrix.index.astype(str),
            colorscale='Purples', text=retention_matrix.applymap(lambda x: f"{x:.0%}" if not pd.isna(x) else "").values,
            texttemplate="%{text}", xgap=2, ygap=2
        ))
        fig = style_plot(fig_cohort, "Matrice de Rétention (Mois d'Acquisition)")
        fig.update_layout(height=700, yaxis_autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)

    # --- SEGMENTS (AVEC DÉFINITIONS AJOUTÉES) ---
    elif page == "Segments (Prioriser)":
        st.title("Segmentation & Priorisation")
        
        # Ajout du Guide des Définitions
        with st.expander("📘 Guide des Segments - Qui sont-ils ?", expanded=False):
            st.markdown("""
            La segmentation est basée sur les scores Récence (R) et Fréquence/Montant (FM).
            
            - **🏆 Champions** : Acheté très récemment, achètent souvent et pour cher. *Action : Chouchouter.*
            - **🌱 Loyaux Potentiels** : Clients récents avec une bonne fréquence, mais pas encore au top. *Action : Cross-selling.*
            - **👋 Nouveaux Prometteurs** : Viennent de faire leur premier achat récent. *Action : Welcome Pack.*
            - **⚠️ À Risque** : Gros clients passés qui n'ont pas acheté depuis longtemps. *Action : Réactivation urgente.*
            - **💤 Hibernants** : Anciens petits clients, inactifs depuis longtemps. *Action : Automatisation ou nettoyage.*
            """)

        summary = rfm_df.groupby('Segment_Label').agg({'CustomerID': 'count', 'Monetary': 'sum', 'Recency': 'mean'}).reset_index()
        summary.columns = ['Segment', 'Clients', 'CA Total', 'Récence (j)']
        
        c1, c2 = st.columns([5, 4])
        with c1:
            st.subheader("Détails des Segments")
            st.dataframe(summary, use_container_width=True)
        
        with c2:
            st.subheader("Matrice Valeur / Risque")
            fig_scat = px.scatter(summary, x='Récence (j)', y='CA Total', size='Clients', color='Segment', size_max=50, color_discrete_sequence=px.colors.qualitative.Bold)
            fig_scat.update_layout(xaxis_autorange="reversed")
            st.plotly_chart(style_plot(fig_scat), use_container_width=True)
            
        st.markdown("---")
        st.subheader("⚡ Actions recommandées")
        a1, a2, a3 = st.columns(3)
        with a1: st.markdown('<div class="custom-alert alert-green"><strong>🏆 Champions</strong><br>Programme VIP.</div>', unsafe_allow_html=True)
        with a2: st.markdown('<div class="custom-alert alert-yellow"><strong>⚠️ À Risque</strong><br>Offre "Reviens !".</div>', unsafe_allow_html=True)
        with a3: st.markdown('<div class="custom-alert alert-red"><strong>💤 Hibernants</strong><br>Email de réactivation.</div>', unsafe_allow_html=True)

    # --- SIMULATEUR ---
    elif page == "Scénarios (Simuler)":
        st.title("Simulateur d'Impact")
        
        st.markdown("#### 🛠️ Paramètres de simulation")
        
        c1, c2, c3 = st.columns(3)
        sim_margin = c1.slider("Marge (%)", 0.05, 0.50, 0.20, 0.01)
        sim_retention = c2.slider("Rétention cible (r)", 0.1, 0.95, 0.60, 0.05)
        discount_rate = c3.number_input("Taux d'actualisation", 0.05, 0.20, 0.10)
            
        avg_spend = rfm_df['Monetary'].mean()
        denom = (1 + discount_rate - sim_retention)
        clv_sim = (avg_spend * sim_margin * sim_retention) / denom if denom != 0 else 0
        
        st.markdown("###")
        k1, k2 = st.columns(2)
        k1.metric("CLV Projetée", f"{clv_sim:.2f} €")
        k2.metric("Valeur Parc Client", f"{clv_sim * df['Customer ID'].nunique():,.0f} €")
        
        st.subheader("Sensibilité : Marge vs Rétention")
        r_range = np.linspace(0.3, 0.9, 15)
        m_range = np.linspace(0.1, 0.4, 15)
        z = [[(avg_spend * m * r) / (1 + discount_rate - r) for r in r_range] for m in m_range]
        fig_3d = go.Figure(data=[go.Surface(z=z, x=r_range, y=m_range, colorscale='Purples')])
        fig_3d.update_layout(scene=dict(xaxis_title='Rétention', yaxis_title='Marge', zaxis_title='CLV (€)'))
        st.plotly_chart(style_plot(fig_3d), use_container_width=True)

    # --- EXPORT ---
    elif page == "Plan d'Action (Exporter)":
        st.title("Exports CRM")
        target_segs = st.multiselect("Cibler segments", rfm_df['Segment_Label'].unique(), default=['Champions 🏆', 'À Risque ⚠️'])
        if target_segs:
            export = rfm_df[rfm_df['Segment_Label'].isin(target_segs)].copy()
            st.download_button("📥 Télécharger CSV", export.to_csv(index=False).encode('utf-8'), f"CRM_Export.csv", "text/csv")
            
            st.write(f"Prévisualisation ({len(export)} clients) :")
            st.dataframe(export.head(10), use_container_width=True)
        else:
            st.info("Sélectionnez un segment.")

else:
    st.warning("Veuillez charger 'online_retail_II.xlsx'")