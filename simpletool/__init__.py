"""
This module contains the base class for all simple tools.
"""
import asyncio
import os
import random
import json
import functools
import logging
from functools import wraps
from abc import ABC
from typing import List, Dict, Any, Union, Type, Literal, Sequence, Tuple, get_args
from typing import Optional, TypeVar, AnyStr, Callable, Awaitable, Coroutine, ClassVar   # noqa: F401, F403
from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo
from .types import Content, TextContent, ImageContent, FileContent, ResourceContent, BoolContent, ErrorContent
from .models import SimpleInputModel
from .schema import NoTitleDescriptionJsonSchema
from .errors import SimpleToolError, ValidationError


def get_valid_content_types() -> Tuple[Type, ...]:
    """Directly return the types from the TypeVar definition as a tuple"""
    return (Content, TextContent, ImageContent, FileContent, ResourceContent, BoolContent, ErrorContent)


def validate_tool_output(func):
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Sequence[Union[Content, TextContent, ImageContent, FileContent, ResourceContent, BoolContent, ErrorContent]]:
        result = await func(*args, **kwargs)
        if not isinstance(result, list):
            raise ValidationError("output", "Tool output must be a list")

        valid_types = get_valid_content_types()
        for item in result:
            if not any(isinstance(item, t) for t in valid_types):
                raise ValidationError("output_type", f"Invalid output type: {type(item)}. Expected one of {[t.__name__ for t in valid_types]}")
        return result
    return wrapper


def set_timeout(seconds):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                return [ErrorContent(
                    code=408,  # Request Timeout
                    message=f"Tool execution timed out after {seconds} seconds",
                    data={"timeout": seconds}
                )]
        return wrapper
    return decorator


