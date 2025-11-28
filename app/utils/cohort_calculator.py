import pandas as pd
import numpy as np

def compute_cohorts(df):
    """
    Calcule la matrice de rétention des cohortes.
    """
    # Copie pour ne pas modifier l'original
    df_c = df[['Customer ID', 'InvoiceDate']].drop_duplicates().copy()
    
    # Mois de la commande
    df_c['OrderMonth'] = df_c['InvoiceDate'].dt.to_period('M')
    
    # Mois de la cohorte (première commande)
    df_c['CohortMonth'] = df_c.groupby('Customer ID')['InvoiceDate'].transform('min').dt.to_period('M')
    
    # Agrégation par cohorte et mois de commande
    df_cohort = df_c.groupby(['CohortMonth', 'OrderMonth']).agg(
        n_customers=('Customer ID', 'nunique')
    ).reset_index()
    
    # Calcul du numéro de période (mois écoulés)
    df_cohort['PeriodNumber'] = (df_cohort.OrderMonth - df_cohort.CohortMonth).apply(lambda x: x.n)
    
    # Pivot table
    cohort_pivot = df_cohort.pivot_table(index='CohortMonth', columns='PeriodNumber', values='n_customers')
    
    # Taille de la cohorte (mois 0)
    cohort_size = cohort_pivot.iloc[:, 0]
    
    # Matrice de rétention
    retention_matrix = cohort_pivot.divide(cohort_size, axis=0)
    
    return retention_matrix, cohort_size

def compute_clv_empirique(df):
    """
    calcule la clv empirique basee sur les donnees reelles
    clv = ca total genere / nb clients dans la cohorte
    ajout pour avoir la vraie valeur historique
    """
    df_c = df.copy()
    df_c['CohortMonth'] = df_c.groupby('Customer ID')['InvoiceDate'].transform('min').dt.to_period('M')
    
    clv_by_cohort = df_c.groupby('CohortMonth').agg({
        'TotalPrice': 'sum',
        'Customer ID': 'nunique'
    }).reset_index()
    
    # calcul clv moyenne par cohorte
    clv_by_cohort['CLV_Empirique'] = clv_by_cohort['TotalPrice'] / clv_by_cohort['Customer ID']
    clv_by_cohort.columns = ['Cohorte', 'CA Total', 'Clients', 'CLV Empirique']
    
    return clv_by_cohort