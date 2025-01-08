#!/bin/bash

# Ensure script is running with bash
if [ -z "$BASH_VERSION" ]; then
    echo "Error: This script must be run with bash"
    exit 1
fi

# Disable __pycache__ generation
export PYTHONDONTWRITEBYTECODE=1

# Remove any existing __pycache__ directories
find . -type d -name "__pycache__" ! -path "*/venv/*" -exec rm -rf {} +

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "### Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -e . -r requirements-dev.txt
else
    echo "### Virtual environment already exists. Activating..."
    { source venv/bin/activate; } 2>/dev/null
fi

# Run Autopep8 amd Flake8 if --lint argument is provided
if [ "$1" = "--lint" ]; then
    echo "### Running Autopep8 to fix formatting issues..."
    # E701 - multiple statements on one line (colon)
    # E302 - expected 2 blank lines, found 1
    # W293 - blank line contains whitespace
    # W291 - trailing whitespace
    # F401 - imported but unused (not working for some reason)
    # E306 - expected 1 blank line after class or function definition, found 0
    # E303 - expected 1 blank line after function or class definition, found 0
    for f in `find tests/ -name "*.py"`; do autopep8 --in-place --select=E701,E302,W293,W291,F401,E303,E306 $f; done

    # Run Flake8 on test files
    echo "### Running Flake8 linting on test files..."
    flake8 tests/
fi



# Run tests with coverage and detailed error reporting
echo "### Running pytest with coverage and detailed error reporting..."
python -m pytest -v --tb=long --cov=simpletool --cov-report=term-missing --cov-report=html tests/

# coverage report for potential CI/CD integration
coverage run -m pytest tests/ simpletool/ && coverage report -m --include="simpletool/*"

# if .vscode folder exist.. then remove htmlcov
if [ -d ".vscode" ]; then
    rm -rf htmlcov .pytest_cache .coverage simpletool.egg-info
fi
