#!/bin/bash

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -e . -r requirements-dev.txt
else
    echo "Virtual environment already exists. Activating..."
    { source venv/bin/activate; } 2>/dev/null
fi

# Run tests with coverage
python -m pytest --cov=simpletool --cov-report=term-missing --cov-report=html tests/

# coverage report for potential CI/CD integration
python -m coverage

# if .vscode folder exist.. then remove htmlcov
if [ -d ".vscode" ]; then
    rm -rf htmlcov .pytest_cache .coverage simpletool.egg-info
fi
