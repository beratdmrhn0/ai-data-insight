# 🐳 Docker Kurulum ve Kullanım Rehberi

## 📋 **Hızlı Başlangıç**

### **1. Development Ortamı (Hot Reload)**
```bash
# Development servisleri başlat
docker-compose -f docker-compose.dev.yml up -d

# Logları izle
docker-compose -f docker-compose.dev.yml logs -f
```

**Erişim URL'leri:**
- Frontend: http://localhost:5173 (Vite dev server)
- Backend: http://localhost:8000
- Database: localhost:5432

### **2. Production Ortamı**
```bash
# Production servisleri başlat
docker-compose -f docker-compose.prod.yml up -d

# Logları izle
docker-compose -f docker-compose.prod.yml logs -f
```

**Erişim URL'leri:**
- Frontend: http://localhost:80 (Nginx)
- Backend: http://localhost:8000
- Database: Sadece internal network

## 🛠️ **Docker Komutları**

### **Build İşlemleri**
```bash
# Tüm servisleri build et
docker-compose build

# Development build
docker-compose -f docker-compose.dev.yml build

# Production build
docker-compose -f docker-compose.prod.yml build
```

### **Servis Yönetimi**
```bash
# Servisleri başlat
docker-compose up -d

# Servisleri durdur
docker-compose down

# Servisleri yeniden başlat
docker-compose restart

# Belirli bir servisi yeniden başlat
docker-compose restart backend
```

### **Log ve Debug**
```bash
# Tüm logları görüntüle
docker-compose logs -f

# Belirli servisin logları
docker-compose logs -f backend

# Container'a bağlan
docker-compose exec backend bash
docker-compose exec database psql -U postgres -d ai_data_insight
```

## 🧪 **Test ve Geliştirme**

### **Test Çalıştırma**
```bash
# Container içinde test çalıştır
docker-compose -f docker-compose.dev.yml exec backend python -m pytest tests/ -v

# Integration testleri
docker-compose -f docker-compose.dev.yml exec backend python -m pytest tests/test_integration.py -v
```

### **Database İşlemleri**
```bash
# Database'e bağlan
docker-compose exec database psql -U postgres -d ai_data_insight

# Database backup
docker-compose exec database pg_dump -U postgres ai_data_insight > backup.sql

# Database restore
docker-compose exec -T database psql -U postgres ai_data_insight < backup.sql
```

## 🔧 **Konfigürasyon**

### **Environment Variables**
```bash
# .env dosyası oluştur
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
DATABASE_URL=postgresql://postgres:postgres123@database:5432/ai_data_insight
```

### **Volume Mounting**
```yaml
# Development için volume mounting
volumes:
  - ./ai-data-insight:/app          # Hot reload için
  - ./ai-data-insight/uploads:/app/uploads
  - ./ai-data-insight/models:/app/models
```

## 🚀 **Production Deployment**

### **SSL/HTTPS Kurulumu**
```bash
# SSL sertifikalarını nginx/ssl/ klasörüne koy
# nginx.conf dosyasını SSL için güncelle
docker-compose -f docker-compose.prod.yml up -d
```

### **Monitoring ve Logging**
```bash
# Log dosyalarını görüntüle
docker-compose -f docker-compose.prod.yml logs nginx
docker-compose -f docker-compose.prod.yml logs backend

# Container resource kullanımı
docker stats
```

## 🧹 **Temizlik**

### **Container ve Image Temizliği**
```bash
# Tüm containerları ve imageları sil
docker-compose down --rmi all --volumes --remove-orphans

# Sadece volume'ları sil
docker-compose down --volumes

# Kullanılmayan volume'ları temizle
docker volume prune -f
```

### **Sistem Temizliği**
```bash
# Kullanılmayan imageları sil
docker image prune -f

# Kullanılmayan containerları sil
docker container prune -f

# Tüm Docker sistem temizliği
docker system prune -f
```

## 🔍 **Troubleshooting**

### **Yaygın Sorunlar**

**1. Port Conflict**
```bash
# Port kullanımını kontrol et
netstat -tulpn | grep :8000
netstat -tulpn | grep :5432

# Farklı port kullan
docker-compose up -d --scale backend=0
docker-compose up -d --scale backend=1
```

**2. Database Bağlantı Sorunu**
```bash
# Database container'ının çalıştığını kontrol et
docker-compose ps database

# Database loglarını kontrol et
docker-compose logs database

# Database'e manuel bağlan
docker-compose exec database psql -U postgres
```

**3. Volume Mount Sorunu**
```bash
# Volume'ları kontrol et
docker volume ls

# Volume detaylarını görüntüle
docker volume inspect saas_postgres_data
```

## 📊 **Performance Monitoring**

### **Resource Kullanımı**
```bash
# Container resource kullanımı
docker stats

# Disk kullanımı
docker system df

# Container detayları
docker inspect <container_name>
```

### **Log Rotation**
```yaml
# docker-compose.yml'de log rotation
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## 🎯 **Best Practices**

1. **Development**: `docker-compose.dev.yml` kullan
2. **Production**: `docker-compose.prod.yml` kullan
3. **Secrets**: `.env` dosyası kullan, asla hardcode etme
4. **Backup**: Database'i düzenli backup al
5. **Monitoring**: Logları düzenli kontrol et
6. **Security**: SSL sertifikalarını güncel tut

## 🔗 **Faydalı Linkler**

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Nginx Docker Image](https://hub.docker.com/_/nginx)
- [FastAPI Docker Guide](https://fastapi.tiangolo.com/deployment/docker/)
