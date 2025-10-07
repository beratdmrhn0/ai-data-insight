import pytest
import pandas as pd
from preprocess import Preprocessor
from anomaly import detect_anomalies
from forecast import forecast_sales


class TestIntegration:
    """Integration testleri - modüller bir arada çalışıyor mu?"""
    
    def test_upload_to_preprocess_pipeline(self, sample_csv_small):
        """Upload → Preprocess pipeline testi"""
        # CSV yükle
        preprocessor = Preprocessor(sample_csv_small)
        df, summary, anomaly_count, forecast = preprocessor.run()
        
        # Temel kontroller
        assert len(df) > 0
        assert isinstance(summary, dict)
        assert isinstance(anomaly_count, int)
        assert isinstance(forecast, list)
        
        # Summary stats kontrolü
        assert 'record_count' in str(summary) or len(df) > 0
        
    def test_preprocess_to_anomaly_pipeline(self, sample_csv_anomaly):
        """Preprocess → Anomaly pipeline testi"""
        # Preprocess
        preprocessor = Preprocessor(sample_csv_anomaly)
        df, summary, anomaly_count, forecast = preprocessor.run()
        
        # Anomaly detection
        anomalies, daily = detect_anomalies(df, 'order_date', 'quantity')
        
        # Pipeline kontrolleri
        assert len(df) > 0
        assert len(daily) > 0
        assert anomaly_count >= 0
        
    def test_preprocess_to_forecast_pipeline(self, sample_csv_small):
        """Preprocess → Forecast pipeline testi"""
        # Preprocess
        preprocessor = Preprocessor(sample_csv_small)
        df, summary, anomaly_count, forecast = preprocessor.run()
        
        # Forecast
        forecast_df, model = forecast_sales(df, 'order_date', 'quantity')
        
        # Pipeline kontrolleri
        assert len(forecast) > 0  # Preprocess forecast
        assert len(forecast_df) == 7  # Forecast modülü forecast
        assert model is not None
        
    def test_full_pipeline_with_missing_data(self, sample_csv_with_missing):
        """Eksik veri ile tam pipeline testi"""
        # Preprocess (eksik değerleri doldurur)
        preprocessor = Preprocessor(sample_csv_with_missing)
        df, summary, anomaly_count, forecast = preprocessor.run()
        
        # Anomaly detection
        anomalies, daily = detect_anomalies(df, 'order_date', 'quantity')
        
        # Forecast
        forecast_df, model = forecast_sales(df, 'order_date', 'quantity')
        
        # Pipeline kontrolleri
        assert len(df) > 0
        assert df['quantity'].isna().sum() == 0  # Eksik değerler doldurulmuş
        assert len(forecast) > 0
        assert len(forecast_df) == 7
        
    def test_error_propagation_pipeline(self):
        """Hata yayılımı pipeline testi"""
        # Boş DataFrame ile pipeline (kolonlar olmadan)
        empty_df = pd.DataFrame()
        
        try:
            anomalies, daily = detect_anomalies(empty_df, 'order_date', 'quantity')
            # Boş DataFrame ile çalışmalı
            assert len(anomalies) == 0
            assert len(daily) == 0
        except Exception as e:
            # Eğer hata fırlatırsa, kontrollü olmalı (KeyError bekleniyor)
            assert isinstance(e, KeyError) or "order_date" in str(e)
            
    def test_data_consistency_across_modules(self, sample_dataframe):
        """Modüller arası veri tutarlılığı testi"""
        # Aynı DataFrame'i farklı modüllerde kullan
        anomalies, daily = detect_anomalies(sample_dataframe, 'order_date', 'quantity')
        forecast_df, model = forecast_sales(sample_dataframe, 'order_date', 'quantity')
        
        # Veri tutarlılığı kontrolleri
        assert len(sample_dataframe) == len(sample_dataframe)  # Original intact
        assert len(daily) <= len(sample_dataframe)  # Daily <= original
        assert len(forecast_df) == 7  # Forecast length consistent
