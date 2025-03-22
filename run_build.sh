#!/bin/bash
set -e

echo "=== SimpleTool Python Package Build Script ==="

# Check if virtual environment exists and activate it if it does
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
fi

# Install build dependencies if not already installed
echo "Ensuring build dependencies are installed..."
pip install --upgrade build wheel twine setuptools

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/

# Run tests to ensure everything is working
echo "Running tests..."
./run_pytest.sh

# Build the package
echo "Building SimpleTool package..."
python -m build

# Show build results
echo "=== Build Complete ==="
echo "Build artifacts:"
ls -l dist/

echo "To upload to PyPI, run:"
echo "> twine upload dist/*"

echo "Do you want to install the package locally? (y/n)"
read answer
if [[ $answer == "y" || $answer == "Y" ]]; then
    pip install dist/*.whl
    echo "Package installed locally."
else
    echo "Skipping local installation."
fi
