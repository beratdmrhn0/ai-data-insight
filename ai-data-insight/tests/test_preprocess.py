import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from preprocess import Preprocessor


class TestPreprocessor:
    """Preprocessor sınıfının testleri"""
    
    def create_sample_csv(self, data_dict: dict, filename: str = "test.csv"):
        """Test için CSV dosyası oluşturur"""
        df = pd.DataFrame(data_dict)
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        df.to_csv(temp_file.name, index=False)
        temp_file.close()
        return temp_file.name
    
    def test_csv_loading(self):
        """CSV dosyası yükleme testi"""
        # Test verisi
        data = {
            'sku': ['A', 'B', 'C'],
            'quantity': [10, 20, 30],
            'price': [100.0, 200.0, 300.0],
            'order_date': ['2023-01-01', '2023-01-02', '2023-01-03']
        }
        
        csv_path = self.create_sample_csv(data)
        
        try:
            preprocessor = Preprocessor(csv_path)
            df, summary, anomaly_count, forecast = preprocessor.run()
            
            # Temel kontroller
            assert len(df) == 3
            assert 'sku' in df.columns
            assert 'quantity' in df.columns
            assert anomaly_count >= 0
            assert len(forecast) >= 0
            
        finally:
            os.unlink(csv_path)  # Temp dosyayı sil
    
    def test_missing_value_handling(self):
        """Eksik değer işleme testi"""
        data = {
            'sku': ['A', 'B', None],
            'quantity': [10, None, 30],
            'price': [100.0, 200.0, None],
            'order_date': ['2023-01-01', '2023-01-02', '2023-01-03']
        }
        
        csv_path = self.create_sample_csv(data)
        
        try:
            preprocessor = Preprocessor(csv_path)
            df, summary, anomaly_count, forecast = preprocessor.run()
            
            # Eksik değerler doldurulmuş olmalı
            assert df['quantity'].isna().sum() == 0
            assert df['price'].isna().sum() == 0
            
        finally:
            os.unlink(csv_path)
    
    def test_date_parsing(self):
        """Tarih parsing testi"""
        data = {
            'order_date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'quantity': [10, 20, 30]
        }
        
        csv_path = self.create_sample_csv(data)
        
        try:
            preprocessor = Preprocessor(csv_path)
            df, summary, anomaly_count, forecast = preprocessor.run()
            
            # Tarih kolonu datetime tipinde olmalı
            assert pd.api.types.is_datetime64_any_dtype(df['order_date'])
            
        finally:
            os.unlink(csv_path)
    
    def test_empty_dataset(self):
        """Boş dataset testi"""
        data = {
            'sku': [],
            'quantity': [],
            'price': []
        }
        
        csv_path = self.create_sample_csv(data)
        
        try:
            preprocessor = Preprocessor(csv_path)
            df, summary, anomaly_count, forecast = preprocessor.run()
            
            # Boş dataset ile crash olmamalı
            assert len(df) == 0
            assert anomaly_count == 0
            assert len(forecast) == 0
            
        finally:
            os.unlink(csv_path)
    
    def test_single_row_dataset(self):
        """Tek satırlık dataset testi"""
        data = {
            'sku': ['A'],
            'quantity': [10],
            'price': [100.0],
            'order_date': ['2023-01-01']
        }
        
        csv_path = self.create_sample_csv(data)
        
        try:
            preprocessor = Preprocessor(csv_path)
            df, summary, anomaly_count, forecast = preprocessor.run()
            
            # Tek satır ile çalışmalı
            assert len(df) == 1
            assert anomaly_count == 0  # Tek satırda anomali olmaz
            
        finally:
            os.unlink(csv_path)
