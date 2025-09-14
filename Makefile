# Brevo Email Automation Makefile
# Simplify common development and deployment tasks

.PHONY: help install setup run test clean deploy lint format

# Default target
help:
	@echo "Brevo Email Automation - Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  make install     - Install dependencies"
	@echo "  make setup       - Initial project setup"
	@echo "  make run         - Start development servers"
	@echo "  make test        - Run tests"
	@echo "  make lint        - Run linting"
	@echo "  make format      - Format code"
	@echo ""
	@echo "Deployment:"
	@echo "  make build       - Build for production"
	@echo "  make deploy      - Deploy to production"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean       - Clean temporary files"
	@echo "  make backup      - Create backup"
	@echo "  make logs        - Show application logs"
	@echo "  make health      - Check application health"

# Installation
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt

install-dev:
	@echo "Installing development dependencies..."
	pip install -r requirements.txt
	pip install pytest black flake8 mypy pre-commit

# Setup
setup: install
	@echo "Setting up project..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env file from template"; \
		echo "⚠️  Please edit .env with your actual credentials"; \
	fi
	@mkdir -p logs temp backups output
	@echo "✅ Created necessary directories"
	@echo "Setup complete! Run 'make run' to start the application."

# Development
run:
	@echo "Starting development servers..."
	@echo "API Server: http://localhost:5000"
	@echo "UI Dashboard: http://localhost:8501"
	@echo "API Docs: http://localhost:5000/docs"
	@echo ""
	@echo "Starting API server..."
	@uvicorn user_retention_api:app --host 0.0.0.0 --port 5000 --reload &
	@echo "Starting UI dashboard..."
	@streamlit run streamlit_app.py &
	@echo "Servers started. Press Ctrl+C to stop."

run-api:
	@echo "Starting API server..."
	uvicorn user_retention_api:app --host 0.0.0.0 --port 5000 --reload

run-ui:
	@echo "Starting UI dashboard..."
	streamlit run streamlit_app.py

# Testing
test:
	@echo "Running tests..."
	pytest tests/ -v --cov=. --cov-report=html

test-unit:
	@echo "Running unit tests..."
	pytest tests/unit/ -v

test-integration:
	@echo "Running integration tests..."
	pytest tests/integration/ -v

# Code Quality
lint:
	@echo "Running linting..."
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:
	@echo "Formatting code..."
	black . --line-length 88
	isort .

type-check:
	@echo "Running type checking..."
	mypy . --ignore-missing-imports

# Production Build
build:
	@echo "Building for production..."
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "✅ Environment file found"
	docker build -t brevo-automation:latest .
	@echo "✅ Docker image built"

build-compose:
	@echo "Building with Docker Compose..."
	docker-compose build

# Deployment
deploy: build
	@echo "Deploying to production..."
	docker-compose up -d
	@echo "✅ Deployment complete"
	@echo "Application available at:"
	@echo "  - API: http://your-server:5000"
	@echo "  - UI: http://your-server:8501"

deploy-aws:
	@echo "Deploying to AWS..."
	@echo "Building Docker image..."
	docker build -t brevo-automation .
	@echo "Pushing to ECR..."
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com
	docker tag brevo-automation:latest your-account.dkr.ecr.us-east-1.amazonaws.com/brevo-automation:latest
	docker push your-account.dkr.ecr.us-east-1.amazonaws.com/brevo-automation:latest
	@echo "Updating ECS service..."
	aws ecs update-service --cluster brevo-cluster --service brevo-service --force-new-deployment
	@echo "✅ AWS deployment complete"

# Maintenance
clean:
	@echo "Cleaning temporary files..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf temp/*
	rm -rf output/*
	@echo "✅ Cleanup complete"

clean-all: clean
	@echo "Cleaning all generated files..."
	rm -rf logs/*
	rm -rf backups/*
	rm -rf .env
	@echo "✅ Full cleanup complete"

backup:
	@echo "Creating backup..."
	@mkdir -p backups
	@BACKUP_FILE=backups/backup_$(shell date +%Y%m%d_%H%M%S).tar.gz; \
	tar -czf $$BACKUP_FILE .env logs/ temp/ --exclude='*.log' || true; \
	echo "✅ Backup created: $$BACKUP_FILE"

# Monitoring
logs:
	@echo "Showing application logs..."
	docker-compose logs -f

logs-api:
	@echo "Showing API logs..."
	docker-compose logs -f api

logs-ui:
	@echo "Showing UI logs..."
	docker-compose logs -f ui

health:
	@echo "Checking application health..."
	@curl -f http://localhost:5000/health && echo "✅ API healthy" || echo "❌ API unhealthy"
	@curl -f http://localhost:8501/health && echo "✅ UI healthy" || echo "❌ UI unhealthy"

status:
	@echo "Application status:"
	@echo "=================="
	@docker-compose ps
	@echo ""
	@echo "Disk usage:"
	@df -h | grep -E "(Filesystem|%)"
	@echo ""
	@echo "Memory usage:"
	@free -h

# Database
db-backup:
	@echo "Creating database backup..."
	@mkdir -p backups/db
	@mongodump --uri="$$(grep MONGO_URI .env | cut -d'=' -f2)" --out=backups/db/$(shell date +%Y%m%d_%H%M%S)
	@echo "✅ Database backup complete"

db-restore:
	@echo "Restoring database from latest backup..."
	@LATEST_BACKUP=$$(ls -td backups/db/*/ | head -1); \
	if [ -z "$$LATEST_BACKUP" ]; then \
		echo "❌ No backup found"; \
		exit 1; \
	fi; \
	mongorestore --uri="$$(grep MONGO_URI .env | cut -d'=' -f2)" --drop $$LATEST_BACKUP; \
	echo "✅ Database restored from $$LATEST_BACKUP"

# Development Tools
pre-commit:
	@echo "Setting up pre-commit hooks..."
	pre-commit install
	pre-commit run --all-files

update-deps:
	@echo "Updating dependencies..."
	pip install --upgrade -r requirements.txt
	pip list --outdated

# Docker
docker-clean:
	@echo "Cleaning Docker resources..."
	docker system prune -f
	docker volume prune -f
	docker image prune -f

# Environment
env-check:
	@echo "Checking environment configuration..."
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found"; \
		exit 1; \
	fi
	@echo "✅ .env file exists"
	@python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('✅ Environment variables loaded')"
	@echo "Required variables:"
	@grep -E "^(BREVO_API_KEY|MONGO_URI|USER_RETENTION_API_URL)=" .env | sed 's/=.*//' | sed 's/^/  ✅ /' || echo "  ❌ Some required variables missing"

# Help for specific commands
help-%:
	@echo "Help for '$*':"
	@grep -A5 -B1 "^$*:" Makefile | sed 's/^# //' | sed 's/^$*://' | sed 's/^/  /'

# Version
version:
	@echo "Brevo Email Automation v1.2.0"
	@echo "Last updated: September 14, 2025"

# Emergency stop
stop:
	@echo "Stopping all services..."
	@pkill -f uvicorn || true
	@pkill -f streamlit || true
	@docker-compose down || true
	@echo "✅ All services stopped"