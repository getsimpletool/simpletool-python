"""
Pytest tests for simpletool.models module.
"""
import pytest
from pydantic import BaseModel, Field
from simpletool.models import SimpleInputModel, SimpleToolModel


class TestInputModel(SimpleInputModel):
    """Test input model for SimpleInputModel tests."""
    test_field: str = Field(description="A test field")
    camel_case_field: str = Field(description="A camel case field")

    @classmethod
    def _convert_camel_to_snake(cls, data):
        """Convert camelCase keys to snake_case."""
        converted_data = {}
        for key, value in data.items():
            # Convert camelCase to snake_case
            snake_key = ''.join(['_'+c.lower() if c.isupper() else c for c in key]).lstrip('_')
            converted_data[snake_key] = value
        return converted_data

    @classmethod
    def model_validate(cls, data):
        """Custom validation method to handle camelCase conversion."""
        converted_data = cls._convert_camel_to_snake(data)
        return super().model_validate(converted_data)


def test_simple_input_model_json_schema():
    """Test JSON schema generation without titles and descriptions."""
    schema = TestInputModel.model_json_schema()
    
    # Assert no top-level title or description
    assert 'title' not in schema
    assert 'description' not in schema
    
    # Assert no property-level titles or descriptions
    assert 'properties' in schema
    for prop in schema['properties'].values():
        assert 'title' not in prop
        assert 'description' not in prop


def test_simple_input_model_camel_case_conversion():
    """Test camelCase to snake_case conversion."""
    data = {
        "testField": "test value",
        "camelCaseField": "another test value"
    }
    model = TestInputModel.model_validate(data)
    
    assert model.test_field == "test value"
    assert model.camel_case_field == "another test value"


def test_simple_input_model_without_input_schema():
    """Test conversion when inputSchema is not present."""
    data = {"someField": "test value"}
    result = SimpleInputModel._convert_camel_to_snake_names(data)
    assert result == {"someField": "test value"}
    assert "input_schema" not in result

def test_simple_input_model_with_input_schema():
    """Test conversion when inputSchema is present."""
    data = {"inputSchema": {"type": "object"}}
    result = SimpleInputModel._convert_camel_to_snake_names(data)
    assert "inputSchema" not in result
    assert result["input_schema"] == {"type": "object"}

def test_simple_tool_model():
    """Test SimpleToolModel initialization."""
    tool_model = SimpleToolModel(
        name="TestTool", 
        description="A test tool", 
        input_model=TestInputModel
    )
    
    assert tool_model.name == "TestTool"
    assert tool_model.description == "A test tool"
    assert tool_model.input_model == TestInputModel
