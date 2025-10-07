from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import os
import shutil
import uuid
import pandas as pd
import json
from joblib import load
from preprocess import Preprocessor
import asyncio
import threading
from contextlib import asynccontextmanager

# Import our new modules
from database import get_db, init_db, check_db_connection, SessionLocal
from models import Upload, Analysis, PipelineHistory, Tenant, User, Customer, MLModel, Prediction
from auth import get_current_user, get_current_tenant, create_user, authenticate_user
from config import UPLOAD_DIR, SECRET_KEY

# Import ML modules
from train import train_churn_model
from predict import predict_churn

def run_scheduler():
    """Scheduler fonksiyonu - her saat çalışır"""
    while True:
        try:
            db = SessionLocal()
            try:
                uploads = db.query(Upload).filter(Upload.status == "uploaded").all()
                for u in uploads:
                    process_pipeline(u.id)
            finally:
                db.close()
        except Exception as e:
            print(f"Scheduler error: {e}")
        threading.Event().wait(3600)  # 1 saat bekle

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting AI Data Insight API...")
    
    # Initialize database
    init_db()
    
    # Check database connection
    if not check_db_connection():
        print("❌ Database connection failed!")
        raise Exception("Database connection failed")
    
    print("✅ Database connected successfully")
    
    # Start scheduler
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    yield
    
    # Shutdown
    print("🛑 Shutting down AI Data Insight API...")

# Create uploads directory
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Load ML model
MODEL_PATH = "./models/demand_model.joblib"
if os.path.exists(MODEL_PATH):
    model = load(MODEL_PATH)
else:
    model = None

def simple_analysis(file_path: str):
    """Basit analiz fonksiyonu"""
    df = pd.read_csv(file_path)
    summary = {
        "rows": len(df),
        "columns": list(df.columns),
        "last_order_date": str(df["order_date"].max()) if "order_date" in df.columns else None
    }

    insights = {}
    if "sku" in df.columns and "quantity" in df.columns:
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0)
        top_skus = df.groupby("sku")["quantity"].sum().sort_values(ascending=False).head(5)
        insights["top_skus"] = top_skus.to_dict()

    if "customer_id" in df.columns and "order_date" in df.columns:
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
        last_dates = df.groupby("customer_id")["order_date"].max()
        cutoff = df["order_date"].max() - pd.Timedelta(days=90)
        at_risk = last_dates[last_dates < cutoff]
        insights["churn_at_risk_count"] = int(len(at_risk))

    anomalies = []
    if "sku" in df.columns and "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        for sku, g in df.groupby("sku"):
            if len(g) < 5: continue
            mean = g["price"].mean()
            std = g["price"].std()
            outliers = g[(g["price"] > mean + 3*std) | (g["price"] < mean - 3*std)]
            for idx, row in outliers.iterrows():
                anomalies.append({"sku": sku, "row_index": int(idx), "price": float(row["price"])})
    insights["anomalies"] = anomalies

    return summary, insights

def process_upload(upload_id: int, file_path: str, db: Session):
    """Upload işleme fonksiyonu"""
    upload = db.query(Upload).filter(Upload.id == upload_id).first()
    if upload:
        upload.status = "processing"
        db.commit()

        # Create pipeline history
        history = PipelineHistory(
            upload_id=upload_id,
            status="processing",
            message="Dosya analiz ediliyor..."
        )
        db.add(history)
        db.commit()

    try:
        summary, insights = simple_analysis(file_path)
        
        # Create analysis record
        analysis = Analysis(
            upload_id=upload_id,
            summary=json.dumps(summary),
            insights=json.dumps(insights)
        )
        db.add(analysis)
        
        # Update upload status
        upload.status = "ready"
        db.commit()
        
        # Update pipeline history
        history.status = "completed"
        history.message = "Analiz tamamlandı"
        db.commit()
        
    except Exception as e:
        # Update upload status to failed
        upload.status = "failed"
        db.commit()
        
        # Update pipeline history
        history.status = "failed"
        history.message = f"Analiz hatası: {str(e)}"
        db.commit()
        raise

