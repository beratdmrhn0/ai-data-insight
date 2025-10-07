"""
LightGBM Churn Prediction
Multi-tenant churn prediction script
"""

import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from database import SessionLocal
from models import MLModel, Prediction, Customer

logger = logging.getLogger(__name__)

class ChurnPredictor:
    def __init__(self, tenant_id: int):
        self.tenant_id = tenant_id
        self.db = SessionLocal()
        self.model = None
        self.features = None
        self.model_record = None
        
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()
    
    def load_model(self):
        """Tenant'a ait aktif churn modelini yükle"""
        try:
            # Database'den model bilgilerini al
            self.model_record = self.db.query(MLModel).filter(
                MLModel.tenant_id == self.tenant_id,
                MLModel.name == "churn_model",
                MLModel.is_active == True
            ).first()
            
            if not self.model_record:
                raise ValueError(f"Tenant {self.tenant_id} için aktif churn modeli bulunamadı")
            
            # Model dosyasını yükle
            if not os.path.exists(self.model_record.model_path):
                raise FileNotFoundError(f"Model dosyası bulunamadı: {self.model_record.model_path}")
            
            self.model = joblib.load(self.model_record.model_path)
            self.features = self.model_record.features
            # Kaydedilen threshold'u metadata'dan al (feature_importance içine __threshold__ eklenmişti)
            self.threshold = 0.5
            try:
                fi = self.model_record.feature_importance or {}
                if isinstance(fi, dict) and '__threshold__' in fi:
                    self.threshold = float(fi['__threshold__'])
            except Exception:
                self.threshold = 0.5
            
            logger.info(f"Model başarıyla yüklendi. Model ID: {self.model_record.id}")
            return True
            
        except Exception as e:
            logger.error(f"Model yükleme hatası: {e}")
            raise
    
    def prepare_features(self, customer_data):
        """Müşteri verilerini model için hazırla"""
        try:
            # Input validation
            required_fields = ['age', 'gender', 'segment', 'subscription_length', 'last_login_date']
            for field in required_fields:
                if field not in customer_data:
                    raise ValueError(f"Gerekli alan eksik: {field}")
            
            # DataFrame oluştur
            df = pd.DataFrame([customer_data])
            
            # Feature engineering (train.py ile aynı işlemler)
            df_processed = df.copy()
            
            # 1. Tarih feature'ları
            df_processed['last_login_date'] = pd.to_datetime(df_processed['last_login_date'], utc=True)
            current_date = datetime.now().replace(tzinfo=None)
            df_processed['days_since_last_login'] = (current_date - df_processed['last_login_date'].dt.tz_localize(None)).dt.days
            df_processed['days_since_last_login'] = df_processed['days_since_last_login'].fillna(365)
            
            # 2. Subscription length
            df_processed['subscription_length'] = df_processed['subscription_length'].fillna(0)
            
            # 3. Demografik feature'lar
            df_processed['age'] = df_processed['age'].fillna(df_processed['age'].median())
            df_processed['gender'] = df_processed['gender'].fillna('Unknown')
            df_processed['segment'] = df_processed['segment'].fillna('Unknown')
            
            # 4. İş feature'ları (varsayılan değerler)
            df_processed['total_orders'] = customer_data.get('total_orders', 0)
            df_processed['total_spent'] = customer_data.get('total_spent', 0.0)
            df_processed['avg_order_value'] = customer_data.get('avg_order_value', 0.0)
            
            # 5. Categorical encoding (One-hot encoding)
            categorical_cols = ['gender', 'segment']
            for col in categorical_cols:
                if col in df_processed.columns:
                    dummies = pd.get_dummies(df_processed[col], prefix=col)
                    df_processed = pd.concat([df_processed, dummies], axis=1)
                    df_processed.drop(col, axis=1, inplace=True)
            
            # 6. Feature'ları model ile aynı sırada hazırla
            feature_cols = [
                'age', 'subscription_length', 'days_since_last_login',
                'total_orders', 'total_spent', 'avg_order_value'
            ]
            
            # Categorical dummy column'ları ekle
            categorical_dummies = [col for col in df_processed.columns if any(cat in col for cat in ['gender_', 'segment_'])]
            feature_cols.extend(categorical_dummies)
            
            # Model feature'ları ile eşleştir
            X = pd.DataFrame(index=[0])
            for feature in self.features:
                if feature in df_processed.columns:
                    X[feature] = df_processed[feature].iloc[0]
                else:
                    X[feature] = 0  # Eksik feature için 0
            
            # Feature'ları model ile aynı sırada düzenle
            X = X[self.features]
            
            return X
            
        except Exception as e:
            logger.error(f"Feature hazırlama hatası: {e}")
            raise
    
    def predict_churn(self, customer_data):
        """Churn tahmini yap"""
        try:
            # Model yüklü değilse yükle
            if self.model is None:
                self.load_model()
            
            # Feature'ları hazırla
            X = self.prepare_features(customer_data)
            
            # Tahmin yap
            churn_probability = self.model.predict(X)[0]
            
            # Confidence hesapla (basit bir yaklaşım)
            confidence = min(max(abs(churn_probability - 0.5) * 2, 0.1), 0.9)
            
            logger.info(f"Churn tahmini tamamlandı. Probability: {churn_probability:.3f}")
            
            thr = getattr(self, 'threshold', 0.5)
            return {
                'churn_probability': float(churn_probability),
                'confidence': float(confidence),
                'prediction': 'High Risk' if churn_probability >= max(thr, 0.7) else ('Medium Risk' if churn_probability >= thr else 'Low Risk'),
                'threshold': float(thr)
            }
            
        except Exception as e:
            logger.error(f"Churn tahmin hatası: {e}")
            raise
    
    def save_prediction(self, customer_id, prediction_result, input_features):
        """Tahmin sonucunu database'e kaydet"""
        try:
            prediction = Prediction(
                model_id=self.model_record.id,
                customer_id=customer_id,
                prediction_value=prediction_result['churn_probability'],
                confidence=prediction_result['confidence'],
                input_features=input_features,
                tenant_id=self.tenant_id
            )
            
            self.db.add(prediction)
            self.db.commit()
            
            logger.info(f"Tahmin sonucu kaydedildi. Prediction ID: {prediction.id}")
            return prediction.id
            
        except Exception as e:
            logger.error(f"Tahmin kaydetme hatası: {e}")
            self.db.rollback()
            raise

