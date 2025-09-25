# Coventure.es URL Shortener Backend Makefile

.PHONY: help setup install dev prod clean test test-api lint format check requirements docker-build docker-run docker-stop logs backup restore

# Default target
.DEFAULT_GOAL := help

# Python and virtual environment paths
PYTHON := python3
VENV := venv
VENV_BIN := $(VENV)/bin
PIP := $(VENV_BIN)/pip
PYTHON_VENV := $(VENV_BIN)/python
UVICORN := $(VENV_BIN)/uvicorn

# Application settings
APP_MODULE := main:app
HOST := 0.0.0.0
DEV_PORT := 8000
PROD_PORT := 8000

# Database settings
DB_FILE := url_shortener.db
BACKUP_DIR := backups

help: ## Show this help message
	@echo "Coventure.es URL Shortener Backend"
	@echo "=================================="
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Create virtual environment and install dependencies
	@echo "🔧 Setting up development environment..."
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt
	@echo "✅ Setup complete! Virtual environment created at ./$(VENV)"

install: ## Install/update dependencies (assumes venv exists)
	@echo "📦 Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt
	@echo "✅ Development dependencies installed!"

install-prod: ## Install production dependencies
	@echo "📦 Installing production dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "✅ Production dependencies installed!"

dev: ## Run development server with auto-reload
	@echo "🚀 Starting development server on http://$(HOST):$(DEV_PORT)"
	@echo "📝 Auto-reload enabled - edit files and see changes instantly"
	$(UVICORN) $(APP_MODULE) --reload --host $(HOST) --port $(DEV_PORT) --log-level debug

prod: ## Run production server
	@echo "🏭 Starting production server on http://$(HOST):$(PROD_PORT)"
	$(UVICORN) $(APP_MODULE) --host $(HOST) --port $(PROD_PORT) --workers 4

dev-bg: ## Run development server in background
	@echo "🚀 Starting development server in background..."
	nohup $(UVICORN) $(APP_MODULE) --reload --host $(HOST) --port $(DEV_PORT) > server.log 2>&1 &
	@echo "✅ Server started! Check logs with 'make logs'"

stop: ## Stop background development server
	@echo "🛑 Stopping development server..."
	@pkill -f "uvicorn.*$(APP_MODULE)" || echo "No server process found"

clean: ## Clean database and temporary files
	@echo "🧹 Cleaning up..."
	rm -f $(DB_FILE)
	rm -f *.log
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	@echo "✅ Cleanup complete!"

test: ## Run API health check
	@echo "🏥 Testing API health..."
	@curl -s -f "http://localhost:$(DEV_PORT)/api/health" | python3 -m json.tool || echo "❌ Health check failed - is the server running?"

test-api: ## Run comprehensive API tests
	@echo "🧪 Running comprehensive API tests..."
	@echo ""
	@echo "1️⃣ Health Check:"
	@curl -s -f "http://localhost:$(DEV_PORT)/api/health" | python3 -m json.tool || echo "❌ Health check failed"
	@echo ""
	@echo "2️⃣ URL Shortening Test:"
	@curl -s -X POST "http://localhost:$(DEV_PORT)/api/shorten" \
		-H "Content-Type: application/json" \
		-d '{"url": "https://github.com/welhox"}' | python3 -m json.tool || echo "❌ URL shortening failed"
	@echo ""
	@echo "3️⃣ Custom Code Test:"
	@curl -s -X POST "http://localhost:$(DEV_PORT)/api/shorten" \
		-H "Content-Type: application/json" \
		-d '{"url": "https://example.com", "custom_code": "test123"}' | python3 -m json.tool || echo "❌ Custom code test failed"
	@echo ""
	@echo "✅ API tests complete!"

test-redirect: ## Test redirect functionality
	@echo "🔄 Testing redirect functionality..."
	@echo "Creating a test URL first..."
	@RESPONSE=$$(curl -s -X POST "http://localhost:$(DEV_PORT)/api/shorten" \
		-H "Content-Type: application/json" \
		-d '{"url": "https://github.com/welhox", "custom_code": "redirect-test"}') && \
	echo "$$RESPONSE" | python3 -m json.tool && \
	echo "" && \
	echo "Testing redirect..." && \
	curl -s -w "Status: %{http_code} | Redirect: %{redirect_url}\n" "http://localhost:$(DEV_PORT)/redirect-test"

