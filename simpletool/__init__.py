"""
This module contains the base class for all simple tools.
"""
import os
import random
import json
from abc import ABC
from typing import List, Dict, Any, Union, Type, Literal
from pydantic import BaseModel, Field
from pydantic.json_schema import GenerateJsonSchema
from .types import ImageContent, TextContent, EmbeddedResource, ErrorData


class BaseTool(ABC):
    """Base class for all simple tools. """
    name: str
    description: Union[str, None] = None
    input_schema: dict[str, Any] = Field(..., alias='inputSchema')

    async def run(self, arguments: Dict[str, Any]) -> Union[List[Union[ImageContent, TextContent, EmbeddedResource]], ErrorData]:
        """Execute the tool with the given arguments"""
        # Try execute method first
        if hasattr(self, 'execute'):
            # Check if execute is not the base class method
            if self.execute.__code__ is not BaseTool.execute.__code__:
                result = await self.execute(arguments)
                return result

        # Fallback to default implementation
        raise NotImplementedError("Tool must implement either 'run' or 'execute' async method")

    async def execute(self, arguments: Dict[str, Any]) -> Union[List[Union[ImageContent, TextContent, EmbeddedResource]], ErrorData]:
        """Alternative name for run method"""
        # Try run method first
        if hasattr(self, 'run'):
            # Check if run is not the base class method
            if self.run.__code__ is not BaseTool.run.__code__:
                result = await self.run(arguments)
                return result

        # Fallback to default implementation
        raise NotImplementedError("Tool must implement either 'run' or 'execute' async method")

    def _select_random_api_key(self, env_name: str, env_value: str) -> str:
        """ Select random api key from env_value only if env_name contains 'API' and 'KEY' """
        if 'API' in env_name.upper() and 'KEY' in env_name.upper():
            api_keys = list(filter(bool, [key.strip() for key in env_value.split(',')]))
            return api_keys[0] if len(api_keys) == 1 else random.choice(api_keys)
        return env_value  # return original value if not an API key

    def get_env(self, arguments: dict, prefix: Union[str, List[str], None] = None) -> Dict[str, str]:
        """Check if arguments contains env_vars and resources[env] and merge them with os.environ"""
        envs = {}
        # 1) lets take first env_vars
        if isinstance(arguments.get('env_vars', None), dict):
            for key, value in arguments['env_vars'].items():
                envs[key] = str(value)

        # 2) lets take os env next
        for key, value in os.environ.items():
            envs[key] = value

        # 3) lets take resources['env'] as last one
        if isinstance(arguments.get('resources', None), dict) and \
           isinstance(arguments['resources'].get('env', None), dict):
            for key, value in arguments['resources']['env'].items():
                envs[key] = str(value)

        # 4) lets keep only those envs with prefixes
        if prefix is None:
            pass
        elif isinstance(prefix, str):
            envs = {k: v for k, v in envs.items() if k.startswith(prefix)}
        elif isinstance(prefix, list):
            envs = {k: v for k, v in envs.items() if any(k.startswith(pre) for pre in prefix)}

        # 5) lets replace API_KEYS with random one if it is a list
        for key, value in envs.items():
            envs[key] = self._select_random_api_key(key, value)

        return envs

    def to_json(self, input_model: Type[BaseModel], schema: Literal["full", "no_title_description"] = "no_title_description"):
        """Convert the InputModel to JSON schema."""
        if schema == "no_title_description":
            return input_model.model_json_schema(schema_generator=NoTitleDescriptionJsonSchema)
        return input_model.model_json_schema()

    def __str__(self) -> str:
        """Return a one-line JSON string representation of the tool."""
        return json.dumps({
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema
        }).encode("utf-8").decode("unicode_escape")

    def __init_subclass__(cls, **kwargs):
        """
        Validate mandatory attributes for tool subclasses.
        """
        super().__init_subclass__(**kwargs)

        # Check name (mandatory)
        if not hasattr(cls, 'name') or not isinstance(cls.name, str) or not cls.name.strip():
            raise TypeError(f"Subclass {cls.__name__} must define a non-empty 'name' string attribute")

        # Check input_schema (mandatory)
        if not hasattr(cls, 'input_schema') or not isinstance(cls.input_schema, dict):
            raise TypeError(f"Subclass {cls.__name__} must define 'input_schema' as a dictionary")

    @property
    def info(self) -> str:
        """Return a one-line JSON string representation of the tool."""
        return json.dumps({
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema
        }, indent=4)

    @property
    def to_dict(self) -> Dict[str, Any]:
        """Return a dictionary representation of the tool."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema
        }


class NoTitleDescriptionJsonSchema(GenerateJsonSchema):
    """
    A specialized JSON schema generator that removes title and description fields.

    This class inherits from GenerateJsonSchema and modifies the generated schema
    by stripping out top-level and property-level title and description fields.
    Useful when you want a clean JSON schema without descriptive metadata.

    Attributes:
        Inherits attributes from GenerateJsonSchema

    Methods:
        generate(*args, **kwargs): Generates a JSON schema and removes title/description fields
    """
    def generate(self, *args, **kwargs):
        result = super().generate(*args, **kwargs)

        # Remove title and description from top-level
        result.pop('title', None)
        result.pop('description', None)

        # Remove titles and descriptions from properties
        if 'properties' in result:
            for prop in result['properties'].values():
                prop.pop('title', None)
                prop.pop('description', None)

        return result
