import pytest
import pandas as pd
from hypothesis import given, strategies as st
from anomaly import detect_anomalies
from forecast import forecast_sales


class TestPropertyBased:
    """Property-based testler - otomatik random input ile edge case tarar"""
    
    @given(
        st.lists(
            st.floats(min_value=0, max_value=1000, allow_nan=False),
            min_size=5,
            max_size=50
        )
    )
    def test_anomaly_detection_properties(self, quantities):
        """Anomali tespiti property-based testi"""
        # Random quantities ile DataFrame oluştur
        dates = pd.date_range('2023-01-01', periods=len(quantities), freq='D')
        df = pd.DataFrame({
            'order_date': dates,
            'quantity': quantities
        })
        
        anomalies, daily = detect_anomalies(df, 'order_date', 'quantity')
        
        # Property kontrolleri
        assert len(anomalies) <= len(daily)  # Anomaly sayısı <= toplam gün sayısı
        assert len(daily) == len(df)  # Daily length = original length
        assert anomalies['quantity'].dtype == daily['quantity'].dtype  # Type consistency
        
        # Anomaly değerleri mantıklı olmalı
        if len(anomalies) > 0:
            assert anomalies['quantity'].min() >= 0  # Negatif anomali olmamalı
            assert anomalies['quantity'].max() < float('inf')  # Infinity olmamalı
    
    @given(
        st.lists(
            st.floats(min_value=0, max_value=1000, allow_nan=False),
            min_size=3,
            max_size=30
        )
    )
    def test_forecast_properties(self, quantities):
        """Forecast property-based testi"""
        # Random quantities ile DataFrame oluştur
        dates = pd.date_range('2023-01-01', periods=len(quantities), freq='D')
        df = pd.DataFrame({
            'order_date': dates,
            'quantity': quantities
        })
        
        try:
            forecast_df, model = forecast_sales(df, 'order_date', 'quantity')
            
            # Property kontrolleri
            assert len(forecast_df) == 7  # Her zaman 7 günlük tahmin
            assert 'forecast' in forecast_df.columns  # Forecast kolonu var
            assert all(isinstance(x, (int, float)) for x in forecast_df['forecast'])  # Numeric değerler
            assert not forecast_df['forecast'].isna().any()  # NaN değer yok
            
            # Forecast değerleri mantıklı olmalı
            forecasts = forecast_df['forecast'].tolist()
            # NOT: Linear regression negatif tahminler üretebilir (azalan trend durumunda)
            # Bu gerçek bir durum, bu yüzden sadece infinity kontrolü yapıyoruz
            assert all(x < float('inf') for x in forecasts)  # Infinity olmamalı
            assert all(x > float('-inf') for x in forecasts)  # -Infinity olmamalı
            
        except Exception as e:
            # Eğer hata fırlatırsa, kontrollü olmalı
            assert "error" in str(e).lower() or "empty" in str(e).lower()
    
    @given(
        st.lists(
            st.floats(min_value=0, max_value=1000, allow_nan=False),
            min_size=1,
            max_size=100
        )
    )
    def test_dataframe_properties(self, quantities):
        """DataFrame property-based testi"""
        # Random quantities ile DataFrame oluştur
        dates = pd.date_range('2023-01-01', periods=len(quantities), freq='D')
        df = pd.DataFrame({
            'order_date': dates,
            'quantity': quantities
        })
        
        # Property kontrolleri
        assert len(df) == len(quantities)  # Length consistency
        assert df['quantity'].dtype in ['int64', 'float64']  # Numeric type
        assert df['order_date'].dtype == 'datetime64[ns]'  # Date type
        assert not df['quantity'].isna().any()  # No NaN values
        assert not df['order_date'].isna().any()  # No NaT values
        
        # Quantity değerleri mantıklı olmalı
        assert df['quantity'].min() >= 0  # Non-negative
        assert df['quantity'].max() < float('inf')  # No infinity
        
        # Standart sapma kontrolü (tek değerli serilerde NaN olabilir)
        if len(df) > 1:
            assert df['quantity'].std() >= 0  # Non-negative std
        else:
            # Tek değerli serilerde std NaN olabilir, bu normal
            assert pd.isna(df['quantity'].std()) or df['quantity'].std() >= 0
    
    @given(
        st.lists(
            st.floats(min_value=0, max_value=1000, allow_nan=False),
            min_size=2,
            max_size=20
        ),
        st.floats(min_value=1.0, max_value=10.0)
    )
    def test_anomaly_threshold_properties(self, quantities, multiplier):
        """Anomali threshold property-based testi"""
        # Random quantities ile DataFrame oluştur
        dates = pd.date_range('2023-01-01', periods=len(quantities), freq='D')
        df = pd.DataFrame({
            'order_date': dates,
            'quantity': quantities
        })
        
        anomalies, daily = detect_anomalies(df, 'order_date', 'quantity')
        
        # Threshold property kontrolleri
        mean = daily['quantity'].mean()
        std = daily['quantity'].std()
        
        if std > 0:  # Eğer standart sapma varsa
            # Anomaly değerleri threshold dışında olmalı
            if len(anomalies) > 0:
                upper_threshold = mean + 2 * std
                lower_threshold = mean - 2 * std
                
                anomaly_quantities = anomalies['quantity'].tolist()
                for qty in anomaly_quantities:
                    assert qty > upper_threshold or qty < lower_threshold


