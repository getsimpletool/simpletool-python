import pytest
from simpletool import BaseTool

class DummyTool(BaseTool):
    name = "dummy_tool"
    description = "A dummy tool for testing"
    input_schema = {"type": "object", "properties": {}}

    async def run(self, arguments):
        return [{"type": "text", "text": "Run method result"}]

    async def execute(self, arguments):
        return [{"type": "text", "text": "Execute method result"}]

@pytest.mark.asyncio
async def test_base_tool_run():
    """Test the run method of BaseTool."""
    tool = DummyTool()
    result = await tool.run({})
    assert result[0]["text"] == "Run method result"

@pytest.mark.asyncio
async def test_base_tool_execute():
    """Test the execute method of BaseTool."""
    tool = DummyTool()
    result = await tool.execute({})
    assert result[0]["text"] == "Execute method result"
