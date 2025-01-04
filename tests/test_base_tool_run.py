import pytest
from simpletool import BaseTool, validate_tool_output
from simpletool.types import ErrorData, TextContent
from pydantic import BaseModel, Field


class DummyContentType(BaseModel):
    """A dummy content type not in the allowed list for testing invalid type handling."""
    type: str = Field(default="dummy")
    content: str = Field(default="dummy content")


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


@pytest.mark.asyncio
async def test_validate_tool_output_non_list():
    """Test validate_tool_output decorator raises TypeError for non-list output."""
    @validate_tool_output
    async def dummy_tool_non_list():
        return "not a list"

    with pytest.raises(TypeError, match="Tool output must be a list"):
        await dummy_tool_non_list()


@pytest.mark.asyncio
async def test_validate_tool_output_invalid_type():
    """Test validate_tool_output decorator raises TypeError for invalid output type."""
    @validate_tool_output
    async def dummy_tool_invalid_type():
        return [42]  # Invalid type

    with pytest.raises(TypeError, match="Invalid output type"):
        await dummy_tool_invalid_type()


@pytest.mark.asyncio
async def test_validate_tool_output_error_data():
    """Test validate_tool_output decorator passes through ErrorData."""
    error_data = ErrorData(code=1, message="Test error")

    @validate_tool_output
    async def dummy_tool_error_data():
        return [error_data]  # Wrap ErrorData in a list

    result = await dummy_tool_error_data()
    assert result == [error_data]


@pytest.mark.asyncio
async def test_validate_tool_output_single_content_type():
    """Test validate_tool_output decorator raises TypeError when a content type is returned instead of a list."""
    @validate_tool_output
    async def dummy_tool_single_content():
        return TextContent(type="text", text="Single content")  # Not wrapped in a list

    with pytest.raises(TypeError, match="Tool output must be a list"):
        await dummy_tool_single_content()


@pytest.mark.asyncio
async def test_validate_tool_output_mixed_invalid_types():
    """Test validate_tool_output decorator raises TypeError for return invalid type in the list."""
    @validate_tool_output
    async def dummy_tool_mixed_types():
        return [DummyContentType(type="dummy", content="dummy content"), 42]

    with pytest.raises(TypeError, match="Invalid output type"):
        await dummy_tool_mixed_types()