class SimpleTool(ABC):
    """Base class for all simple tools. """
    name: str = Field(..., description="Name of the tool")
    description: str = Field("This tool does not have a description", description="Description of the tool")
    input_model: ClassVar[Type[SimpleInputModel]]  # Class-level input model

    # Add default timeout configuration
    DEFAULT_TIMEOUT: ClassVar[float] = 60.0  # 1 minute default timeout

    def __init__(self):
        """
        Initialize SimpleTool.
        """
        # Validate input_model is defined at the class level
        if not hasattr(self.__class__, 'input_model') or not issubclass(self.__class__.input_model, SimpleInputModel):
            raise ValidationError("input_model", f"Subclass {self.__class__.__name__} must define a class-level 'input_model' as a subclass of SimpleInputModel")

        # Dynamically generate input_schema from input_model
        self.input_schema = self.__class__.input_model.model_json_schema()

        # Generate output_schema and output_model from return type
        run_method = getattr(self.__class__, 'run', None)
        self.output_model = None
        if run_method is not None:
            self.output_model = run_method.__annotations__.get('return')

        # Generate output schema from output model if available
        if self.output_model is not None:
            # Get inner type(s) from Sequence/List
            if not hasattr(self.output_model, '__origin__'):
                inner_types = []  # Invalid type annotation
            else:
                inner_type = get_args(self.output_model)[0]  # Get the type inside Sequence/List
                # Extract types from Union or UnionType
                if hasattr(inner_type, '__origin__') and inner_type.__origin__ is Union:
                    # Handle typing.Union
                    inner_types = get_args(inner_type)
                elif str(type(inner_type)) == "<class 'types.UnionType'>":
                    # Handle | operator (UnionType)
                    inner_types = list(get_args(inner_type))
                else:
                    # Single type
                    inner_types = [inner_type]
            self.output_schema = {
                "type": "array",
                "items": {
                    "oneOf": [
                        t.model_json_schema() for t in inner_types
                    ]
                }
            }
        else:
            self.output_schema = None

        # Remove timeout-related initialization
        self._timeout = self.DEFAULT_TIMEOUT

    async def __aenter__(self):
        """
        Async context manager entry point for resource initialization
        - Proper initialization of resources
        - Guaranteed cleanup of resources, even if exceptions occur
        - Deterministic resource lifecycle management return self
        """
        return self

    def __init_subclass__(cls, **kwargs):
        # modify the __init__ method to always call super()
        original_init = cls.__init__

        def modified_init(self, *args, **kwargs):
            super(cls, self).__init__()  # Force super() call
            original_init(self, *args, **kwargs)
        cls.__init__ = modified_init
        super().__init_subclass__(**kwargs)

        # Validate 'name' - check if 'name' is a FieldInfo and extract its value
        if isinstance(cls.name, FieldInfo):
            name = cls.name.default
        else:
            name = cls.name

        # Ensure name is defined and is a non-empty string
        if not name or not isinstance(name, str):
            raise ValidationError("name", f"Subclass {cls.__name__} must define a non-empty 'name' string attribute")

        # Validate 'description'
        # Check if 'description' is a FieldInfo and extract its value
        if isinstance(cls.description, FieldInfo):
            description = cls.description.default
        else:
            description = cls.description

        if description is not None and (not isinstance(description, str) or not description.strip()):
            raise ValidationError("description", f"Subclass {cls.__name__} must define a non-empty 'description' string attribute")

        # Validate input_model is defined and is a subclass of SimpleInputModel
        if not hasattr(cls, 'input_model') or not issubclass(cls.input_model, SimpleInputModel):
            raise ValidationError("input_model", f"Subclass {cls.__name__} must define a class-level 'input_model' as a subclass of SimpleInputModel")

        # Prevent manual input_schema definition
        if hasattr(cls, 'input_schema'):
            raise ValidationError("input_schema", f"Subclass {cls.__name__} cannot manually define 'input_schema'. It will be automatically generated from 'input_model'.")

    def _sort_input_schema(self, input_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sort input_schema keys with a specified order.

        The order prioritizes: type, properties, required
        Any additional keys are added after these in their original order.

        Args:
            input_schema (Dict[str, Any]): The input schema to be sorted

        Returns:
            Dict[str, Any]: A sorted version of the input schema
        """
        # Define the desired key order
        priority_keys = ['type', 'properties', 'required']

        # Create a new dictionary with prioritized keys
        sorted_schema = {}

        # Add priority keys if they exist in the original schema
        for key in priority_keys:
            if key in input_schema:
                sorted_schema[key] = input_schema[key]

        # Add remaining keys in their original order
        for key, value in input_schema.items():
            if key not in priority_keys:
                sorted_schema[key] = value

        return sorted_schema

    def __str__(self) -> str:
        """Return a one-line JSON string representation of the tool."""
        sorted_input_schema = self._sort_input_schema(self.input_schema)
        return json.dumps({
            "name": self.name,
            "description": self.description,
            "input_schema": sorted_input_schema
        }).encode("utf-8").decode("unicode_escape")

    def __repr__(self):
        return f"SimpleTool(name='{self.name}', description={self.description})"

    @validate_tool_output
    @set_timeout(DEFAULT_TIMEOUT)
    async def run(self, arguments: Dict[str, Any]) -> Sequence[Union[Content, TextContent, ImageContent, FileContent, ResourceContent, BoolContent, ErrorContent]]:
        """
        Execute the tool with the given arguments.

        This is the primary method that tool developers should override.

        Args:
            arguments (Dict[str, Any]): Input arguments for the tool

        Returns:
            Sequence of content types (text, image, file, resource, or error)

        Raises:
            TypeError: If arguments are not a dictionary
            NotImplementedError: If run method is not implemented in child class
        """
        # Validate and convert input arguments to the input model
        try:
            # Validate that all required fields are present and have correct types
            validated_arguments = self.input_model.model_validate(arguments)
        except ValidationError as e:
            return [ErrorContent(
                code=400,  # Bad Request
                message=f"Input validation error: {str(e)}",
                data={"validation_error": str(e)}
            )]

        # Apply timeout mechanism
        if self._timeout > 0:
            try:
                # Require implementation in child classes with timeout
                result = await asyncio.wait_for(
                    self._run_implementation(validated_arguments),
                    timeout=self._timeout
                )
                return result
            except asyncio.TimeoutError:
                return [ErrorContent(
                    code=408,  # Request Timeout
                    message=f"Tool execution timed out after {self._timeout} seconds",
                    data={"timeout": self._timeout}
                )]
        else:
            # No timeout if _timeout is 0 or negative
            return await self._run_implementation(validated_arguments)

    async def _run_implementation(self, arguments: SimpleInputModel) -> Sequence[Union[Content, TextContent, ImageContent, FileContent, ResourceContent, BoolContent, ErrorContent]]:
        """
        Actual implementation of the tool's run method.
        Must be implemented by child classes.

        Args:
            arguments (SimpleInputModel): Validated input arguments

        Raises:
            SimpleToolError: If not implemented by child class
        """
        raise SimpleToolError(f"Subclass {self.__class__.__name__} must implement _run_implementation method")

    async def __call__(self, arguments: Dict[str, Any]) -> Sequence[Union[Content, TextContent, ImageContent, FileContent, ResourceContent, BoolContent, ErrorContent]]:
        """Alias for run method"""
        return await self.run(arguments)

    def _select_random_api_key(self, env_name: str, env_value: str) -> str:
        """ Select random api key from env_value only if env_name contains 'API' and 'KEY' """
        if 'API' in env_name.upper() and 'KEY' in env_name.upper():
            api_keys = list(filter(bool, [key.strip() for key in env_value.split(',')]))
            if not api_keys:
                return ""
            return api_keys[0] if len(api_keys) == 1 else random.choice(api_keys)
        return env_value  # return original value if not an API key

    def get_env(self, arguments: dict, prefix: Union[str, List[str], None] = None) -> Dict[str, str]:
        """Check if arguments contains env_vars and resources[env] and merge them with os.environ"""
        envs = {}

        # 1) lets take os env first
        for key, value in os.environ.items():
            envs[key] = value

        # 2) lets take env_vars and override os env
        if isinstance(arguments.get('env_vars', None), dict):
            for key, value in arguments['env_vars'].items():
                envs[key] = str(value)

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

    @property
    def info(self) -> str:
        """Return a one-line JSON string representation of the tool."""
        sorted_input_schema = self._sort_input_schema(self.input_schema)
        return json.dumps({
            "name": self.name,
            "description": self.description,
            "input_schema": sorted_input_schema
        }, indent=4)

    @property
    def to_dict(self) -> Dict[str, Any]:
        """Return a dictionary representation of the tool."""
        sorted_input_schema = self._sort_input_schema(self.input_schema)
        return {
            "name": self.name,
            "description": str(self.description),
            "input_schema": sorted_input_schema
        }

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Async context manager exit point for resource cleanup
        Generic async context manager exit point for resource cleanup
        Attempts to close/release any async or sync resources
        """
        # Clean up resources, close connections, release locks
        # Handle any exceptions that occurred during tool execution
        # Collect any potential resources that might need cleanup
        resources_to_close = []

        # Inspect instance attributes for potential resources
        for attr_name in dir(self):
            try:
                attr = getattr(self, attr_name)

                # Skip magic methods and non-objects
                if attr_name.startswith('__') or not hasattr(attr, '__class__'):
                    continue

                # Check for various cleanup methods
                if hasattr(attr, 'aclose') and asyncio.iscoroutinefunction(attr.aclose):
                    # aclose() is used by async generators and some async resources
                    resources_to_close.append(('async_close', attr, 'aclose'))
                elif hasattr(attr, 'close') and asyncio.iscoroutinefunction(attr.close):
                    # async close() method
                    resources_to_close.append(('async_close', attr, 'close'))
                elif hasattr(attr, 'close') and callable(attr.close):
                    # sync close() method (files, sockets, etc)
                    resources_to_close.append(('sync_close', attr, 'close'))
                elif hasattr(attr, 'disconnect') and callable(attr.disconnect):
                    # disconnect() method (some database/network resources)
                    resources_to_close.append(('sync_close', attr, 'disconnect'))
                elif hasattr(attr, 'cleanup') and callable(attr.cleanup):
                    # cleanup() method
                    resources_to_close.append(('sync_close', attr, 'cleanup'))
                elif all(hasattr(attr, name) for name in ('__enter__', '__exit__')):
                    # Context manager protocol
                    resources_to_close.append(('context_manager', attr, None))
                elif all(hasattr(attr, name) for name in ('__aenter__', '__aexit__')):
                    # Async context manager protocol
                    resources_to_close.append(('async_context_manager', attr, None))

                # Check for context managers
                elif hasattr(attr, '__exit__') and hasattr(attr, '__enter__'):
                    resources_to_close.append(('context_manager', attr))
            except Exception:
                # Ignore any attributes that can't be accessed
                pass

        # Attempt to close resources
        for resource_item in resources_to_close:
            resource = None
            resource_type = None
            method_name = None
            try:
                # Handle different tuple lengths
                if len(resource_item) == 2:
                    resource_type, resource = resource_item
                elif len(resource_item) == 3:
                    resource_type, resource, method_name = resource_item
                else:
                    # Skip items that don't match expected tuple lengths
                    continue

                if resource is not None:
                    if resource_type == 'async_close':
                        if method_name == 'aclose':
                            await resource.aclose()
                        elif method_name == 'close':
                            await resource.close()
                    elif resource_type == 'sync_close':
                        if method_name == 'close':
                            resource.close()
                        elif method_name == 'disconnect':
                            resource.disconnect()
                        elif method_name == 'cleanup':
                            resource.cleanup()
                    elif resource_type == 'context_manager':
                        resource.__exit__(exc_type, exc_val, exc_tb)
                    elif resource_type == 'async_context_manager':
                        await resource.__aexit__(exc_type, exc_val, exc_tb)
            except Exception as cleanup_error:
                # Log or handle cleanup errors without interrupting other cleanups
                logging.warning("Warning: Error cleaning up resource %s: %s", resource, cleanup_error, exc_info=True)

        # Propagate any original exceptions
        return False
