import json
import pytest
from simpletool import BaseTool
from pydantic import BaseModel, Field

class DummyInputModel(BaseModel):
    """A dummy input model for testing JSON serialization."""
    name: str = Field(description="Name of the item")
    value: int = Field(description="Value of the item")

class DummyTool(BaseTool):
    name = "dummy_tool"
    description = "A dummy tool for testing"
    input_schema = {"type": "object", "properties": {}}

def test_to_json():
    """Test JSON serialization of BaseTool."""
    tool = DummyTool()
    json_data = tool.to_json(DummyInputModel, schema="no_title_description")
    
    # Convert dict to JSON string
    json_str = json.dumps(json_data)
    
    # Parse the JSON to validate it
    parsed_data = json.loads(json_str)
    
    # Check the expected keys
    assert parsed_data.get("type") == "object"
    assert "properties" in parsed_data
    assert "name" in parsed_data["properties"]
    assert "value" in parsed_data["properties"]
