""" Type definitions for the simpletool package."""
from typing import Union, Type, Optional
from pydantic import BaseModel, model_validator, Field


class SimpleInputModel(BaseModel):
    """Pydantic Input Base class for attributes."""
    @classmethod
    def model_json_schema(cls, *args, **kwargs):
        schema = super().model_json_schema(*args, **kwargs)
        # Remove title/description directly in the schema method
        schema.pop('title', None)
        schema.pop('description', None)
        if 'properties' in schema:
            for prop in schema['properties'].values():
                prop.pop('title', None)
                prop.pop('description', None)
        return schema

    @model_validator(mode='before')
    @classmethod
    def _convert_camel_to_snake_names(cls, data):
        if 'inputSchema' in data:
            data['input_schema'] = data.pop('inputSchema')
        return data


class SimpleToolModel(BaseModel):
    name: str
    description: Union[str, None] = None
    input_model: Type[SimpleInputModel]


class SimpleToolResponseModel(BaseModel):
    """
    Response model for the tools endpoint.

    Attributes:
        name (str): The name of the tool.
        description (str): A description of the tool's functionality.
        input_schema (Optional[dict]): The input schema for the tool, if available.
    """
    name: str = Field(..., description="Name of the tool")
    description: str = Field(..., description="Description of the tool's functionality")
    input_schema: Optional[dict] = Field(None, description="Input schema for the tool, if available")

    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "name": "example_tool",
                "description": "An example tool for demonstration",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "input": {"type": "string"}
                    }
                }
            }
        }