def process_pipeline(upload_id: int):
    """Pipeline işleme fonksiyonu"""
    db = SessionLocal()
    try:
        upload = db.query(Upload).filter(Upload.id == upload_id).first()
        if not upload:
            return

        # Create pipeline history
        history = PipelineHistory(
            upload_id=upload_id,
            status="started"
        )
        db.add(history)
        db.commit()

        try:
            # Preprocessing
            pre = Preprocessor(upload.path)
            df, summary_stats, anomaly_count, forecast_values = pre.run()

            # Update history with preprocessing results
            history.status = "preprocessing_completed"
            history.message = f"Preprocessing tamamlandı. Kayıt: {len(df)}, Anomali: {anomaly_count}"
            db.commit()

            # ML Model Prediction (if model exists)
            if model and "sku" in df.columns and "quantity" in df.columns and "order_date" in df.columns:
                try:
                    # Feature engineering for prediction
                    df["order_date"] = pd.to_datetime(df["order_date"])
                    df["month"] = df["order_date"].dt.month
                    df["day_of_week"] = df["order_date"].dt.dayofweek
                    df["day_of_year"] = df["order_date"].dt.dayofyear

                    model_features = ["quantity", "price", "month", "day_of_week", "day_of_year"]
                    for feature in model_features:
                        if feature not in df.columns:
                            df[feature] = 0
                        df[feature] = pd.to_numeric(df[feature], errors="coerce").fillna(0)

                    X = df[model_features]
                    predictions = model.predict(X)

                    history.status = "prediction_completed"
                    history.message = f"Tahmin tamamlandı. {len(predictions)} tahmin üretildi."
                    db.commit()

                except Exception as e:
                    history.status = "prediction_failed"
                    history.message = f"Tahmin hatası: {str(e)}"
                    db.commit()
                    print(f"Prediction error for upload {upload_id}: {e}")

            # Final status update
            upload.status = "completed"
            history.status = "completed"
            history.message = "Tüm pipeline tamamlandı."
            db.commit()

        except Exception as e:
            upload.status = "failed"
            history.status = "failed"
            history.message = f"Pipeline hatası: {str(e)}"
            db.commit()
            print(f"Pipeline error for upload {upload_id}: {e}")
    finally:
        db.close()

app = FastAPI(
    title="AI Data Insight MVP",
    description="Multi-tenant AI Data Analysis Platform",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development için tüm origin'lere izin ver
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "message": "AI Data Insight API v2.0 - Multi-tenant ready"}

@app.post("/api/v1/upload")
async def upload_csv(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """CSV dosyası upload endpoint'i - Multi-tenant aware"""
    try:
        if not file.filename.lower().endswith(".csv"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sadece CSV dosyaları kabul ediliyor"
            )

        uid = str(uuid.uuid4())
        path = os.path.join(UPLOAD_DIR, f"{uid}_{file.filename}")

        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Create upload record with default tenant and user (development)
        upload = Upload(
            filename=file.filename,
            path=path,
            status="uploaded",
            tenant_id=2,  # Default test tenant
            user_id=2     # Default test user
        )
        db.add(upload)
        db.commit()
        db.refresh(upload)

        # Create pipeline history
        history = PipelineHistory(
            upload_id=upload.id,
            status="started",
            message=f"Upload başlatıldı: {file.filename}"
        )
        db.add(history)
        db.commit()

        # Start background processing
        background_tasks.add_task(process_upload, upload.id, path, db)

        return {
            "upload_id": upload.id,
            "status": "uploaded",
            "tenant_id": 2,  # Default test tenant
            "user_id": 2     # Default test user
        }
    except Exception as e:
        print(f"Upload error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload hatası: {str(e)}"
        )

@app.get("/api/v1/upload/{upload_id}/status")
def upload_status(
    upload_id: int,
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """Upload durumu endpoint'i - Multi-tenant aware"""
    upload = db.query(Upload).filter(
        Upload.id == upload_id,
        Upload.tenant_id == current_tenant.id
    ).first()
    
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload bulunamadı"
        )
    
    return {
        "upload_id": upload.id,
        "status": upload.status,
        "tenant_id": upload.tenant_id
    }

@app.get("/api/v1/upload/{upload_id}/result")
def get_analysis_result(
    upload_id: int,
    db: Session = Depends(get_db)
):
    """Analiz sonucu endpoint'i - Development için basitleştirildi"""
    upload = db.query(Upload).filter(Upload.id == upload_id).first()
    
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload bulunamadı"
        )
    
    analysis = db.query(Analysis).filter(Analysis.upload_id == upload_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analiz sonucu bulunamadı"
        )
    
    return {
        "upload_id": analysis.upload_id,
        "summary": json.loads(analysis.summary) if analysis.summary else {},
        "insights": json.loads(analysis.insights) if analysis.insights else {}
    }

