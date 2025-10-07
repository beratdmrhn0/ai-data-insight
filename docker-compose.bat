@echo off
setlocal

if "%1"=="" (
    echo.
    echo Usage: docker-compose.bat [command]
    echo.
    echo Commands:
    echo   build        - Build all images
    echo   build-dev    - Build development images  
    echo   build-prod   - Build production images
    echo   up           - Start all services (production)
    echo   up-dev       - Start all services (development with hot reload)
    echo   up-prod      - Start all services (production with nginx)
    echo   down         - Stop all services
    echo   down-dev     - Stop development services
    echo   down-prod    - Stop production services
    echo   logs         - Show all logs
    echo   logs-dev     - Show development logs
    echo   logs-prod    - Show production logs
    echo   test         - Run tests in container
    echo   clean        - Clean up containers and images
    echo.
    goto :eof
)

if "%1"=="build" (
    echo 📦 Building all images...
    docker-compose -f docker-compose.yml build
) else if "%1"=="build-dev" (
    echo 🛠️ Building development images...
    docker-compose -f docker-compose.dev.yml build
) else if "%1"=="build-prod" (
    echo 🚀 Building production images...
    docker-compose -f docker-compose.prod.yml build
) else if "%1"=="up" (
    echo 🚀 Starting all services (production)...
    docker-compose -f docker-compose.yml up -d
) else if "%1"=="up-dev" (
    echo 🛠️ Starting all services (development)...
    docker-compose -f docker-compose.dev.yml up -d
) else if "%1"=="up-prod" (
    echo 🚀 Starting all services (production with nginx)...
    docker-compose -f docker-compose.prod.yml up -d
) else if "%1"=="down" (
    echo 🛑 Stopping all services...
    docker-compose -f docker-compose.yml down
) else if "%1"=="down-dev" (
    echo 🛑 Stopping development services...
    docker-compose -f docker-compose.dev.yml down
) else if "%1"=="down-prod" (
    echo 🛑 Stopping production services...
    docker-compose -f docker-compose.prod.yml down
) else if "%1"=="logs" (
    echo 📋 Showing all logs...
    docker-compose -f docker-compose.yml logs -f
) else if "%1"=="logs-dev" (
    echo 📋 Showing development logs...
    docker-compose -f docker-compose.dev.yml logs -f
) else if "%1"=="logs-prod" (
    echo 📋 Showing production logs...
    docker-compose -f docker-compose.prod.yml logs -f
) else if "%1"=="test" (
    echo 🧪 Running tests in container...
    docker-compose -f docker-compose.dev.yml exec backend python -m pytest tests/ -v
) else if "%1"=="clean" (
    echo 🧹 Cleaning up containers and images...
    docker-compose -f docker-compose.yml down --rmi all --volumes --remove-orphans
    docker-compose -f docker-compose.dev.yml down --rmi all --volumes --remove-orphans
    docker-compose -f docker-compose.prod.yml down --rmi all --volumes --remove-orphans
) else (
    echo ❌ Unknown command: %1
    goto :eof
)

echo.
echo ✅ Command completed.
endlocal
