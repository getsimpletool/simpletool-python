"""
Pytest tests for simpletool.__init__ module.
"""
import pytest
import asyncio
import json
from typing import Sequence, Union, Dict, Any
from pydantic import BaseModel, Field
from simpletool import (
    SimpleTool, 
    validate_tool_output, 
    set_timeout, 
    get_valid_content_types,
    SimpleInputModel
)
from simpletool.types import (
    ImageContent, 
    TextContent, 
    FileContent, 
    ResourceContent, 
    ErrorContent,
    Content,
    BoolContents
)
from simpletool.errors import ValidationError


# Test input model for SimpleTool
class TestInputModel(SimpleInputModel):
    test_field: str = Field(description="A test field")


# Test SimpleTool subclass for testing
class TestSimpleTool(SimpleTool):
    name = "TestTool"
    description = "A tool for testing"
    input_model = TestInputModel

    async def run(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        """Dummy run method for testing."""
        return [TextContent(type="text", text=arguments['test_field'])]


def test_get_valid_content_types():
    """Test get_valid_content_types function."""
    valid_types = get_valid_content_types()
    assert len(valid_types) == 7
    assert set(valid_types) == {Content, TextContent, ImageContent, FileContent, ResourceContent, BoolContents, ErrorContent}


def test_validate_tool_output_decorator():
    """Test validate_tool_output decorator."""
    @validate_tool_output
    async def valid_output_tool():
        return [TextContent(type="text", text="test")]
    
    @validate_tool_output
    async def invalid_output_tool():
        return ["not a valid content type"]

    # Test valid output
    result = asyncio.run(valid_output_tool())
    assert len(result) == 1
    assert isinstance(result[0], TextContent)

    # Test invalid output type
    with pytest.raises(ValidationError, match="Invalid output type"):
        asyncio.run(invalid_output_tool())

    # Test non-list output
    @validate_tool_output
    async def non_list_output_tool():
        return TextContent(type="text", text="test")
    
    with pytest.raises(ValidationError, match="Tool output must be a list"):
        asyncio.run(non_list_output_tool())


def test_set_timeout_decorator():
    """Test set_timeout decorator."""
    @set_timeout(0.1)  # 100ms timeout
    async def slow_tool():
        await asyncio.sleep(0.2)
        return [TextContent(type="text", text="delayed")]

    @set_timeout(0.2)
    async def fast_tool():
        await asyncio.sleep(0.1)
        return [TextContent(type="text", text="quick")]

    # Test timeout
    result = asyncio.run(slow_tool())
    assert len(result) == 1
    assert isinstance(result[0], ErrorContent)
    assert result[0].code == 408
    assert "timed out" in result[0].message

    # Test non-timeout
    result = asyncio.run(fast_tool())
    assert len(result) == 1
    assert isinstance(result[0], TextContent)


def test_simpletool_initialization():
    """Test SimpleTool initialization."""
    tool = TestSimpleTool()
    
    # Test basic attributes
    assert tool.name == "TestTool"
    assert tool.description == "A tool for testing"
    assert tool.input_model == TestInputModel
    
    # Test input schema
    assert "properties" in tool.input_schema
    assert "test_field" in tool.input_schema["properties"]
    
    # Test timeout
    assert tool._timeout == tool.DEFAULT_TIMEOUT


def test_simpletool_str_representation():
    """Test __str__ method of SimpleTool."""
    tool = TestSimpleTool()
    tool_str = str(tool)
    
    # Parse the JSON string
    tool_dict = json.loads(tool_str)
    
    # Validate structure
    assert "name" in tool_dict
    assert "description" in tool_dict
    assert "input_schema" in tool_dict
    assert tool_dict["name"] == "TestTool"
    assert tool_dict["description"] == "A tool for testing"
    assert "properties" in tool_dict["input_schema"]


def test_simpletool_repr():
    """Test __repr__ method of SimpleTool."""
    tool = TestSimpleTool()
    repr_str = repr(tool)
    
    assert repr_str == "SimpleTool(name='TestTool', description=A tool for testing)"


def test_simpletool_async_context_manager():
    """Test async context manager functionality."""
    async def test_context_manager():
        async with TestSimpleTool() as tool:
            assert isinstance(tool, TestSimpleTool)
    
    asyncio.run(test_context_manager())


def test_simpletool_subclass_validation():
    """Test validation during subclass creation."""
    # Test invalid name
    with pytest.raises(ValidationError, match="must define a non-empty 'name' string attribute"):
        class InvalidNameTool(SimpleTool):
            name = ""
            description = "Test tool"
            input_model = TestInputModel

    # Test invalid description
    with pytest.raises(ValidationError, match="must define a non-empty 'description' string attribute"):
        class InvalidDescriptionTool(SimpleTool):
            name = "InvalidTool"
            description = ""
            input_model = TestInputModel

    # Test missing input_model
    with pytest.raises(ValidationError, match="must define a class-level 'input_model' as a subclass of SimpleInputModel"):
        class MissingInputModelTool(SimpleTool):
            name = "MissingInputModel"
            description = "Test tool"


def test_simpletool_sort_input_schema():
    """Test _sort_input_schema method."""
    tool = TestSimpleTool()
    unsorted_schema = {
        "additionalProperties": False,
        "required": ["test_field"],
        "properties": {"test_field": {}},
        "title": "Test"
    }
    
    sorted_schema = tool._sort_input_schema(unsorted_schema)
    
    # Check key order
    keys = list(sorted_schema.keys())
    assert keys[0] == "properties"
    assert keys[1] == "required"
    assert keys[2] == "additionalProperties"
    assert keys[3] == "title"


def test_simpletool_run_method():
    """Test default run method."""
    tool = TestSimpleTool()
    
    async def test_run():
        result = await tool.run({"test_field": "hello"})
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].text == "hello"
    
    asyncio.run(test_run())