lint: ## Check code style with flake8 (install with: pip install flake8)
	@echo "🔍 Checking code style..."
	@$(VENV_BIN)/flake8 --version > /dev/null 2>&1 || (echo "Installing flake8..." && $(PIP) install flake8)
	$(VENV_BIN)/flake8 *.py --max-line-length=120 --ignore=E501,W503

format: ## Format code with black (install with: pip install black)
	@echo "✨ Formatting code..."
	@$(VENV_BIN)/black --version > /dev/null 2>&1 || (echo "Installing black..." && $(PIP) install black)
	$(VENV_BIN)/black *.py --line-length=120

check: lint ## Run all code quality checks
	@echo "✅ Code quality checks complete!"

requirements: ## Generate/update requirements.txt
	@echo "📋 Generating requirements.txt..."
	$(PIP) freeze > requirements.txt
	@echo "✅ Requirements updated!"

logs: ## View server logs
	@echo "📋 Server logs:"
	@tail -f server.log 2>/dev/null || echo "No log file found. Start server with 'make dev-bg' first."

backup: ## Backup database
	@echo "💾 Creating database backup..."
	@mkdir -p $(BACKUP_DIR)
	@if [ -f $(DB_FILE) ]; then \
		cp $(DB_FILE) $(BACKUP_DIR)/$(DB_FILE).backup.$$(date +%Y%m%d_%H%M%S); \
		echo "✅ Backup created in $(BACKUP_DIR)/"; \
	else \
		echo "❌ No database file found to backup"; \
	fi

restore: ## Restore database from backup (usage: make restore BACKUP=filename)
	@echo "🔄 Restoring database..."
	@if [ -z "$(BACKUP)" ]; then \
		echo "❌ Please specify backup file: make restore BACKUP=filename"; \
		echo "Available backups:"; \
		ls -la $(BACKUP_DIR)/ 2>/dev/null || echo "No backups found"; \
	else \
		cp $(BACKUP_DIR)/$(BACKUP) $(DB_FILE); \
		echo "✅ Database restored from $(BACKUP)"; \
	fi

docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t coventure-url-shortener .

docker-run: ## Run Docker container
	@echo "🐳 Running Docker container..."
	docker run -d -p $(DEV_PORT):8000 --name coventure-url-shortener coventure-url-shortener

docker-stop: ## Stop and remove Docker container
	@echo "🐳 Stopping Docker container..."
	docker stop coventure-url-shortener 2>/dev/null || true
	docker rm coventure-url-shortener 2>/dev/null || true

status: ## Show server status and recent activity
	@echo "📊 Server Status:"
	@echo "================"
	@curl -s "http://localhost:$(DEV_PORT)/api/health" | python3 -m json.tool 2>/dev/null || echo "❌ Server not responding"
	@echo ""
	@echo "📈 Database Info:"
	@if [ -f $(DB_FILE) ]; then \
		echo "📁 Database file: $(DB_FILE) ($$(du -h $(DB_FILE) | cut -f1))"; \
		echo "📅 Last modified: $$(date -r $(DB_FILE))"; \
	else \
		echo "❌ No database file found"; \
	fi
	@echo ""
	@echo "🔄 Process Info:"
	@ps aux | grep -E "(uvicorn|python.*main)" | grep -v grep || echo "No server processes found"

all: setup dev ## Setup environment and start development server

# Development workflow shortcuts
quick-test: dev-bg test-api stop ## Quick test cycle: start server, test, stop

reset: clean setup ## Clean everything and setup fresh environment

# Production helpers
prod-setup: install ## Setup for production (install deps without dev tools)
	@echo "🏭 Production setup complete!"

# Debug helpers
debug: ## Run server with debug logging
	@echo "🐛 Starting server in debug mode..."
	$(UVICORN) $(APP_MODULE) --reload --host $(HOST) --port $(DEV_PORT) --log-level debug --access-log

# Dependency management
update-deps: ## Update all dependencies
	@echo "⬆️ Updating dependencies..."
	$(PIP) install --upgrade -r requirements.txt
	$(PIP) freeze > requirements.txt
	@echo "✅ Dependencies updated!"
