#!/bin/bash
# Test runner script for the authentication microservice

echo "🧪 Running Authentication Microservice Tests"
echo "=============================================="

# Run tests with coverage if requested
if [ "$1" = "--coverage" ]; then
    echo "📊 Running tests with coverage..."
    poetry run pytest tests/ --cov=src --cov-report=term-missing --cov-report=html -v
else
    echo "🎯 Running all tests..."
    poetry run pytest tests/ -v
fi

echo ""
echo "✅ Test run completed!"
