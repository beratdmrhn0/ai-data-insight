.PHONY: help build build-dev build-prod up up-dev up-prod down down-dev down-prod logs logs-dev logs-prod test clean

# Docker Compose Files
COMPOSE_FILE = docker-compose.yml
COMPOSE_DEV_FILE = docker-compose.dev.yml
COMPOSE_PROD_FILE = docker-compose.prod.yml

# Service Names
SERVICES = backend frontend database
SERVICES_DEV = backend frontend database
SERVICES_PROD = backend frontend database nginx

# --- Help ---
help:
	@echo "🚀 AI Data Insight Docker Commands"
	@echo ""
	@echo "📦 Build Commands:"
	@echo "  build        - Build all images"
	@echo "  build-dev    - Build development images"
	@echo "  build-prod   - Build production images"
	@echo ""
	@echo "🚀 Run Commands:"
	@echo "  up           - Start all services (production)"
	@echo "  up-dev       - Start all services (development with hot reload)"
	@echo "  up-prod      - Start all services (production with nginx)"
	@echo ""
	@echo "🛑 Stop Commands:"
	@echo "  down         - Stop all services"
	@echo "  down-dev     - Stop development services"
	@echo "  down-prod    - Stop production services"
	@echo ""
	@echo "📋 Log Commands:"
	@echo "  logs         - Show all logs"
	@echo "  logs-dev     - Show development logs"
	@echo "  logs-prod    - Show production logs"
	@echo ""
	@echo "🧪 Test Commands:"
	@echo "  test         - Run tests in container"
	@echo "  test-integration - Run integration tests"
	@echo ""
	@echo "🧹 Clean Commands:"
	@echo "  clean        - Clean up containers and images"
	@echo "  clean-volumes - Clean up volumes"

# --- Build Commands ---
build:
	docker-compose -f $(COMPOSE_FILE) build

build-dev:
	docker-compose -f $(COMPOSE_DEV_FILE) build

build-prod:
	docker-compose -f $(COMPOSE_PROD_FILE) build

# --- Run Commands ---
up:
	docker-compose -f $(COMPOSE_FILE) up -d

up-dev:
	docker-compose -f $(COMPOSE_DEV_FILE) up -d

up-prod:
	docker-compose -f $(COMPOSE_PROD_FILE) up -d

# --- Stop Commands ---
down:
	docker-compose -f $(COMPOSE_FILE) down

down-dev:
	docker-compose -f $(COMPOSE_DEV_FILE) down

down-prod:
	docker-compose -f $(COMPOSE_PROD_FILE) down

# --- Log Commands ---
logs:
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-dev:
	docker-compose -f $(COMPOSE_DEV_FILE) logs -f

logs-prod:
	docker-compose -f $(COMPOSE_PROD_FILE) logs -f

# --- Test Commands ---
test:
	docker-compose -f $(COMPOSE_DEV_FILE) exec backend python -m pytest tests/ -v

test-integration:
	docker-compose -f $(COMPOSE_DEV_FILE) exec backend python -m pytest tests/test_integration.py -v

# --- Clean Commands ---
clean:
	docker-compose -f $(COMPOSE_FILE) down --rmi all --volumes --remove-orphans
	docker-compose -f $(COMPOSE_DEV_FILE) down --rmi all --volumes --remove-orphans
	docker-compose -f $(COMPOSE_PROD_FILE) down --rmi all --volumes --remove-orphans

clean-volumes:
	docker-compose -f $(COMPOSE_FILE) down --volumes
	docker-compose -f $(COMPOSE_DEV_FILE) down --volumes
	docker-compose -f $(COMPOSE_PROD_FILE) down --volumes
	docker volume prune -f

# --- Utility Commands ---
shell-backend:
	docker-compose -f $(COMPOSE_DEV_FILE) exec backend bash

shell-db:
	docker-compose -f $(COMPOSE_DEV_FILE) exec database psql -U postgres -d ai_data_insight_dev

status:
	docker-compose -f $(COMPOSE_FILE) ps
	docker-compose -f $(COMPOSE_DEV_FILE) ps
	docker-compose -f $(COMPOSE_PROD_FILE) ps
