# Multi-stage build için Dockerfile
# Stage 1: Dependencies
FROM python:3.11-slim as dependencies

# Sistem paketlerini güncelle ve gerekli araçları yükle
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizinini ayarla
WORKDIR /app

# Python dependencies'leri kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Production image
FROM python:3.11-slim as production

# Çalışma dizinini ayarla
WORKDIR /app

# Dependencies'leri önceki stage'den kopyala
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Uygulama kodunu kopyala
COPY main.py .
COPY preprocess.py .
COPY anomaly.py .
COPY forecast.py .
COPY train.py .
COPY sample_orders.csv .

# Uploads dizinini oluştur
RUN mkdir -p uploads

# Port'u expose et
EXPOSE 8000

# Health check ekle
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/')" || exit 1

# Uygulamayı başlat
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

