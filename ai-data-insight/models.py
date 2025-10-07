from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

class Tenant(Base):
    """Multi-tenant yapı için firma/şirket tablosu"""
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    domain = Column(String(255), unique=True, nullable=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="tenant")
    uploads = relationship("Upload", back_populates="tenant")

class User(Base):
    """Kullanıcı tablosu - tenant'a bağlı"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    uploads = relationship("Upload", back_populates="user")

class Upload(Base):
    """Dosya upload tablosu - tenant ve user'a bağlı"""
    __tablename__ = "uploads"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    status = Column(String(50), default="uploaded", index=True)
    
    # Foreign Keys
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="uploads")
    user = relationship("User", back_populates="uploads")
    analyses = relationship("Analysis", back_populates="upload")
    pipeline_histories = relationship("PipelineHistory", back_populates="upload")

class Analysis(Base):
    """Analiz sonuçları tablosu"""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=False)
    summary = Column(JSON, nullable=True)  # JSON field for summary stats
    insights = Column(JSON, nullable=True)  # JSON field for insights
    anomaly_count = Column(Integer, default=0)
    forecast_data = Column(JSON, nullable=True)  # JSON field for forecast results
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    upload = relationship("Upload", back_populates="analyses")

class PipelineHistory(Base):
    """Pipeline işlem geçmişi tablosu"""
    __tablename__ = "pipeline_histories"
    
    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=False)
    status = Column(String(50), nullable=False, index=True)
    message = Column(Text, nullable=True)
    execution_time = Column(Integer, nullable=True)  # milliseconds
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    upload = relationship("Upload", back_populates="pipeline_histories")

class Customer(Base):
    """Müşteri verileri tablosu - churn modelleme için"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(255), nullable=False, index=True)
    
    # Demografik bilgiler
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    segment = Column(String(100), nullable=True)
    
    # İş bilgileri
    subscription_length = Column(Integer, nullable=True)  # days
    last_login_date = Column(DateTime(timezone=True), nullable=True)
    total_orders = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    avg_order_value = Column(Float, default=0.0)
    
    # Churn hedef değişkeni
    churned = Column(Integer, nullable=True)  # 1: churned, 0: not churned
    
    # Tenant bilgisi
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant")

class MLModel(Base):
    """Machine Learning modelleri tablosu - tenant bazlı"""
    __tablename__ = "ml_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # "churn_model", "demand_forecast", etc.
    model_type = Column(String(100), nullable=False)  # "lightgbm", "sklearn", etc.
    
    # Model dosyası yolu ve metadata
    model_path = Column(String(500), nullable=False)
    model_version = Column(String(50), default="1.0")
    
    # Model performansı
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    
    # Feature bilgileri
    features = Column(JSON, nullable=True)  # Modelde kullanılan feature listesi
    feature_importance = Column(JSON, nullable=True)  # Feature importance scores
    
    # Training bilgileri
    training_data_size = Column(Integer, nullable=True)
    training_date = Column(DateTime(timezone=True), nullable=True)
    
    # Tenant bilgisi
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant")

class Prediction(Base):
    """Model tahminleri tablosu"""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Model ve müşteri referansları
    model_id = Column(Integer, ForeignKey("ml_models.id"), nullable=False)
    customer_id = Column(String(255), nullable=False, index=True)
    
    # Tahmin sonuçları
    prediction_value = Column(Float, nullable=False)  # Tahmin değeri (churn probability, etc.)
    confidence = Column(Float, nullable=True)  # Tahmin güveni
    
    # Input features (debugging için)
    input_features = Column(JSON, nullable=True)
    
    # Tenant bilgisi
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    model = relationship("MLModel")
    tenant = relationship("Tenant")

# Alembic için metadata
metadata = Base.metadata