@app.get("/api/v1/pipeline/history")
def pipeline_history(
    db: Session = Depends(get_db)
):
    """Pipeline geçmişi endpoint'i - Development için basitleştirildi"""
    # Get all pipeline histories
    histories = db.query(PipelineHistory).order_by(PipelineHistory.created_at.desc()).limit(10).all()
    
    return [
        {
            "upload_id": h.upload_id,
            "status": h.status,
            "created_at": str(h.created_at),
            "message": h.message
        } for h in histories
    ]

@app.post("/api/v1/preprocess/{upload_id}")
def preprocess_file(
    upload_id: int,
    db: Session = Depends(get_db)
):
    """Preprocess endpoint'i - Development için basitleştirildi"""
    try:
        upload = db.query(Upload).filter(Upload.id == upload_id).first()
        
        if not upload:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Upload bulunamadı"
            )

        pre = Preprocessor(upload.path)
        df, summary, anomaly_count, forecast_values = pre.run()

        return {
            "upload_id": upload_id,
            "record_count": len(df),
            "column_count": df.shape[1],
            "anomaly_count": anomaly_count,
            "forecast": forecast_values,
            "summary_stats": summary
        }
    except Exception as e:
        print(f"Preprocessing hatası: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Preprocessing hatası: {str(e)}"
        )

# Auth endpoints
@app.post("/api/v1/auth/register")
def register_user(
    email: str,
    password: str,
    full_name: str,
    tenant_name: str,
    db: Session = Depends(get_db)
):
    """Kullanıcı kayıt endpoint'i"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email adresi zaten kullanılıyor"
        )
    
    # Create or get tenant
    tenant = db.query(Tenant).filter(Tenant.name == tenant_name).first()
    if not tenant:
        tenant = Tenant(name=tenant_name, domain=tenant_name.lower().replace(" ", "_"))
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
    
    # Create user
    user = create_user(email, password, full_name, tenant.id, db)
    
    return {
        "user_id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "tenant_id": user.tenant_id,
        "message": "Kullanıcı başarıyla oluşturuldu"
    }

@app.post("/api/v1/auth/login")
def login_user(
    login_data: dict,
    db: Session = Depends(get_db)
):
    """Kullanıcı giriş endpoint'i"""
    email = login_data.get("email")
    password = login_data.get("password")
    
    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ve şifre gerekli"
        )
    
    user = authenticate_user(email, password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz email veya şifre"
        )
    
    # Create access token
    from auth import create_access_token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "tenant_id": user.tenant_id
    }

# Churn Model Endpoints
@app.post("/api/v1/churn/train")
def train_churn(
    db: Session = Depends(get_db)
):
    """Churn model eğitimi endpoint'i"""
    try:
        # Churn verisi var mı kontrol et
        customer_count = db.query(Customer).filter(
            Customer.tenant_id == 2,  # Default test tenant
            Customer.churned.isnot(None)
        ).count()

        if customer_count < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Model eğitimi için en az 10 müşteri verisi gerekli. Mevcut: {customer_count}"
            )

        # Model eğitimi
        result = train_churn_model(2)  # Default test tenant
        
        if result['success']:
            return {
                "message": result['message'],
                "model_id": result['model_id'],
                "metrics": result['metrics']
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result['error']
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Churn model eğitimi hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model eğitimi hatası: {str(e)}"
        )

