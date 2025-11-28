import pandas as pd
import numpy as np


def compute_rfm(df, analysis_date):
    # 1. Sécurité : Si le dataframe filtré est vide, on retourne une structure vide immédiatement
    if df.empty:
        return pd.DataFrame(columns=[
            'CustomerID', 'Recency', 'Frequency', 'Monetary',
            'R_Score', 'F_Score', 'M_Score', 'Segment_Label'
        ])

    # 2. Agrégation par client
    rfm = df.groupby('Customer ID').agg({
        'InvoiceDate': lambda x: (analysis_date - x.max()).days,
        'Invoice': 'nunique',
        'TotalPrice': 'sum'
    }).reset_index()

    rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']

    # On ne garde que ceux qui ont un montant positif (pour éviter les erreurs de log ou bizarreries)
    rfm = rfm[rfm['Monetary'] > 0]

    # Sécurité supplémentaire : Si après nettoyage des montants négatifs c'est vide
    if rfm.empty:
        return pd.DataFrame(columns=[
            'CustomerID', 'Recency', 'Frequency', 'Monetary',
            'R_Score', 'F_Score', 'M_Score', 'Segment_Label'
        ])

    # 3. Calcul des Scores (qcut)
    labels = [1, 2, 3, 4]
    try:
        rfm['R_Score'] = pd.qcut(rfm['Recency'], q=4, labels=list(reversed(labels)))
        rfm['F_Score'] = pd.qcut(rfm['Frequency'], q=4, labels=labels)
        rfm['M_Score'] = pd.qcut(rfm['Monetary'], q=4, labels=labels)
    except ValueError:
        # Cas où il y a trop peu de données pour faire 4 quartiles
        rfm['R_Score'] = 1
        rfm['F_Score'] = 1
        rfm['M_Score'] = 1

    # 4. Fonction de catégorisation
    def categorize(row):
        r = int(row['R_Score'])
        f = int(row['F_Score'])
        m = int(row['M_Score'])

        fm_score = (f + m) / 2

        if r >= 4 and fm_score >= 3.5: return "Champions 🏆"
        if r >= 3 and fm_score >= 2: return "Loyaux Potentiels 🌱"
        if r >= 3 and fm_score < 2: return "Nouveaux Prometteurs 👋"
        if r <= 2 and fm_score >= 3: return "À Risque ⚠️"
        if r <= 2 and fm_score < 3: return "Hibernants 💤"
        return "Autres"

    # 5. Application de la catégorisation
    # L'utilisation de result_type='reduce' peut parfois aider,
    # mais la vérification "if rfm.empty" au début est la vraie solution.
    rfm['Segment_Label'] = rfm.apply(categorize, axis=1)

    return rfm