from sqlalchemy import create_engine, text as sa_text
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
import logging

logger = logging.getLogger(__name__)

# PostgreSQL engine oluştur (StaticPool KULLANMA)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # bozuk bağlantıları otomatik yenile
    pool_size=5,          # temel havuz boyutu
    max_overflow=10,      # yoğunlukta ekstra bağlantı
    echo=False            # Production'da False olmalı
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Database'i başlat ve tabloları oluştur"""
    try:
        # Tüm tabloları oluştur
        from models import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

def check_db_connection():
    """Database bağlantısını test et"""
    try:
        with engine.connect() as connection:
            connection.execute(sa_text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
