"""Pytest configuration and global fixtures."""


def pytest_configure(config):
    """Pytest configuration hook."""
    config.addinivalue_line(
        "markers",
        "asyncio: mark test to run with asyncio"
    )
    # Set the default asyncio fixture loop scope to function
    config.option.asyncio_default_fixture_loop_scope = "function"
