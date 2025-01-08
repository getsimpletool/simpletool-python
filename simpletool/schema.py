"""
JSON Schema
"""
from pydantic.json_schema import GenerateJsonSchema
from pydantic import BaseModel


class NoTitleDescriptionJsonSchema(GenerateJsonSchema):
    """A specialized JSON schema generator that removes title and description fields."""

    def generate(self, model: type[BaseModel], *args, **kwargs):
        """
        Generate JSON schema for a Pydantic model.
        Args:
            model: Pydantic model class
        """
        # Get the core schema for the model
        core_schema = model.model_json_schema(*args, **kwargs)
        # Remove title and description from top-level
        core_schema.pop('title', None)
        core_schema.pop('description', None)
        # Remove titles and descriptions from properties
        if 'properties' in core_schema:
            for prop in core_schema['properties'].values():
                prop.pop('title', None)
                prop.pop('description', None)
        return core_schema
