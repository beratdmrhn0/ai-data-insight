import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

def forecast_sales(df: pd.DataFrame, date_col="order_date", value_col="quantity", days_ahead=7):
    """
    Günlük satış verilerini kullanarak gelecek günler için tahmin yapar.
    Linear regression kullanarak trend analizi yapar.
    """
    # Günlük toplam satış
    daily = df.groupby(date_col)[value_col].sum().reset_index()
    daily = daily.sort_values(date_col)
    
    # Tarihleri sayıya çevir
    daily["day_index"] = np.arange(len(daily))
    
    X = daily[["day_index"]]
    y = daily[value_col]
    
    # Linear regression modeli
    model = LinearRegression()
    model.fit(X, y)
    
    # Gelecek günler için tahmin
    future_days = np.arange(len(daily), len(daily) + days_ahead).reshape(-1,1)
    preds = model.predict(future_days)
    
    forecast_df = pd.DataFrame({
        "day_index": future_days.flatten(),
        "forecast": preds
    })
    
    return forecast_df, model

def moving_average_forecast(df: pd.DataFrame, date_col="order_date", value_col="quantity", days_ahead=7, window=7):
    """
    Hareketli ortalama kullanarak basit tahmin yapar.
    Son N günün ortalamasını alır.
    """
    # Günlük toplam satış
    daily = df.groupby(date_col)[value_col].sum().reset_index()
    daily = daily.sort_values(date_col)
    
    # Son N günün ortalaması
    last_avg = daily[value_col].tail(window).mean()
    
    # Gelecek günler için tahmin (aynı değer)
    future_dates = pd.date_range(start=daily[date_col].max(), periods=days_ahead+1, freq='D')[1:]
    
    forecast_df = pd.DataFrame({
        "forecast": [last_avg] * days_ahead,
        "date": future_dates
    })
    
    return forecast_df, daily

def naive_forecast(df: pd.DataFrame, date_col="order_date", value_col="quantity", days_ahead=7):
    """
    Naive forecast: yarın bugünkü kadar satılır.
    En basit tahmin yöntemi.
    """
    # Günlük toplam satış
    daily = df.groupby(date_col)[value_col].sum().reset_index()
    daily = daily.sort_values(date_col)
    
    # Son günün değeri
    last_value = daily[value_col].iloc[-1]
    
    # Gelecek günler için tahmin (aynı değer)
    future_dates = pd.date_range(start=daily[date_col].max(), periods=days_ahead+1, freq='D')[1:]
    
    forecast_df = pd.DataFrame({
        "forecast": [last_value] * days_ahead,
        "date": future_dates
    })
    
    return forecast_df, daily
