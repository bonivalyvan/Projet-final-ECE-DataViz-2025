"""
Fonctions helper pour afficher les KPIs avec infobulles et définitions
"""
import streamlit as st
import pandas as pd


def display_kpi_with_help(label, value, help_text, delta=None, delta_color="normal"):
    """
    Affiche un KPI avec une infobulle explicative
    
    Args:
        label: Nom du KPI
        value: Valeur à afficher
        help_text: Texte d'aide (définition + exemple)
        delta: Delta optionnel (ex: "+5%")
        delta_color: "normal", "off", "inverse"
    """
    col1, col2 = st.columns([20, 1])
    with col1:
        st.metric(label, value, delta=delta, delta_color=delta_color)
    with col2:
        st.info("ℹ️", icon="ℹ️")
        st.caption(help_text)


def create_kpi_help_html(metric_name, definition, formula="", example="", unit=""):
    """
    Crée un texte d'aide formaté pour les infobulles KPI
    
    Args:
        metric_name: Nom de la métrique
        definition: Explication de ce qu'est la métrique
        formula: Formule de calcul (optionnel)
        example: Exemple numérique (optionnel)
        unit: Unité de mesure (optionnel)
    """
    help_text = f"""
    **{metric_name}**
    
    📌 **Définition** : {definition}
    """
    
    if unit:
        help_text += f"\n\n📊 **Unité** : {unit}"
    
    if formula:
        help_text += f"\n\n🧮 **Formule** : {formula}"
    
    if example:
        help_text += f"\n\n💡 **Exemple** : {example}"
    
    return help_text


# Dictionnaire centralisé des définitions KPI
KPI_DEFINITIONS = {
    "clients_actifs": {
        "label": "Clients Actifs",
        "definition": "Nombre de clients uniques ayant effectué au moins une transaction dans la période",
        "unit": "Nombre de clients",
        "example": "Si 3,000 clients ont acheté ce mois, n=3,000"
    },
    "ca_total": {
        "label": "Chiffre d'Affaires Total",
        "definition": "Somme des ventes (Quantité × Prix) sur la période",
        "unit": "£ (Livres Sterling)",
        "example": "CA = 100 clients × 50£ panier moyen = 5,000£"
    },
    "panier_moyen": {
        "label": "Panier Moyen",
        "definition": "CA total divisé par le nombre de transactions",
        "formula": "CA Total ÷ Nombre de transactions",
        "unit": "£ (Livres Sterling)",
        "example": "5,000£ CA ÷ 100 transactions = 50£"
    },
    "clv_historique": {
        "label": "CLV Empirique Moyenne",
        "definition": "Valeur réelle moyenne générée par chaque client depuis son acquisition",
        "formula": "CA Total Généré par Cohorte ÷ Nombre de Clients",
        "unit": "£ (Livres Sterling)",
        "example": "Cohorte 2020-01 : 50,000£ CA ÷ 1,000 clients = 50£ CLV"
    },
    "retention_m1": {
        "label": "Rétention M+1",
        "definition": "% de clients acquis le mois N qui ont acheté à nouveau le mois N+1",
        "formula": "Clients revenant M+1 ÷ Clients acquis mois N",
        "unit": "%",
        "example": "1,000 clients acquis nov 2020, 450 achètent en déc = Rétention 45%"
    },
    "retention_m3": {
        "label": "Rétention M+3",
        "definition": "% de clients acquis le mois N qui ont acheté à nouveau au mois N+3",
        "formula": "Clients revenant M+3 ÷ Clients acquis mois N",
        "unit": "%",
        "example": "1,000 clients acquis oct 2020, 350 achètent en janv = Rétention 35%"
    },
    "clv_formule": {
        "label": "CLV Formule Fermée",
        "definition": "Valeur vie client estimée via modèle mathématique intégrant marge, rétention et coût du capital",
        "formula": "CLV = (Panier Moyen × Marge × Rétention) ÷ (1 + Taux d'Actualisation - Rétention)",
        "unit": "£ (Livres Sterling)",
        "example": "CLV = (50£ × 25% × 60%) ÷ (1 + 10% - 60%) = 14£"
    },
    "rfm_score": {
        "label": "RFM Score",
        "definition": "Score combiné de Récence (R), Fréquence (F) et Montant (M) allant de 1-4 par dimension",
        "formula": "Score = (R_Score + F_Score + M_Score) / 3",
        "unit": "Score 1-4",
        "example": "R=4 (Récent), F=3, M=4 → Score élevé = Champion"
    }
}


def get_kpi_help(metric_key):
    """Récupère le texte d'aide pour une métrique"""
    if metric_key not in KPI_DEFINITIONS:
        return "Métrique non documentée"
    
    meta = KPI_DEFINITIONS[metric_key]
    return create_kpi_help_html(
        meta["label"],
        meta["definition"],
        meta.get("formula", ""),
        meta.get("example", ""),
        meta.get("unit", "")
    )


def format_count_with_n(value, total, metric_type="percentage"):
    """
    Formate une valeur avec le compteur (n)
    
    Args:
        value: Valeur (pourcentage ou nombre)
        total: Nombre total pour calculer le compteur
        metric_type: "percentage" ou "count"
    
    Returns:
        Texte formaté "Value (n=X)"
    """
    if metric_type == "percentage":
        count = int(total)
        return f"{value:.1%} (n={count:,})"
    else:
        return f"{value:,.0f} (n={total:,})"