@app.post("/api/v1/churn/predict")
def predict_churn_endpoint(
    customer_data: dict,
    db: Session = Depends(get_db)
):
    """Churn tahmini endpoint'i"""
    try:
        # Model var mı kontrol et
        model = db.query(MLModel).filter(
            MLModel.tenant_id == 2,  # Default test tenant
            MLModel.name == "churn_model",
            MLModel.is_active == True
        ).first()

        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aktif churn modeli bulunamadı. Önce model eğitimi yapın."
            )

        # Tahmin yap
        result = predict_churn(2, customer_data)  # Default test tenant
        
        if result['success']:
            return {
                "message": result['message'],
                "prediction": result['result'],
                "model_info": {
                    "model_id": model.id,
                    "version": model.model_version,
                    "accuracy": model.accuracy
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result['error']
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Churn tahmin hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tahmin hatası: {str(e)}"
        )

@app.get("/api/v1/churn/models")
def get_churn_models(
    db: Session = Depends(get_db)
):
    """Churn modellerini listele - Development için basitleştirildi"""
    models = db.query(MLModel).filter(
        MLModel.tenant_id == 2,  # Default test tenant
        MLModel.name == "churn_model"
    ).order_by(MLModel.created_at.desc()).all()
    
    return [
        {
            "id": model.id,
            "version": model.model_version,
            "accuracy": model.accuracy,
            "training_date": model.training_date,
            "is_active": model.is_active,
            "training_data_size": model.training_data_size,
            "features": model.features
        } for model in models
    ]

@app.get("/api/v1/churn/predictions")
def get_churn_predictions(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Churn tahminlerini listele - Development için basitleştirildi"""
    predictions = db.query(Prediction).filter(
        Prediction.tenant_id == 2  # Default test tenant
    ).order_by(Prediction.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": pred.id,
            "customer_id": pred.customer_id,
            "churn_probability": pred.prediction_value,
            "confidence": pred.confidence,
            "created_at": pred.created_at,
            "model_id": pred.model_id
        } for pred in predictions
    ]

@app.post("/api/v1/churn/customers")
def add_customer_data(
    customer_data: dict,
    db: Session = Depends(get_db)
):
    """Müşteri verisi ekleme endpoint'i"""
    try:
        # Gerekli alanları kontrol et
        required_fields = ['customer_id', 'age', 'gender', 'segment']
        for field in required_fields:
            if field not in customer_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Gerekli alan eksik: {field}"
                )
        
        # Müşteri zaten var mı kontrol et
        existing_customer = db.query(Customer).filter(
            Customer.customer_id == customer_data['customer_id'],
            Customer.tenant_id == 2  # Default test tenant
        ).first()

        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bu müşteri ID'si zaten mevcut"
            )

        # Müşteri kaydı oluştur
        customer = Customer(
            customer_id=customer_data['customer_id'],
            age=customer_data.get('age'),
            gender=customer_data.get('gender'),
            segment=customer_data.get('segment'),
            subscription_length=customer_data.get('subscription_length'),
            last_login_date=customer_data.get('last_login_date'),
            total_orders=customer_data.get('total_orders', 0),
            total_spent=customer_data.get('total_spent', 0.0),
            avg_order_value=customer_data.get('avg_order_value', 0.0),
            churned=customer_data.get('churned'),
            tenant_id=2  # Default test tenant
        )
        
        db.add(customer)
        db.commit()
        db.refresh(customer)
        
        return {
            "message": "Müşteri verisi başarıyla eklendi",
            "customer_id": customer.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Müşteri ekleme hatası: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Müşteri ekleme hatası: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
