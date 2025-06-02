# PollenPal API Makefile
# Cross-platform convenience commands

.PHONY: help install dev test build deploy clean

# Default target
help:
	@echo "PollenPal API - Available Commands"
	@echo ""
	@echo "Development:"
	@echo "  make install    Install dependencies"
	@echo "  make dev        Start development server"
	@echo "  make test       Run all tests"
	@echo "  make lint       Check code quality"
	@echo "  make lint-fix   Fix code formatting"
	@echo ""
	@echo "Production:"
	@echo "  make build      Build Docker image"
	@echo "  make deploy     Deploy to production"
	@echo "  make start      Start production services"
	@echo "  make stop       Stop all services"
	@echo "  make logs       View service logs"
	@echo "  make status     Show service status"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean      Clean Docker resources"
	@echo "  make health     Check service health"
	@echo ""
	@echo "Alternative: python scripts/run.py <command>"

# Development commands
install:
	python scripts/run.py install

dev:
	python scripts/run.py dev

test:
	python scripts/run.py test

lint:
	python scripts/run.py lint

lint-fix:
	python scripts/run.py lint:fix

# Production commands
build:
	python scripts/run.py build

deploy:
	python scripts/run.py deploy

start:
	python scripts/run.py start

stop:
	python scripts/run.py stop

restart:
	python scripts/run.py restart

logs:
	python scripts/run.py logs

status:
	python scripts/run.py status

# Utility commands
clean:
	python scripts/run.py clean

health:
	python scripts/run.py health

# Docker-specific commands
docker-dev:
	python scripts/run.py dev:docker

docker-test:
	python scripts/run.py test:docker

# Testing variants
test-unit:
	python scripts/run.py test:unit

test-integration:
	python scripts/run.py test:integration

test-docker:
	python scripts/run.py test:docker 