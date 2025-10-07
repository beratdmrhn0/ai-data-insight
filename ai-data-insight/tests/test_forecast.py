import pytest
import pandas as pd
import numpy as np
from forecast import forecast_sales


class TestForecast:
    """Forecast modülünün testleri"""
    
    def create_test_dataframe(self, dates, quantities):
        """Test için DataFrame oluşturur"""
        data = {
            'order_date': dates,
            'quantity': quantities
        }
        df = pd.DataFrame(data)
        df['order_date'] = pd.to_datetime(df['order_date'])
        return df
    
    def test_basic_forecast(self):
        """Temel forecast testi"""
        dates = ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05']
        quantities = [100, 110, 120, 130, 140]  # Artan trend
        
        df = self.create_test_dataframe(dates, quantities)
        forecast_df, model = forecast_sales(df, 'order_date', 'quantity', days_ahead=7)
        
        # Temel kontroller
        assert len(forecast_df) == 7
        assert 'forecast' in forecast_df.columns
        assert model is not None
        
        # Forecast değerleri mantıklı olmalı (artan trend devam etmeli)
        forecasts = forecast_df['forecast'].tolist()
        assert forecasts[0] > 140  # İlk tahmin son değerden büyük olmalı
        assert all(forecast > 0 for forecast in forecasts)  # Negatif tahmin olmamalı
    
    def test_decreasing_trend(self):
        """Azalan trend testi"""
        dates = ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05']
        quantities = [140, 130, 120, 110, 100]  # Azalan trend
        
        df = self.create_test_dataframe(dates, quantities)
        forecast_df, model = forecast_sales(df, 'order_date', 'quantity', days_ahead=5)
        
        # Azalan trendde tahminler azalmalı
        forecasts = forecast_df['forecast'].tolist()
        assert forecasts[0] < 100  # İlk tahmin son değerden küçük olmalı
        assert len(forecast_df) == 5
    
    def test_constant_values(self):
        """Sabit değerler testi"""
        dates = ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05']
        quantities = [100, 100, 100, 100, 100]  # Sabit değerler
        
        df = self.create_test_dataframe(dates, quantities)
        forecast_df, model = forecast_sales(df, 'order_date', 'quantity', days_ahead=3)
        
        # Sabit değerlerde tahminler de sabit olmalı
        forecasts = forecast_df['forecast'].tolist()
        assert all(abs(forecast - 100) < 0.1 for forecast in forecasts)
        assert len(forecast_df) == 3
    
    def test_empty_dataset(self):
        """Boş dataset testi"""
        df = self.create_test_dataframe([], [])
        
        # Boş dataset ile hata fırlatmalı
        with pytest.raises(Exception):
            forecast_sales(df, 'order_date', 'quantity')
    
    def test_single_value_dataset(self):
        """Tek değerli dataset testi"""
        dates = ['2023-01-01']
        quantities = [100]
        
        df = self.create_test_dataframe(dates, quantities)
        forecast_df, model = forecast_sales(df, 'order_date', 'quantity', days_ahead=2)
        
        # Tek değer ile de çalışmalı
        assert len(forecast_df) == 2
        forecasts = forecast_df['forecast'].tolist()
        assert all(forecast == 100 for forecast in forecasts)
    
    def test_forecast_length(self):
        """Forecast uzunluğu testi"""
        dates = ['2023-01-01', '2023-01-02', '2023-01-03']
        quantities = [100, 110, 120]
        
        df = self.create_test_dataframe(dates, quantities)
        
        # Farklı days_ahead değerleri test et
        for days in [1, 7, 14, 30]:
            forecast_df, model = forecast_sales(df, 'order_date', 'quantity', days_ahead=days)
            assert len(forecast_df) == days
    
    def test_negative_values(self):
        """Negatif değerler testi"""
        dates = ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05']
        quantities = [100, -50, 150, -25, 200]  # Negatif değerler içeren
        
        df = self.create_test_dataframe(dates, quantities)
        forecast_df, model = forecast_sales(df, 'order_date', 'quantity', days_ahead=3)
        
        # Negatif değerlerle de çalışmalı
        assert len(forecast_df) == 3
        forecasts = forecast_df['forecast'].tolist()
        assert len(forecasts) == 3
    
    def test_large_dataset(self):
        """Büyük dataset testi"""
        # 100 günlük veri
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        quantities = np.random.normal(100, 10, 100).tolist()  # Normal dağılım
        
        df = self.create_test_dataframe(dates.strftime('%Y-%m-%d'), quantities)
        forecast_df, model = forecast_sales(df, 'order_date', 'quantity', days_ahead=7)
        
        # Büyük dataset ile çalışmalı
        assert len(forecast_df) == 7
        assert model is not None
        forecasts = forecast_df['forecast'].tolist()
        assert all(forecast > 0 for forecast in forecasts)
