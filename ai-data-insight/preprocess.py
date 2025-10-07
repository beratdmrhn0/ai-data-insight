import pandas as pd
import numpy as np
import logging
from anomaly import detect_anomalies, detect_anomalies_customer
from forecast import forecast_sales, moving_average_forecast, naive_forecast

logger = logging.getLogger(__name__)

class Preprocessor:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.df = None

    def load(self):
        try:
            self.df = pd.read_csv(self.filepath)
            logger.info(f"Dosya yüklendi: {self.filepath} | {self.df.shape[0]} satır, {self.df.shape[1]} kolon")
        except Exception as e:
            logger.error(f"Dosya yükleme hatası: {e}")
            raise

    def clean_missing(self):
        if self.df is None:
            raise ValueError("DataFrame yüklenmedi.")
        
        # Basit strateji: sayısal kolonlarda ortalama, kategoriklerde en sık değer
        for col in self.df.columns:
            if self.df[col].dtype in [np.float64, np.int64]:
                self.df[col] = self.df[col].fillna(self.df[col].mean())
            else:
                mode_val = self.df[col].mode()
                if len(mode_val) > 0:
                    self.df[col] = self.df[col].fillna(mode_val[0])

    def parse_dates(self):
        if self.df is None:
            raise ValueError("DataFrame yüklenmedi.")
        
        for col in self.df.columns:
            if "date" in col.lower() or "tarih" in col.lower():
                try:
                    self.df[col] = pd.to_datetime(self.df[col], errors="coerce")
                except Exception as e:
                    logger.warning(f"{col} tarih parse edilemedi: {e}")

    def enforce_numeric(self):
        if self.df is None:
            raise ValueError("DataFrame yüklenmedi.")
        
        for col in self.df.columns:
            if self.df[col].dtype == object:
                try:
                    self.df[col] = pd.to_numeric(self.df[col])
                except:
                    pass  # string kolonlar bırakılacak

    def summary(self):
        if self.df is None:
            raise ValueError("DataFrame yüklenmedi.")
        
        return self.df.describe(include="all")

    def _find_date_column(self):
        """Tarih kolonunu akıllı tespit et"""
        date_keywords = [
            'date', 'time', 'created', 'order', 'timestamp', 'tarih', 
            'zaman', 'sipariş', 'registered', 'updated', 'modified'
        ]
        
        # Önce tam eşleşme ara
        for col in self.df.columns:
            col_lower = col.lower().strip()
            if col_lower in date_keywords:
                return col
        
        # Sonra kısmi eşleşme ara
        for col in self.df.columns:
            col_lower = col.lower().strip()
            for keyword in date_keywords:
                if keyword in col_lower:
                    return col
        
        # Son olarak pandas ile tarih tipini kontrol et
        for col in self.df.columns:
            if self.df[col].dtype == 'datetime64[ns]':
                return col
            # String kolonlarda tarih formatını kontrol et
            if self.df[col].dtype == 'object':
                try:
                    pd.to_datetime(self.df[col].dropna().head(10))
                    return col
                except:
                    pass
        
        return None

    def _find_quantity_column(self):
        """Miktar kolonunu akıllı tespit et"""
        qty_keywords = [
            'quantity', 'qty', 'amount', 'count', 'total', 'miktar',
            'adet', 'sayı', 'tutar', 'price', 'fiyat', 'sales', 'satış'
        ]
        
        # Önce tam eşleşme ara
        for col in self.df.columns:
            col_lower = col.lower().strip()
            if col_lower in qty_keywords:
                return col
        
        # Sonra kısmi eşleşme ara
        for col in self.df.columns:
            col_lower = col.lower().strip()
            for keyword in qty_keywords:
                if keyword in col_lower:
                    return col
        
        # Son olarak sayısal kolonları kontrol et
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            # En büyük varyansa sahip sayısal kolonu seç (muhtemelen miktar)
            variances = self.df[numeric_cols].var()
            return variances.idxmax() if not variances.empty else None
        
        return None

    def run(self):
        try:
            self.load()
            self.clean_missing()
            self.parse_dates()
            self.enforce_numeric()
            summary_stats = self.summary()
            
            # Anomali tespiti (e-ticaret verisi varsa)
            anomaly_count = 0
            date_col = None
            qty_col = None
            
            # Kolon isimlerini akıllı tespit et
            date_col = self._find_date_column()
            qty_col = self._find_quantity_column()
            
            logger.info(f"Tespit edilen kolonlar - Date: {date_col}, Quantity: {qty_col}")
            
            # Anomali tespiti (güvenli)
            if date_col and qty_col:
                try:
                    # Veri temizleme
                    self.df[qty_col] = pd.to_numeric(self.df[qty_col], errors="coerce").fillna(0)
                    
                    # Minimum veri kontrolü
                    if len(self.df) < 10:
                        logger.warning("Veri seti çok küçük, anomali tespiti atlanıyor")
                        anomaly_count = 0
                    else:
                        anomalies, daily = detect_anomalies(self.df, date_col, qty_col)
                        anomaly_count = len(anomalies)
                        logger.info(f"Anomali tespiti: {anomaly_count} anomali bulundu")
                except Exception as e:
                    logger.warning(f"Anomali tespiti başarısız: {e}")
                    anomaly_count = 0
            else:
                logger.info("Tarih veya miktar kolonu bulunamadı, anomali tespiti atlanıyor")
                anomaly_count = 0
            
            # Forecast (güvenli)
            forecast_values = []
            if date_col and qty_col:
                try:
                    # Veri temizleme
                    self.df[qty_col] = pd.to_numeric(self.df[qty_col], errors="coerce").fillna(0)
                    
                    # Minimum veri kontrolü
                    if len(self.df) < 5:
                        logger.warning("Veri seti çok küçük, forecast atlanıyor")
                        forecast_values = []
                    else:
                        forecast_df, model = forecast_sales(self.df, date_col, qty_col)
                        # NaN ve infinity değerlerini temizle
                        forecast_values = forecast_df["forecast"].replace([np.inf, -np.inf], np.nan).fillna(0).tolist()
                        logger.info(f"Forecast tamamlandı: {len(forecast_values)} günlük tahmin")
                except Exception as e:
                    logger.warning(f"Forecast başarısız: {e}")
                    forecast_values = []
            else:
                logger.info("Tarih veya miktar kolonu bulunamadı, forecast atlanıyor")
                forecast_values = []
            
            # Summary stats'ı JSON uyumlu hale getir
            summary_dict = summary_stats.to_dict()
            for col in summary_dict:
                for stat in summary_dict[col]:
                    value = summary_dict[col][stat]
                    if pd.isna(value):
                        summary_dict[col][stat] = 0
                    elif isinstance(value, (int, float)) and (np.isinf(value) or np.isnan(value)):
                        summary_dict[col][stat] = 0
            
            logger.info("Preprocessing tamamlandı.")
            return self.df, summary_dict, anomaly_count, forecast_values
        except Exception as e:
            logger.error(f"Preprocessing hatası: {e}")
            raise


if __name__ == "__main__":
    pre = Preprocessor("sample_orders.csv")
    df, summary = pre.run()
    print(summary)
