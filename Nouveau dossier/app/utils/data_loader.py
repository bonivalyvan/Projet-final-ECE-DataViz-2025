import streamlit as st
import pandas as pd
import os

# Chemin relatif vers les données (à adapter selon ta config)
DATA_PATH = os.path.join(os.path.dirname(__file__), '../../data/raw/online_retail_II.xlsx')


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
        st.error(f"Erreur chargement: {e}. Vérifiez le chemin : {file_path}")
        return None


def filter_data(df, date_range, countries, return_mode):
    mask = (df['InvoiceDate'].dt.date >= date_range[0]) & (df['InvoiceDate'].dt.date <= date_range[1])
    if countries: mask = mask & (df['Country'].isin(countries))
    df_filtered = df.loc[mask].copy()
    if return_mode == "Exclure les retours":
        df_filtered = df_filtered[df_filtered['Quantity'] > 0]
    elif return_mode == "Uniquement les retours":
        df_filtered = df_filtered[df_filtered['Quantity'] < 0]
    return df_filtered


def sidebar_filters():
    """Génère la sidebar et retourne le dataframe filtré."""
    st.sidebar.title("🛍️ Retail Analytics")
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎛️ Filtres")

    # On utilise un chemin absolu ou relatif robuste
    # Pour le dev, on peut mettre le chemin en dur ou le passer en param
    if not os.path.exists(DATA_PATH):
        st.sidebar.error("Fichier introuvable.")
        return None, None

    with st.spinner('Chargement...'):
        df_raw = load_data(DATA_PATH)

    if df_raw is not None:
        min_date = df_raw['InvoiceDate'].min().date()
        max_date = df_raw['InvoiceDate'].max().date()

        date_range = st.sidebar.date_input("Période", [min_date, max_date], min_value=min_date, max_value=max_date)
        all_countries = sorted(df_raw['Country'].unique().tolist())
        selected_countries = st.sidebar.multiselect("Pays", all_countries, default=['United Kingdom'])
        return_mode = st.sidebar.radio("Mode Retours",
                                       ["Exclure les retours", "Inclure tout", "Uniquement les retours"])

        if len(date_range) == 2:
            df_filtered = filter_data(df_raw, date_range, selected_countries, return_mode)
            # On retourne aussi la date de fin pour le calcul RFM
            return df_filtered, pd.to_datetime(date_range[1])

    return None, None