import inspect
import typing
from typing import List, Union, Optional

# Additional test cases for edge scenarios and uncovered lines

class ComplexInputModel(SimpleInputModel):
    """Input model with more complex type annotations."""
    optional_field: Optional[str] = None
    list_field: List[str] = []
    union_field: Union[str, int] = ""


class AdvancedSimpleTool(SimpleTool):
    """Advanced SimpleTool for testing complex scenarios."""
    name = "AdvancedTool"
    description = "A tool with complex input and output types"
    input_model = ComplexInputModel

    async def run(self, arguments: Dict[str, Any]) -> Sequence[Union[TextContent, ErrorContent]]:
        """Demonstrate more complex run method with multiple return types."""
        if not arguments.get('optional_field'):
            return [ErrorContent(
                code=400, 
                message="Optional field is required", 
                data={"input": arguments}
            )]
        return [TextContent(type="text", text=str(arguments['optional_field']))]


def test_advanced_simpletool_complex_initialization():
    """Test initialization with more complex input model."""
    tool = AdvancedSimpleTool()
    
    # Verify input schema generation for complex types
    assert 'properties' in tool.input_schema
    assert 'optional_field' in tool.input_schema['properties']
    assert 'list_field' in tool.input_schema['properties']
    assert 'union_field' in tool.input_schema['properties']


def test_simpletool_output_schema_generation():
    """Test output schema generation with different type annotations."""
    tool = AdvancedSimpleTool()
    
    # Verify output schema generation
    assert tool.output_schema is not None
    assert 'type' in tool.output_schema
    assert tool.output_schema['type'] == 'array'
    assert 'items' in tool.output_schema
    assert 'oneOf' in tool.output_schema['items']


def test_simpletool_error_handling_in_run():
    """Test error handling in run method with different input scenarios."""
    async def test_error_scenarios():
        tool = AdvancedSimpleTool()
        
        # Test error scenario
        error_result = await tool.run({})
        assert len(error_result) == 1
        assert isinstance(error_result[0], ErrorContent)
        assert error_result[0].code == 400
        
        # Test successful scenario
        success_result = await tool.run({"optional_field": "test"})
        assert len(success_result) == 1
        assert isinstance(success_result[0], TextContent)
        assert success_result[0].text == "test"
    
    asyncio.run(test_error_scenarios())


def test_simpletool_timeout_configuration():
    """Test timeout configuration and customization."""
    # Test default timeout
    default_tool = TestSimpleTool()
    assert default_tool._timeout == default_tool.DEFAULT_TIMEOUT
    
    # Test custom timeout
    custom_timeout = 30.0
    with pytest.raises(TypeError):
        custom_tool = TestSimpleTool(timeout=custom_timeout)


def test_simpletool_input_model_validation():
    """Test input model validation during tool initialization."""
    # Test valid input model
    class ValidToolWithInputModel(SimpleTool):
        name = "ValidTool"
        description = "A tool with a valid input model"
        input_model = TestInputModel

    # This should not raise an exception
    ValidToolWithInputModel()

    # Test invalid input model
    with pytest.raises(ValidationError, match="must define a class-level 'input_model' as a subclass of SimpleInputModel"):
        class InvalidToolWithoutInputModel(SimpleTool):
            name = "InvalidTool"
            description = "A tool without an input model"


def test_simpletool_method_resolution():
    """Test method resolution and inheritance."""
    # Verify that run method is async
    run_method = getattr(TestSimpleTool, 'run')
    assert inspect.iscoroutinefunction(run_method)
    
    # Verify method signature
    signature = inspect.signature(run_method)
    assert list(signature.parameters.keys()) == ['self', 'arguments']
    assert signature.return_annotation == typing.Sequence[TextContent]


def test_simpletool_async_context_manager_error_handling():
    """Test async context manager with potential resource initialization errors."""
    class FailingInitTool(SimpleTool):
        name = "FailingTool"
        description = "A tool that fails during initialization"
        input_model = TestInputModel

        async def __aenter__(self):
            """Simulate a resource initialization failure."""
            raise RuntimeError("Resource initialization failed")

    async def test_context_manager_error():
        with pytest.raises(RuntimeError, match="Resource initialization failed"):
            async with FailingInitTool() as tool:
                pass
    
    asyncio.run(test_context_manager_error())
