.PHONY: help install run dev test lint format type-check clean migrate upgrade downgrade migration pre-commit setup-dev

# Default target
help:
	@echo "Available commands:"
	@echo "  install      Install dependencies"
	@echo "  setup-dev    Setup development environment"
	@echo "  run          Run the application"
	@echo "  dev          Run in development mode with auto-reload"
	@echo "  test         Run tests"
	@echo "  test-cov     Run tests with coverage"
	@echo "  lint         Run linting with Ruff"
	@echo "  lint-fix     Run linting with auto-fix"
	@echo "  format       Format code with Black and Ruff"
	@echo "  type-check   Run type checking with MyPy"
	@echo "  pre-commit   Run pre-commit hooks"
	@echo "  clean        Clean cache files"
	@echo "  migrate      Apply database migrations"
	@echo "  upgrade      Upgrade database to latest migration"
	@echo "  downgrade    Downgrade database by one migration"
	@echo "  migration    Create new migration (use: make migration msg='description')"
	@echo "  check-all    Run all checks (lint, type-check, test)"

# Install dependencies
install:
	poetry install

# Setup development environment
setup-dev:
	poetry install
	poetry run pre-commit install
	@echo "Development environment setup complete!"
	@echo "Run 'make dev' to start the development server"

# Run the application
run:
	poetry run uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Run in development mode
dev:
	poetry run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
test:
	poetry run pytest -v

# Run tests with coverage
test-cov:
	poetry run pytest -v --cov=src --cov-report=term-missing --cov-report=html

# Run linting with Ruff
lint:
	poetry run ruff check .

# Run linting with auto-fix
lint-fix:
	poetry run ruff check . --fix

# Format code
format:
	poetry run black .
	poetry run isort .
	poetry run ruff format .

# Type checking
type-check:
	poetry run mypy .

# Run pre-commit hooks
pre-commit:
	poetry run pre-commit run --all-files

# Run all checks
check-all: lint type-check test
	@echo "All checks completed successfully!"

# Clean cache files (cross-platform: Python script instead of find)
clean:
	poetry run python -c "import shutil, pathlib; \
	[shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; \
	[shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('.pytest_cache')]; \
	[shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('.mypy_cache')]; \
	[shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('.ruff_cache')]; \
	[p.unlink(missing_ok=True) for p in pathlib.Path('.').rglob('*.pyc')]; \
	pathlib.Path('htmlcov').rmdir() if pathlib.Path('htmlcov').exists() else None; \
	pathlib.Path('coverage.xml').unlink(missing_ok=True); \
	pathlib.Path('.coverage').unlink(missing_ok=True)"

# Database migration commands
migrate:
	poetry run alembic upgrade head

upgrade:
	poetry run alembic upgrade head

downgrade:
	poetry run alembic downgrade -1

migration:
	@if [ -z "$(msg)" ]; then \
		echo "Error: Please provide a message. Usage: make migration msg='Your migration description'"; \
		exit 1; \
	fi
	poetry run alembic revision --autogenerate -m "$(msg)"

# Monitoring and health check commands
health-check:
	@echo "🏥 Checking service health..."
	@curl -s http://localhost:8000/health | jq . || echo "❌ Service not responding"

health-detailed:
	@echo "🔍 Detailed health check..."
	@curl -s http://localhost:8000/health/detailed | jq . || echo "❌ Service not responding"

health-all:
	@echo "🩺 Running all health checks..."
	@echo "Basic health:"
	@curl -s http://localhost:8000/health | jq .
	@echo "Liveness:"
	@curl -s http://localhost:8000/health/live | jq .
	@echo "Readiness:"
	@curl -s http://localhost:8000/health/ready | jq . || echo "Service not ready (expected if DB not running)"

metrics:
	@echo "📊 Fetching Prometheus metrics..."
	@curl -s http://localhost:8000/metrics | head -20

metrics-custom:
	@echo "📈 Custom application metrics..."
	@curl -s http://localhost:8000/metrics | grep -E "(service_info|auth_requests|active_users|database_connections)"

logs:
	@echo "📝 Recent application logs..."
	@tail -20 app.log | jq . || tail -20 app.log

logs-errors:
	@echo "❌ Error logs..."
	@tail -100 app.log | jq 'select(.level == "error")' || echo "No error logs found"

start-monitoring:
	@echo "🚀 Starting full monitoring stack..."
	@docker-compose -f docker-compose.monitoring.yml up -d

stop-monitoring:
	@echo "🛑 Stopping monitoring stack..."
	@docker-compose -f docker-compose.monitoring.yml down

monitoring-status:
	@echo "📊 Monitoring stack status..."
	@docker-compose -f docker-compose.monitoring.yml ps

# Development server with monitoring
dev-server:
	@echo "🔧 Starting development server with monitoring..."
	LOG_LEVEL=DEBUG JSON_LOGS=false ENABLE_METRICS=true poetry run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

prod-server:
	@echo "🚀 Starting production server..."
	LOG_LEVEL=INFO JSON_LOGS=true ENABLE_METRICS=true poetry run uvicorn src.api.main:app --host 0.0.0.0 --port 8000
