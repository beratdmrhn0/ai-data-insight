# Stage 1: Build Stage - Node.js ile build işlemi
FROM node:20-alpine AS builder

WORKDIR /app

# Package dosyalarını kopyala
COPY package*.json ./

# Bağımlılıkları yükle
RUN npm ci --only=production

# Kaynak kodunu kopyala
COPY . .

# Production build
RUN npm run build

# Stage 2: Production Stage - Nginx ile static serve
FROM nginx:alpine AS production

# Nginx config dosyasını kopyala
COPY nginx.conf /etc/nginx/nginx.conf

# Build edilmiş dosyaları builder stage'den kopyala
COPY --from=builder /app/dist /usr/share/nginx/html

# Port 80'i aç
EXPOSE 80

# Nginx'i başlat
CMD ["nginx", "-g", "daemon off;"]