def predict_churn(tenant_id: int, customer_data: dict, save_result: bool = True):
    """Churn tahmini ana fonksiyonu"""
    try:
        predictor = ChurnPredictor(tenant_id)
        
        # Tahmin yap
        result = predictor.predict_churn(customer_data)
        
        # Sonucu kaydet
        if save_result:
            customer_id = customer_data.get('customer_id', f"temp_{datetime.now().timestamp()}")
            prediction_id = predictor.save_prediction(customer_id, result, customer_data)
            result['prediction_id'] = prediction_id
        
        return {
            'success': True,
            'result': result,
            'message': 'Churn tahmini başarıyla tamamlandı'
        }
        
    except Exception as e:
        logger.error(f"Churn tahmin hatası: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': 'Churn tahmini yapılamadı'
        }

if __name__ == "__main__":
    # Test için
    import sys
    if len(sys.argv) > 1:
        tenant_id = int(sys.argv[1])
        
        # Test müşteri verisi
        test_customer = {
            'customer_id': 'test_001',
            'age': 35,
            'gender': 'Male',
            'segment': 'Premium',
            'subscription_length': 365,
            'last_login_date': '2024-01-01',
            'total_orders': 10,
            'total_spent': 1500.0,
            'avg_order_value': 150.0
        }
        
        result = predict_churn(tenant_id, test_customer)
        print(result)
    else:
        print("Kullanım: python predict.py <tenant_id>")
