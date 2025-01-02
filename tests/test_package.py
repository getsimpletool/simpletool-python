import importlib
import importlib
import pytest
import simpletool
import ast

def test_package_importable():
    """Verify that the simpletool package can be imported."""
    try:
        importlib.import_module('simpletool')
    except ImportError:
        pytest.fail("Package 'simpletool' cannot be imported")


def test_package_metadata():
    """Basic validation of package metadata."""
    
    # Parse setup.py to get the version
    with open('setup.py', 'r') as f:
        tree = ast.parse(f.read())
    
    version = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'setup':
            for keyword in node.keywords:
                if keyword.arg == 'version':
                    if isinstance(keyword.value, ast.Constant):
                        version = keyword.value.value
                        break
            if version:
                break
    
    assert version, "Package version should not be empty"
