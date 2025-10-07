from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, create_engine, Session, select
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

def run_scheduler():
    """Scheduler fonksiyonu - her saat çalışır"""
    while True:
        try:
            with Session(engine) as session:
                uploads = session.exec(select(Upload).where(Upload.status == "uploaded")).all()
                for u in uploads:
                    process_pipeline(u.id)
        except Exception as e:
            print(f"Scheduler error: {e}")
        threading.Event().wait(3600)  # 1 saat bekle

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    yield
    # Shutdown
    pass

DATABASE_URL = "sqlite:///./app.db"  # MVP için SQLite
engine = create_engine(DATABASE_URL, echo=False)

class Upload(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    filename: str
    path: str
    status: str = "uploaded"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Analysis(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    upload_id: int
    summary: str | None = None   # JSON string
    insights: str | None = None  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PipelineHistory(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    upload_id: int
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    message: str | None = None

# DB oluştur
SQLModel.metadata.create_all(engine)

# Upload klasörü
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Model yükleme
MODEL_PATH = "./models/demand_model.joblib"
if os.path.exists(MODEL_PATH):
    model = load(MODEL_PATH)
else:
    model = None

def simple_analysis(file_path: str):
    df = pd.read_csv(file_path)
    summary = {
        "rows": len(df),
        "columns": list(df.columns),
        "last_order_date": str(df["order_date"].max()) if "order_date" in df.columns else None
    }

    insights = {}
    # Top 5 SKUs by quantity
    if "sku" in df.columns and "quantity" in df.columns:
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0)
        top_skus = df.groupby("sku")["quantity"].sum().sort_values(ascending=False).head(5)
        insights["top_skus"] = top_skus.to_dict()

    # Churn heuristic: last_order per customer >90 gün önce
    if "customer_id" in df.columns and "order_date" in df.columns:
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
        last_dates = df.groupby("customer_id")["order_date"].max()
        cutoff = df["order_date"].max() - pd.Timedelta(days=90)
        at_risk = last_dates[last_dates < cutoff]
        insights["churn_at_risk_count"] = int(len(at_risk))

    # Anomali tespiti: price z-score > 3
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

def process_upload(upload_id: int, file_path: str):
    with Session(engine) as session:
        upload = session.get(Upload, upload_id)
        if upload:
            upload.status = "processing"
            session.add(upload)
            # Pipeline history'yi güncelle
            history = session.exec(
                select(PipelineHistory).where(PipelineHistory.upload_id == upload_id)
                .order_by(PipelineHistory.created_at.desc())
            ).first()
            if history:
                history.status = "processing"
                history.message = "Dosya analiz ediliyor..."
                session.add(history)
            session.commit()

    try:
        summary, insights = simple_analysis(file_path)
        with Session(engine) as session:
            analysis = Analysis(upload_id=upload_id,
                                summary=json.dumps(summary),
                                insights=json.dumps(insights))
            session.add(analysis)
            # upload status update
            upload = session.get(Upload, upload_id)
            if upload:
                upload.status = "ready"
                session.add(upload)
            # Pipeline history'yi başarılı olarak güncelle
            history = session.exec(
                select(PipelineHistory).where(PipelineHistory.upload_id == upload_id)
                .order_by(PipelineHistory.created_at.desc())
            ).first()
            if history:
                history.status = "completed"
                history.message = "Analiz tamamlandı"
                session.add(history)
            session.commit()
    except Exception as e:
        with Session(engine) as session:
            upload = session.get(Upload, upload_id)
            if upload:
                upload.status = "failed"
                session.add(upload)
            # Pipeline history'yi başarısız olarak güncelle
            history = session.exec(
                select(PipelineHistory).where(PipelineHistory.upload_id == upload_id)
                .order_by(PipelineHistory.created_at.desc())
            ).first()
            if history:
                history.status = "failed"
                history.message = f"Analiz hatası: {str(e)}"
                session.add(history)
            session.commit()
        raise

def process_pipeline(upload_id: int):
    with Session(engine) as session:
        upload = session.get(Upload, upload_id)
        if not upload:
            return

        # History kaydı
        history = PipelineHistory(upload_id=upload_id, status="started")
        session.add(history)
        session.commit()

        try:
            # Analiz
            summary, insights = simple_analysis(upload.path)
            analysis = Analysis(upload_id=upload_id,
                                summary=json.dumps(summary),
                                insights=json.dumps(insights))
            session.add(analysis)

            # Prediction
            if model:
                df = pd.read_csv(upload.path)
                df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)
                X = pd.get_dummies(df[["sku", "price"]])
                model_features = model.feature_names_in_
                for col in model_features:
                    if col not in X.columns:
                        X[col] = 0
                X = X[model_features]
                y_pred = model.predict(X)
                analysis.insights = json.dumps({**insights, "predictions": y_pred.tolist()})

            # Upload status update
            upload.status = "ready"
            session.add(upload)

            # History güncelle
            history.status = "completed"
            session.add(history)
            session.commit()
        except Exception as e:
            history.status = "failed"
            history.message = str(e)
            upload.status = "failed"
            session.add_all([history, upload])
            session.commit()
            raise

app = FastAPI(title="AI Data Insight MVP", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def root():
    return {"status": "ok", "message": "Proje iskeleti hazır"}

@app.post("/api/v1/upload")
async def upload_csv(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        if not file.filename.lower().endswith(".csv"):
            return {"error": "Sadece CSV kabul ediliyor"}

        uid = str(uuid.uuid4())
        path = os.path.join(UPLOAD_DIR, f"{uid}_{file.filename}")

        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        upload_id = None
        with Session(engine) as session:
            upload = Upload(filename=file.filename, path=path, status="uploaded")
            session.add(upload)
            session.commit()
            session.refresh(upload)
            upload_id = upload.id
            
            # Pipeline history kaydı oluştur
            history = PipelineHistory(
                upload_id=upload_id,
                status="started",
                message=f"Upload başlatıldı: {file.filename}"
            )
            session.add(history)
            session.commit()

        # arka plan analizi başlat
        background_tasks.add_task(process_upload, upload_id, path)

        return {"upload_id": upload_id, "status": "uploaded"}
    except Exception as e:
        print(f"Upload error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Upload hatası: {str(e)}"}

@app.get("/api/v1/upload/{upload_id}/status")
def upload_status(upload_id: int):
    with Session(engine) as session:
        upload = session.get(Upload, upload_id)
        if not upload:
            return {"error": "Upload bulunamadı"}
        return {"upload_id": upload.id, "status": upload.status, "filename": upload.filename}

@app.get("/api/v1/upload/{upload_id}/result")
def upload_result(upload_id: int):
    with Session(engine) as session:
        res = session.exec(
            select(Analysis).where(Analysis.upload_id == upload_id)
        ).first()
        if not res:
            return {"status": "no_result"}
        return {"analysis_id": res.id,
                "summary": json.loads(res.summary),
                "insights": json.loads(res.insights)}

@app.post("/api/v1/predict")
def predict_demand(file: UploadFile = File(...)):
    import pandas as pd
    global model
    if model is None:
        return {"error": "Model henüz eğitilmedi"}

    df = pd.read_csv(file.file)
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)
    X = pd.get_dummies(df[["sku", "price"]])
    # eksik sütunları model ile eşle
    model_features = model.feature_names_in_
    for col in model_features:
        if col not in X.columns:
            X[col] = 0
    X = X[model_features]

    y_pred = model.predict(X)
    return {"predictions": y_pred.tolist()}

@app.get("/api/v1/pipeline/history")
def pipeline_history():
    with Session(engine) as session:
        histories = session.exec(select(PipelineHistory).order_by(PipelineHistory.created_at.desc())).all()
        return [
            {
                "upload_id": h.upload_id,
                "status": h.status,
                "created_at": str(h.created_at),
                "message": h.message
            } for h in histories
        ]

@app.post("/api/v1/preprocess/{upload_id}")
def preprocess_file(upload_id: int):
    try:
        # Upload dosyasını bul
        with Session(engine) as session:
            upload = session.get(Upload, upload_id)
            if not upload:
                return {"error": "Upload bulunamadı"}
            
            # Preprocessing çalıştır
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
        return {"error": f"Preprocessing hatası: {str(e)}", "details": str(e)}
