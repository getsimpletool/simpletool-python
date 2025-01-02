import pytest
from simpletool import BaseTool


class DummyTool(BaseTool):
    name = "dummy_tool"
    description = "A dummy tool for testing"
    input_schema = {"type": "object", "properties": {}}


@pytest.fixture
def mock_env(monkeypatch):
    """Create a mock environment for testing API keys."""
    monkeypatch.setenv("DUMMY_TOOL_API_KEY_1", "key1")
    monkeypatch.setenv("DUMMY_TOOL_API_KEY_2", "key2")
    monkeypatch.setenv("DUMMY_TOOL_API_KEY_3", "key3")


def test_select_random_api_key(mock_env):
    """Test selecting a random API key."""
    tool = DummyTool()
    api_key = tool._select_random_api_key("DUMMY_TOOL_API_KEY_1", "key1")
    assert api_key == "key1"


def test_select_random_api_key_multiple(mock_env):
    """Test selecting multiple random API keys."""
    tool = DummyTool()
    api_key = tool._select_random_api_key("DUMMY_TOOL_API_KEY", "key1,key2,key3")
    assert api_key in ["key1", "key2", "key3"]
