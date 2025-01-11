"""Pytest configuration and global fixtures."""
import warnings
import pytest


def pytest_configure(config):
    """Pytest configuration hook."""
    config.addinivalue_line(
        "markers",
        "asyncio: mark test to run with asyncio"
    )
    # Set the default asyncio fixture loop scope to function
    config.option.asyncio_default_fixture_loop_scope = "function"


def pytest_collection_modifyitems(config, items):
    """Modify test collection to ignore specific warnings."""
    for item in items:
        # Suppress warnings about test classes with __init__ constructors
        warnings.filterwarnings(
            "ignore",
            category=pytest.PytestCollectionWarning,
            message=r".*cannot collect test class .* because it has a __init__ constructor"
        )
