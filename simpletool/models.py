""" Type definitions for the simpletool package."""
from typing import Union, Type
from pydantic import BaseModel, model_validator


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
