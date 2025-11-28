import pandas as pd

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