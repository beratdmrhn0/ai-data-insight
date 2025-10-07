#!/bin/bash

echo "🚀 Building AI Data Insight Frontend..."

# Production image build
echo "📦 Building production image..."
docker build -t ai-data-insight-frontend:latest -f Dockerfile .

# Development image build
echo "🛠️ Building development image..."
docker build -t ai-data-insight-frontend:dev -f Dockerfile.dev .

echo "✅ Build completed!"

echo "✨ Available images:"
echo "  Production: ai-data-insight-frontend:latest"
echo "  Development: ai-data-insight-frontend:dev"

echo "🚀 Run commands:"
echo "  Production: docker run -p 80:80 ai-data-insight-frontend:latest"
echo "  Development: docker run -p 5173:5173 -v \$(pwd):/app ai-data-insight-frontend:dev"
