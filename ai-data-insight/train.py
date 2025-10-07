"""
LightGBM Churn Model Trainer
Multi-tenant churn prediction model training script
"""

import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score, confusion_matrix, f1_score, precision_recall_fscore_support
import joblib
import os
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from database import SessionLocal
from models import Customer, MLModel, Tenant

logger = logging.getLogger(__name__)

class ChurnTrainer:
    def __init__(self, tenant_id: int):
        self.tenant_id = tenant_id
        self.db = SessionLocal()
        self.model = None
        self.features = None
        self.feature_importance = None
        
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()
    
    def load_customer_data(self):
        """Tenant'a ait müşteri verilerini yükle"""
        try:
            customers = self.db.query(Customer).filter(
                Customer.tenant_id == self.tenant_id,
                Customer.churned.isnot(None)  # Sadece churn bilgisi olan müşteriler
            ).all()
            
            if not customers:
                raise ValueError(f"Tenant {self.tenant_id} için churn verisi bulunamadı")
            
            # DataFrame'e çevir
            data = []
            for customer in customers:
                data.append({
                    'id': customer.id,
                    'customer_id': customer.customer_id,
                    'age': customer.age,
                    'gender': customer.gender,
                    'segment': customer.segment,
                    'subscription_length': customer.subscription_length,
                    'last_login_date': customer.last_login_date,
                    'total_orders': customer.total_orders,
                    'total_spent': customer.total_spent,
                    'avg_order_value': customer.avg_order_value,
                    'churned': customer.churned
                })
            
            df = pd.DataFrame(data)
            logger.info(f"Tenant {self.tenant_id} için {len(df)} müşteri verisi yüklendi")
            return df
            
        except Exception as e:
            logger.error(f"Veri yükleme hatası: {e}")
            raise
    
    def feature_engineering(self, df):
        """Feature engineering işlemleri"""
        logger.info("Feature engineering başlatılıyor...")
        
        # Kopya oluştur
        df_processed = df.copy()
        
        # 1. Tarih feature'ları
        if 'last_login_date' in df_processed.columns:
            df_processed['last_login_date'] = pd.to_datetime(df_processed['last_login_date'], utc=True)
            current_date = datetime.now().replace(tzinfo=None)
            df_processed['days_since_last_login'] = (current_date - df_processed['last_login_date'].dt.tz_localize(None)).dt.days
            df_processed['days_since_last_login'] = df_processed['days_since_last_login'].fillna(365)  # Hiç login olmamışsa 365 gün
        else:
            df_processed['days_since_last_login'] = 365
        
        # 2. Subscription length feature
        if 'subscription_length' in df_processed.columns:
            df_processed['subscription_length'] = df_processed['subscription_length'].fillna(0)
        else:
            df_processed['subscription_length'] = 0
        
        # 3. Demografik feature'lar
        df_processed['age'] = df_processed['age'].fillna(df_processed['age'].median())
        df_processed['gender'] = df_processed['gender'].fillna('Unknown')
        df_processed['segment'] = df_processed['segment'].fillna('Unknown')
        
        # 4. İş feature'ları
        df_processed['total_orders'] = df_processed['total_orders'].fillna(0)
        df_processed['total_spent'] = df_processed['total_spent'].fillna(0.0)
        df_processed['avg_order_value'] = df_processed['avg_order_value'].fillna(0.0)
        
        # 5. Categorical encoding (One-hot encoding)
        categorical_cols = ['gender', 'segment']
        for col in categorical_cols:
            if col in df_processed.columns:
                dummies = pd.get_dummies(df_processed[col], prefix=col)
                df_processed = pd.concat([df_processed, dummies], axis=1)
                df_processed.drop(col, axis=1, inplace=True)
        
        # 6. Numeric feature'ları seç
        feature_cols = [
            'age', 'subscription_length', 'days_since_last_login',
            'total_orders', 'total_spent', 'avg_order_value'
        ]
        
        # Categorical dummy column'ları ekle
        categorical_dummies = [col for col in df_processed.columns if any(cat in col for cat in ['gender_', 'segment_'])]
        feature_cols.extend(categorical_dummies)
        
        # Mevcut olan feature'ları seç
        available_features = [col for col in feature_cols if col in df_processed.columns]
        
        # Target variable
        target_col = 'churned'
        
        # Feature ve target'ı ayır
        X = df_processed[available_features]
        y = df_processed[target_col]
        
        self.features = available_features
        logger.info(f"Feature engineering tamamlandı. {len(available_features)} feature kullanılıyor: {available_features}")
        
        return X, y
    
    def train_model(self, X, y, test_size=0.2, random_state=42):
        """LightGBM model eğitimi"""
        logger.info("Model eğitimi başlatılıyor...")
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # LightGBM parameters
        params = {
            'objective': 'binary',
            'metric': 'auc',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1,
            'random_state': random_state,
            # Sınıf dengesizliği için
            'is_unbalance': True
        }
        
        # LightGBM dataset
        train_data = lgb.Dataset(X_train, label=y_train)
        test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)
        
        # Model eğitimi
        self.model = lgb.train(
            params,
            train_data,
            valid_sets=[test_data],
            num_boost_round=100,
            callbacks=[lgb.early_stopping(stopping_rounds=10), lgb.log_evaluation(0)]
        )
        
        # Feature importance (int32'yi int'e çevir)
        importance_values = self.model.feature_importance()
        self.feature_importance = dict(zip(self.features, [int(x) for x in importance_values]))
        
        # Model değerlendirme + En iyi eşik seçimi (F1 maksimize)
        y_pred_proba = self.model.predict(X_test)
        best_threshold = 0.5
        best_f1 = -1.0
        best_prec = 0.0
        best_rec = 0.0
        for thr in [x / 100.0 for x in range(10, 90)]:  # 0.10..0.89
            preds = (y_pred_proba >= thr).astype(int)
            precision, recall, f1, _ = precision_recall_fscore_support(y_test, preds, average='binary', zero_division=0)
            if f1 > best_f1:
                best_f1 = f1
                best_threshold = thr
                best_prec = precision
                best_rec = recall

        # Nihai metrikler (seçilen eşikle)
        y_pred = (y_pred_proba >= best_threshold).astype(int)
        accuracy = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_pred_proba)

        logger.info(f"Model eğitimi tamamlandı. Accuracy: {accuracy:.3f}, AUC: {auc:.3f}, F1(best): {best_f1:.3f} @ thr={best_threshold:.2f}")

        return {
            'accuracy': accuracy,
            'auc': auc,
            'precision': best_prec,
            'recall': best_rec,
            'f1_score': best_f1,
            'threshold': best_threshold,
            'classification_report': classification_report(y_test, y_pred),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'feature_importance': self.feature_importance
        }
    
    def save_model(self, metrics):
        """Modeli ve metadata'yı kaydet"""
        try:
            # Model dosyası yolu
            model_dir = f"./models/tenant_{self.tenant_id}"
            os.makedirs(model_dir, exist_ok=True)
            
            model_path = f"{model_dir}/churn_model.pkl"
            
            # Modeli kaydet
            joblib.dump(self.model, model_path)
            
            # Database'de model kaydını oluştur/güncelle
            existing_model = self.db.query(MLModel).filter(
                MLModel.tenant_id == self.tenant_id,
                MLModel.name == "churn_model",
                MLModel.is_active == True
            ).first()
            
            if existing_model:
                # Mevcut modeli pasif yap
                existing_model.is_active = False
                self.db.commit()
            
            # Yeni model kaydı
            # Eşik bilgisini feature_importance dict'ine özel anahtarla ekle
            feature_importance_with_threshold = dict(self.feature_importance or {})
            feature_importance_with_threshold['__threshold__'] = float(metrics.get('threshold', 0.5))

            new_model = MLModel(
                name="churn_model",
                model_type="lightgbm",
                model_path=model_path,
                model_version="1.0",
                accuracy=metrics['accuracy'],
                precision=metrics.get('precision'),
                recall=metrics.get('recall'),
                f1_score=metrics.get('f1_score'),
                features=self.features,
                feature_importance=feature_importance_with_threshold,
                training_data_size=len(self.db.query(Customer).filter(Customer.tenant_id == self.tenant_id).all()),
                training_date=datetime.now(),
                tenant_id=self.tenant_id,
                is_active=True
            )
            
            self.db.add(new_model)
            self.db.commit()
            
            logger.info(f"Model başarıyla kaydedildi: {model_path}")
            return new_model.id
            
        except Exception as e:
            logger.error(f"Model kaydetme hatası: {e}")
            self.db.rollback()
            raise

def train_churn_model(tenant_id: int):
    """Churn model eğitimi ana fonksiyonu"""
    try:
        trainer = ChurnTrainer(tenant_id)
        
        # 1. Veri yükleme
        df = trainer.load_customer_data()
        
        # 2. Feature engineering
        X, y = trainer.feature_engineering(df)
        
        # 3. Model eğitimi
        metrics = trainer.train_model(X, y)
        
        # 4. Model kaydetme
        model_id = trainer.save_model(metrics)
        
        return {
            'success': True,
            'model_id': model_id,
            'metrics': metrics,
            'message': f'Tenant {tenant_id} için churn modeli başarıyla eğitildi'
        }
        
    except Exception as e:
        logger.error(f"Churn model eğitimi hatası: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f'Tenant {tenant_id} için churn modeli eğitilemedi'
        }

if __name__ == "__main__":
    # Test için
    import sys
    if len(sys.argv) > 1:
        tenant_id = int(sys.argv[1])
        result = train_churn_model(tenant_id)
        print(result)
    else:
        print("Kullanım: python train.py <tenant_id>")