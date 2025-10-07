import pytest
import pandas as pd
import numpy as np
from anomaly import detect_anomalies, detect_anomalies_customer


class TestAnomalyDetection:
    """Anomaly detection modülünün testleri"""
    
    def test_normal_data_no_anomalies(self):
        """Normal veri - anomali olmamalı"""
        data = {
            'order_date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'],
            'quantity': [100, 105, 98, 102, 103]  # Normal varyasyon
        }
        df = pd.DataFrame(data)
        df['order_date'] = pd.to_datetime(df['order_date'])
        
        anomalies, daily = detect_anomalies(df, 'order_date', 'quantity')
        
        # Normal veride anomali olmamalı
        assert len(anomalies) == 0
        assert len(daily) == 5
    
    def test_clear_anomaly_detection(self):
        """Açık anomali tespiti"""
        data = {
            'order_date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05', '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10'],
            'quantity': [100, 105, 98, 102, 103, 99, 101, 97, 104, 1000]  # 1000 açık anomali
        }
        df = pd.DataFrame(data)
        df['order_date'] = pd.to_datetime(df['order_date'])
        
        anomalies, daily = detect_anomalies(df, 'order_date', 'quantity')
        
        # Anomali tespit edilmeli
        assert len(anomalies) >= 1
        # Anomali günü 2023-01-10 olmalı
        anomaly_dates = anomalies['order_date'].dt.strftime('%Y-%m-%d').tolist()
        assert '2023-01-10' in anomaly_dates
    
    def test_empty_dataset(self):
        """Boş dataset testi"""
        data = {
            'order_date': [],
            'quantity': []
        }
        df = pd.DataFrame(data)
        df['order_date'] = pd.to_datetime(df['order_date'])
        
        anomalies, daily = detect_anomalies(df, 'order_date', 'quantity')
        
        # Boş dataset ile crash olmamalı
        assert len(anomalies) == 0
        assert len(daily) == 0
    
    def test_single_value_dataset(self):
        """Tek değerli dataset testi"""
        data = {
            'order_date': ['2023-01-01'],
            'quantity': [100]
        }
        df = pd.DataFrame(data)
        df['order_date'] = pd.to_datetime(df['order_date'])
        
        anomalies, daily = detect_anomalies(df, 'order_date', 'quantity')
        
        # Tek değer ile anomali tespit edilemez (std = 0)
        assert len(anomalies) == 0
        assert len(daily) == 1
    
    def test_all_same_values(self):
        """Tüm değerler aynı"""
        data = {
            'order_date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'],
            'quantity': [100, 100, 100, 100, 100]  # Hepsi aynı
        }
        df = pd.DataFrame(data)
        df['order_date'] = pd.to_datetime(df['order_date'])
        
        anomalies, daily = detect_anomalies(df, 'order_date', 'quantity')
        
        # Aynı değerlerde anomali olmamalı
        assert len(anomalies) == 0
        assert len(daily) == 5
    
    def test_customer_anomaly_detection(self):
        """Müşteri anomali tespiti testi"""
        data = {
            'customer_id': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],
            'Total Spend': [1000, 1100, 1050, 1020, 1080, 1030, 1090, 1060, 1070, 50000]  # J açık anomali
        }
        df = pd.DataFrame(data)
        
        anomalies, df_result = detect_anomalies_customer(df, 'Total Spend')
        
        # Anomali tespit edilmeli
        assert len(anomalies) >= 1
        # Anomali müşterisi J olmalı
        anomaly_customers = anomalies['customer_id'].tolist()
        assert 'J' in anomaly_customers
    
    def test_threshold_calculation(self):
        """Threshold hesaplama testi"""
        data = {
            'order_date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'],
            'quantity': [100, 200, 300, 400, 500]  # Artan trend
        }
        df = pd.DataFrame(data)
        df['order_date'] = pd.to_datetime(df['order_date'])
        
        anomalies, daily = detect_anomalies(df, 'order_date', 'quantity')
        
        # Artan trendde anomali tespit edilebilir
        # Test sadece crash olmadığını kontrol eder
        assert len(daily) == 5
        assert daily['quantity'].std() > 0  # Standart sapma hesaplanabilmeli
