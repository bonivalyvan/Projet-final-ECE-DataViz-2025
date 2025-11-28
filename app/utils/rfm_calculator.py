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
        rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=4, labels=labels)
        rfm['M_Score'] = pd.qcut(rfm['Monetary'], q=4, labels=labels)
    except ValueError:
        # Cas où il y a trop peu de données pour faire 4 quartiles
        rfm['R_Score'] = 1
        rfm['F_Score'] = 1
        rfm['M_Score'] = 1

    # 4. Fonction de catégorisation
    def categorize(row):
        r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
        elif r >= 3 and f >= 3 and m >= 3:
            return "Loyal Customers"
        elif r >= 3 and f >= 1 and m >= 2:
            return "Potential Loyalists"
        elif r >= 3 and f <= 1 and m <= 1:
            return "New Customers"
        elif r <= 2 and f >= 3 and m >= 3:
            return "At Risk"
        elif r <= 1 and f <= 2:
            return "Lost"
        else:
            return "Need Attention"

    rfm['Segment_Label'] = rfm.apply(categorize, axis=1)
    return rfm