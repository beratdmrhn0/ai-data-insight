#!/bin/bash

# Docker build script for backend

echo "🐳 Building AI Data Insight Backend..."

# Production build
echo "📦 Building production image..."
docker build -f Dockerfile -t ai-data-insight-backend:latest .

# Development build
echo "🔧 Building development image..."
docker build -f Dockerfile.dev -t ai-data-insight-backend:dev .

echo "✅ Build completed!"
echo ""
echo "📋 Available images:"
echo "  Production: ai-data-insight-backend:latest"
echo "  Development: ai-data-insight-backend:dev"
echo ""
echo "🚀 Run commands:"
echo "  Production: docker run -p 8000:8000 ai-data-insight-backend:latest"
echo "  Development: docker run -p 8000:8000 -v \$(pwd):/app ai-data-insight-backend:dev"