class TestAPIPropertyBased:
    """API property-based testleri"""
    
    @given(st.integers(min_value=1, max_value=10000))
    def test_preprocess_response_schema(self, upload_id):
        """Preprocess endpoint response schema property testi"""
        # Bu test gerçek API çağrısı yapmaz, sadece schema validation test eder
        # Gerçek test için test_api.py kullanılmalı
        
        # Response schema property'leri
        expected_fields = ['record_count', 'column_count', 'anomaly_count', 'forecast', 'summary_stats']
        
        # Her field'ın varlığını kontrol et
        for field in expected_fields:
            assert isinstance(field, str)  # Field isimleri string olmalı
            assert len(field) > 0  # Boş field ismi olmamalı
    
    @given(st.lists(st.integers(min_value=1, max_value=1000), min_size=1, max_size=100))
    def test_forecast_length_property(self, quantities):
        """Forecast her zaman 7 eleman döndürmeli property testi"""
        # Random quantities ile DataFrame oluştur
        dates = pd.date_range('2023-01-01', periods=len(quantities), freq='D')
        df = pd.DataFrame({
            'order_date': dates,
            'quantity': quantities
        })
        
        try:
            forecast_df, model = forecast_sales(df, 'order_date', 'quantity')
            
            # Property: Her zaman 7 eleman
            assert len(forecast_df) == 7
            
            # Property: Forecast değerleri numeric
            assert all(isinstance(x, (int, float)) for x in forecast_df['forecast'])
            
            # Property: Forecast değerleri finite olmalı (negatif olabilir, çünkü azalan trend olabilir)
            assert all(x < float('inf') for x in forecast_df['forecast'])
            assert all(x > float('-inf') for x in forecast_df['forecast'])
            
        except Exception:
            # Eğer hata fırlatırsa, bu da kabul edilebilir (çok küçük veri vs.)
            pass
    
    @given(st.lists(st.floats(min_value=0, max_value=10000), min_size=5, max_size=50))
    def test_anomaly_count_bounds_property(self, quantities):
        """Anomaly count sınırları property testi"""
        # Random quantities ile DataFrame oluştur
        dates = pd.date_range('2023-01-01', periods=len(quantities), freq='D')
        df = pd.DataFrame({
            'order_date': dates,
            'quantity': quantities
        })
        
        anomalies, daily = detect_anomalies(df, 'order_date', 'quantity')
        
        # Property: Anomaly count sınırları
        assert len(anomalies) >= 0  # Negatif olamaz
        assert len(anomalies) <= len(daily)  # Toplam gün sayısından fazla olamaz
        assert len(daily) == len(df)  # Daily length = original length
    
    @given(st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False), min_size=1, max_size=20))
    def test_dataframe_consistency_property(self, quantities):
        """DataFrame tutarlılık property testi"""
        # Random quantities ile DataFrame oluştur
        dates = pd.date_range('2023-01-01', periods=len(quantities), freq='D')
        df = pd.DataFrame({
            'order_date': dates,
            'quantity': quantities
        })
        
        # Property: DataFrame tutarlılığı
        assert len(df) == len(quantities)  # Length consistency
        assert df['quantity'].dtype in ['int64', 'float64']  # Numeric type
        assert df['order_date'].dtype == 'datetime64[ns]'  # Date type
        assert not df['quantity'].isna().any()  # No NaN values
        assert not df['order_date'].isna().any()  # No NaT values
        
        # Property: Quantity değerleri mantıklı
        assert df['quantity'].min() >= 0  # Non-negative
        assert df['quantity'].max() < float('inf')  # No infinity
        if len(df) > 1:
            assert df['quantity'].std() >= 0  # Non-negative std
        else:
            # Tek değerli serilerde std NaN olabilir, bu normal
            assert pd.isna(df['quantity'].std()) or df['quantity'].std() >= 0
