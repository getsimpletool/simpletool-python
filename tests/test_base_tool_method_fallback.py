import pytest
import asyncio
import os
from simpletool import BaseTool
from pydantic import BaseModel, Field

class DummyInputModel(BaseModel):
    name: str = Field(description="Name of the item")
    value: int = Field(description="Value of the item")

class DummyTool(BaseTool):
    name = "dummy_tool"
    description = "A dummy tool for testing"
    input_schema = {"type": "object", "properties": {}}

class PartialTool(BaseTool):
    name = "partial_tool"
    description = "A tool with only execute method"
    input_schema = {"type": "object", "properties": {}}

    async def execute(self, arguments):
        return [{"type": "text", "text": "Executed"}]

class PartialRunTool(BaseTool):
    name = "partial_run_tool"
    description = "A tool with only run method"
    input_schema = {"type": "object", "properties": {}}

    async def run(self, arguments):
        return [{"type": "text", "text": "Ran"}]

def test_run_method_fallback():
    """Test method fallback mechanism when run method is not implemented."""
    tool = DummyTool()
    with pytest.raises(NotImplementedError, match="Tool must implement either 'run' or 'execute' async method"):
        asyncio.run(tool.run({}))

def test_execute_method_fallback():
    """Test method fallback mechanism when execute method is not implemented."""
    tool = DummyTool()
    with pytest.raises(NotImplementedError, match="Tool must implement either 'run' or 'execute' async method"):
        asyncio.run(tool.execute({}))

def test_run_method_not_implemented():
    """Test that a tool can implement either run or execute method."""
    # Tools with only execute method
    execute_tool = PartialTool()
    result = asyncio.run(execute_tool.run({}))
    assert result == [{"type": "text", "text": "Executed"}]

    # Tools with only run method
    run_tool = PartialRunTool()
    result = asyncio.run(run_tool.execute({}))
    assert result == [{"type": "text", "text": "Ran"}]

def test_method_fallback_edge_cases():
    """Test edge cases in method fallback mechanism."""
    class EdgeCaseTool(BaseTool):
        name = "edge_case_tool"
        description = "A tool with a tricky method fallback"
        input_schema = {"type": "object", "properties": {}}

        # Intentionally define methods that look like base class methods
        async def run(self, arguments):
            """Implement run method that looks like base class method."""
            # Simulate a method that returns an empty list
            # This should trigger the fallback mechanism
            return []

        async def execute(self, arguments):
            """Implement execute method that looks like base class method."""
            # Simulate a method that returns an empty list
            # This should trigger the fallback mechanism
            return []

    tool = EdgeCaseTool()
    result = asyncio.run(tool.run({}))
    assert result == []

    result = asyncio.run(tool.execute({}))
    assert result == []

def test_get_env_prefix_handling():
    """Test the get_env method with various prefix types."""
    tool = DummyTool()

    # Set up test environment variables
    os.environ['TEST_VAR1'] = 'value1'
    os.environ['TEST_VAR2'] = 'value2'
    os.environ['OTHER_VAR'] = 'other_value'

    # Test with string prefix
    env_result = tool.get_env({}, prefix='TEST_')
    assert 'TEST_VAR1' in env_result
    assert 'TEST_VAR2' in env_result
    assert 'OTHER_VAR' not in env_result

    # Test with dictionary prefix
    env_result = tool.get_env({}, prefix={'TEST_': 'something'})
    assert 'TEST_VAR1' in env_result
    assert 'TEST_VAR2' in env_result
    assert 'OTHER_VAR' not in env_result

    # Test with None prefix (should return all environment variables)
    env_result = tool.get_env({}, prefix=None)
    assert 'TEST_VAR1' in env_result
    assert 'TEST_VAR2' in env_result
    assert 'OTHER_VAR' in env_result

def test_select_random_api_key():
    """Test the _select_random_api_key method."""
    tool = DummyTool()

    # Test single API key
    result = tool._select_random_api_key('API_KEY', 'single_key')
    assert result == 'single_key'

    # Test multiple API keys
    result = tool._select_random_api_key('API_KEY', 'key1,key2,key3')
    assert result in ['key1', 'key2', 'key3']

    # Test non-API key
    result = tool._select_random_api_key('REGULAR_KEY', 'regular_value')
    assert result == 'regular_value'

def test_to_json_schema():
    """Test the to_json method with different schema types."""
    tool = DummyTool()

    # Test with default 'no_title_description' schema
    json_schema_no_title = tool.to_json(DummyInputModel)
    assert 'title' not in json_schema_no_title
    assert 'description' not in json_schema_no_title['properties']['name']
    assert 'description' not in json_schema_no_title['properties']['value']

    # Test with 'full' schema
    json_schema_full = tool.to_json(DummyInputModel, schema='full')
    assert 'title' in json_schema_full
    assert 'description' in json_schema_full['properties']['name']
    assert 'description' in json_schema_full['properties']['value']
