import os
import pytest
from simpletool import BaseTool


class DummyTool(BaseTool):
    name = "dummy_tool"
    description = "A dummy tool for testing"
    input_schema = {"type": "object", "properties": {}}


@pytest.fixture
def mock_env(monkeypatch):
    """Create a mock environment for testing."""
    monkeypatch.setenv("DUMMY_TOOL_ENV_VAR", "test_value")
    monkeypatch.setenv("ANOTHER_ENV_VAR", "another_value")
    monkeypatch.setenv("RESOURCES_TEST_KEY", "resource_value")


def test_get_env(mock_env):
    """Test getting environment variables."""
    tool = DummyTool()
    env_vars = tool.get_env({"env_vars": {"DUMMY_TOOL_ENV_VAR": "test_value"}})
    assert env_vars["DUMMY_TOOL_ENV_VAR"] == "test_value"


def test_get_env_resources(mock_env):
    """Test getting environment variables with resources."""
    tool = DummyTool()
    env_vars = tool.get_env({
        "resources": {
            "env": {"test_key": "RESOURCES_TEST_KEY"}
        }
    })
    assert env_vars["RESOURCES_TEST_KEY"] == "resource_value"


def test_get_env_prefix(mock_env):
    """Test getting environment variables with a prefix."""
    tool = DummyTool()
    env_vars = tool.get_env({}, prefix="DUMMY_TOOL")
    assert "DUMMY_TOOL_ENV_VAR" in env_vars
    assert env_vars["DUMMY_TOOL_ENV_VAR"] == "test_value"


def test_get_env_prefix_single_item_list(mock_env):
    """Test getting environment variables with a single-item list prefix."""
    tool = DummyTool()
    env_vars = tool.get_env({}, prefix=["DUMMY_TOOL"])
    assert "DUMMY_TOOL_ENV_VAR" in env_vars
    assert env_vars["DUMMY_TOOL_ENV_VAR"] == "test_value"
    assert "ANOTHER_ENV_VAR" not in env_vars


def test_get_env_prefix_multiple_items_list(mock_env):
    """Test getting environment variables with a multi-item list prefix."""
    tool = DummyTool()
    # Add another env var to test multiple prefixes
    os.environ["ANOTHER_TOOL_TEST_VAR"] = "another_test_value"

    try:
        env_vars = tool.get_env({}, prefix=["DUMMY_TOOL", "ANOTHER_TOOL"])
        assert "DUMMY_TOOL_ENV_VAR" in env_vars
        assert env_vars["DUMMY_TOOL_ENV_VAR"] == "test_value"
        assert "ANOTHER_TOOL_TEST_VAR" in env_vars
        assert env_vars["ANOTHER_TOOL_TEST_VAR"] == "another_test_value"
    finally:
        # Clean up the temporary environment variable
        os.environ.pop("ANOTHER_TOOL_TEST_VAR", None)
