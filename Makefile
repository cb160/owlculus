# Owlculus Container Management
.PHONY: help setup setup-dev start start-dev stop restart logs clean build rebuild test

COMPOSE ?= $(shell ./scripts/detect-compose.sh 2>/dev/null)

ifeq ($(strip $(COMPOSE)),)
$(error Unable to locate a compose implementation. Install Docker Compose or Podman Compose, or set COMPOSE="your command")
endif

CONTAINER_RUNTIME := $(firstword $(COMPOSE))

ifeq ($(CONTAINER_RUNTIME),docker-compose)
CONTAINER_RUNTIME := docker
endif

ifeq ($(CONTAINER_RUNTIME),podman-compose)
CONTAINER_RUNTIME := podman
endif

# Default target
help:
	@echo "🦉 Owlculus Container Management"
	@echo ""
	@echo "Available commands:"
	@echo "  setup       - Initial setup with containers (production)"
	@echo "  setup-dev   - Initial setup with containers (development)"
	@echo "  start       - Start all services (production)"
	@echo "  start-dev   - Start all services (development)"
	@echo "  stop        - Stop all services"
	@echo "  restart     - Restart all services"
	@echo "  logs        - View service logs"
	@echo "  build       - Build Docker images"
	@echo "  rebuild     - Rebuild Docker images (no cache)"
	@echo "  clean       - Stop and remove all containers, networks, and volumes"
	@echo "  test        - Run backend tests"
	@echo ""

# Setup commands
setup:
	@echo "🚀 Setting up Owlculus (production)..."
	./setup.sh production

setup-dev:
	@echo "🚀 Setting up Owlculus (development)..."
	./setup.sh dev

# Service management
start:
	@echo "▶️  Starting Owlculus (production)..."
	$(COMPOSE) up -d

start-dev:
	@echo "▶️  Starting Owlculus (development)..."
	$(COMPOSE) -f docker-compose.dev.yml up -d

stop:
	@echo "⏹️  Stopping Owlculus..."
	$(COMPOSE) down
	$(COMPOSE) -f docker-compose.dev.yml down

restart:
	@echo "🔄 Restarting Owlculus..."
	$(COMPOSE) restart
	$(COMPOSE) -f docker-compose.dev.yml restart

# Monitoring
logs:
	@echo "📋 Viewing service logs (Ctrl+C to exit)..."
	$(COMPOSE) logs -f

# Build commands
build:
	@echo "🔨 Building Docker images..."
	$(COMPOSE) build

rebuild:
	@echo "🔨 Rebuilding Docker images (no cache)..."
	$(COMPOSE) build --no-cache
	$(COMPOSE) -f docker-compose.dev.yml build --no-cache

# Cleanup
clean:
	@echo "🧹 Cleaning up all Docker resources..."
	@echo "⚠️  This will destroy all data! Press Ctrl+C to cancel..."
	@sleep 5
	$(COMPOSE) down -v --remove-orphans
	$(COMPOSE) -f docker-compose.dev.yml down -v --remove-orphans
	$(CONTAINER_RUNTIME) system prune -f

# Testing
test:
	@echo "🧪 Running backend tests..."
	$(COMPOSE) exec backend python3 -m pytest tests/ -v

# Development helpers
shell-backend:
	@echo "🐚 Opening backend shell..."
	$(COMPOSE) exec backend bash

shell-db:
	@echo "🐚 Opening database shell..."
	$(COMPOSE) exec postgres psql -U owlculus -d owlculus

# Status
status:
	@echo "📊 Service Status:"
	$(COMPOSE) ps
