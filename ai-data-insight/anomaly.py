import pandas as pd

def detect_anomalies(df: pd.DataFrame, date_col="order_date", value_col="quantity"):
    """
    Günlük satış adetlerini analiz ederek anomalileri tespit eder.
    Ortalama ± 3 * standart sapma dışında kalan günleri anomali kabul eder.
    """
    # Günlük toplam satış
    daily = df.groupby(date_col)[value_col].sum().reset_index()
    
    mean = daily[value_col].mean()
    std = daily[value_col].std()
    
    # Anomali koşulu: ortalamadan 2 standart sapma uzakta (daha hassas)
    anomalies = daily[
        (daily[value_col] > mean + 2*std) |
        (daily[value_col] < mean - 2*std)
    ]
    
    return anomalies, daily

def detect_anomalies_customer(df: pd.DataFrame, value_col="Total Spend"):
    """
    Müşteri harcama verilerinde anomalileri tespit eder.
    Ortalama ± 3 * standart sapma dışında kalan değerleri anomali kabul eder.
    """
    # Sayısal kolonu kontrol et
    if value_col not in df.columns:
        return pd.DataFrame(), df
    
    # Sayısal değerlere çevir
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce").fillna(0)
    
    mean = df[value_col].mean()
    std = df[value_col].std()
    
    # Anomali koşulu: ortalamadan 2 standart sapma uzakta (daha hassas)
    anomalies = df[
        (df[value_col] > mean + 2*std) |
        (df[value_col] < mean - 2*std)
    ]
    
    return anomalies, df
