#!/bin/bash

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

# Run Flake8 on test files
echo "### Running Autopep8 to fix some formating issues and Flake8 linting on test files..."
# E701 - multiple statements on one line (colon)
# E302 - expected 2 blank lines, found 1
# W293 - blank line contains whitespace
# W291 - trailing whitespace
# F401 - imported but unused (not working for some reason)
# E306 - expected 1 blank line after class or function definition, found 0
# E303 - expected 1 blank line after function or class definition, found 0
for f in `find tests/ -name "*.py"`; do autopep8 --in-place --select=E701,E302,W293,W291,F401,E303,E306 $f; done
flake8 tests/

# Run tests with coverage
echo "### Running pytest with coverage..."
python -m pytest --cov=simpletool --cov-report=term-missing --cov-report=html tests/

# coverage report for potential CI/CD integration
python -m coverage

# if .vscode folder exist.. then remove htmlcov
if [ -d ".vscode" ]; then
    rm -rf htmlcov .pytest_cache .coverage simpletool.egg-info
fi
