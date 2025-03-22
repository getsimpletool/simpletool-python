import gc
import json
import logging
import os
import psutil
import random
import sys
from abc import ABC, abstractmethod
from collections.abc import Sequence as ABCSequence
from contextlib import AsyncExitStack
from functools import wraps
from pathlib import Path
from typing import get_args, get_origin
from typing import List, Dict, Any, Union, Type, Literal, ClassVar, Sequence, Tuple, TypeVar, Optional, Callable
from typing import AnyStr, Awaitable, Coroutine, TypeAlias   # noqa: F401, F403
from weakref import WeakMethod, ref, WeakSet

# Import the real asyncio module and re-export it
import asyncio as _asyncio

# Third-party imports
from pydantic import BaseModel
from pydantic import Field  # noqa: F401
from pydantic.fields import FieldInfo

# Local imports
from simpletool.types import (
    Content, TextContent, ImageContent, FileContent,
    ResourceContent, BoolContent, ErrorContent
)
from simpletool.models import SimpleInputModel, SimpleToolResponseModel
from simpletool.schema import NoTitleDescriptionJsonSchema
from simpletool.errors import ValidationError

# Re-export all public attributes from the real asyncio module
# This makes simpletool.asyncio behave like the real asyncio module
_this_module = sys.modules[__name__]
for _name in dir(_asyncio):
    if not _name.startswith('_'):  # Only export public attributes
        setattr(_this_module, _name, getattr(_asyncio, _name))

# Add any simpletool.asyncio specific functionality below this line

# When using asyncio in this module, use _asyncio to refer to the original module
# For example: _asyncio.create_task() instead of asyncio.create_task()

# Type for input arguments - can be dict or any model inheriting from SimpleInputModel
T = TypeVar('T', Dict[str, Any], SimpleInputModel)

# Define a type alias for content types instead of using a TypeVar
ContentType: TypeAlias = Union[Content, TextContent, ImageContent, FileContent, ResourceContent, BoolContent, ErrorContent]

# Define a type alias for response types that can be either Sequence or List of ContentType
ResponseType: TypeAlias = Union[Sequence[ContentType], List[ContentType]]

# Threshold for what we consider a "large" object (1MB)
LARGE_OBJECT_THRESHOLD = 1024 * 1024  # 1MB in bytes


def get_valid_content_types() -> Tuple[Type, ...]:
    """Directly return the types from the ContentType definition as a tuple"""
    return get_args(ContentType)


def validate_tool_output(func):
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> ResponseType:
        result = await func(*args, **kwargs)
        if not isinstance(result, (list, tuple)):
            raise ValidationError("output", "Tool output must be a list or tuple")

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
                return await _asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except _asyncio.TimeoutError:
                return [ErrorContent(
                    code=408,  # Request Timeout
                    error=f"Tool execution timed out after {seconds} seconds",
                    data={"timeout": seconds}
                )]
        return wrapper
    return decorator


class SimpleTool(ABC):
    """Base class for all simple tools."""
    # Default timeout - 60 seconds
    DEFAULT_TIMEOUT = 60

    # Default memory limit - 200MB
    DEFAULT_MEMORY_LIMIT = 200 * 1024 * 1024  # 200MB in bytes

    # Class attributes that must be defined by subclasses
    name: ClassVar[str]
    description: ClassVar[str]
    input_model: ClassVar[Type[SimpleInputModel]]  # This is a class variable, not an instance field

    # Private attributes with type hints
    _timeout: float
    _memory_limit: int
    _process: psutil.Process
    _large_objects: WeakSet
    _callbacks: List
    _resources: List
    _exit_stack: AsyncExitStack
    input_schema: Dict[str, Any]
    output_schema: Optional[Dict[str, Any]]
    output_model: Optional[Type[SimpleInputModel]]

    def __new__(cls, *args, **kwargs):
        """
        Create and initialize SimpleTool instance.
        This runs BEFORE any __init__, so our initialization is guaranteed.
        """
        # Validate required class attributes
        if not hasattr(cls, 'name') or not isinstance(cls.name, str):
            raise ValueError(f"Class {cls.__name__} must define 'name' as a string")
        if not hasattr(cls, 'description') or not isinstance(cls.description, str):
            raise ValueError(f"Class {cls.__name__} must define 'description' as a string")
        if not hasattr(cls, 'input_model') or not issubclass(cls.input_model, SimpleInputModel):
            raise ValueError(f"Class {cls.__name__} must define 'input_model' as a subclass of SimpleInputModel")

        instance = super().__new__(cls)

        # Get timeout from kwargs or use default
        timeout = kwargs.get('timeout', cls.DEFAULT_TIMEOUT)
        instance._timeout = timeout if timeout is not None else cls.DEFAULT_TIMEOUT

        # Initialize memory monitoring
        instance._memory_limit = cls.DEFAULT_MEMORY_LIMIT
        instance._process = psutil.Process(os.getpid())

        # Initialize memory tracking
        instance._large_objects = WeakSet()  # Track large objects without creating strong references

        # Initialize callbacks with weak references
        instance._callbacks = []

        # Initialize resource management
        instance._resources = []
        instance._exit_stack = AsyncExitStack()

        # Initialize schemas
        instance.input_schema = instance._sort_input_schema(
            cls.input_model.model_json_schema()
        )

        # Get the return type annotation of the run method
        run_method = cls.run
        if not hasattr(run_method, '__annotations__') or 'return' not in run_method.__annotations__:
            raise ValidationError(
                "run_return_type",
                f"Method 'run' in {cls.__name__} must declare return type annotation"
            )

        return_type = run_method.__annotations__['return']
        origin = get_origin(return_type)

        if origin not in (list, tuple, Sequence, ABCSequence):
            raise ValidationError(
                "run_return_type",
                f"Method 'run' in {cls.__name__} must return List or Sequence. Got {return_type}"
            )

        instance.output_model = return_type

        # Generate output schema from output model if available
        if instance.output_model is not None:
            # Get inner type(s) from Sequence/List
            if not hasattr(instance.output_model, '__origin__'):
                inner_types = []  # Invalid type annotation
            else:
                inner_type = get_args(instance.output_model)[0]  # Get the type inside Sequence/List
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

            # Filter only types that have model_json_schema
            valid_types = [t for t in inner_types if hasattr(t, 'model_json_schema')]
            if valid_types:
                instance.output_schema = {
                    "type": "array",
                    "items": {
                        "oneOf": [
                            t.model_json_schema() for t in valid_types
                        ]
                    }
                }
            else:
                instance.output_schema = None
        else:
            instance.output_schema = None

        return instance

    def __init__(self, *, timeout: Optional[float] = None):
        """
        Initialize SimpleTool.

        Args:
            timeout (float, optional): Custom timeout value in seconds. If not provided, uses DEFAULT_TIMEOUT.
        """
        pass

    async def __call__(self, arguments: Dict[str, Any]) -> ResponseType:
        """
        Execute the tool with memory management and validation.
        This is the main entry point that handles all the memory management.
        Users should implement run() instead of overriding this method.
        """
        try:
            # Monitor memory before execution
            self._monitor_memory()

            # Check memory pressure before execution
            await self._release_memory_under_pressure()

            # Auto-track arguments
            self._auto_track_large_object(arguments)

            try:
                # Validate arguments
                validated_arguments = self.input_model.model_validate(arguments)
            except ValidationError as e:
                return [ErrorContent(
                    code=400,  # Bad Request
                    error=f"Input validation error: {e}",
                    data={"validation_error": str(e)}
                )]

            # Execute with timeout if needed
            try:
                if self._timeout > 0:
                    result = await _asyncio.wait_for(
                        self.run(validated_arguments),
                        timeout=self._timeout
                    )
                else:
                    result = await self.run(validated_arguments)

                # Auto-track results
                if isinstance(result, (list, tuple)):
                    for item in result:
                        self._auto_track_large_object(item)
                else:
                    self._auto_track_large_object(result)

                return result

            except _asyncio.TimeoutError:
                return [ErrorContent(
                    code=408,  # Request Timeout
                    error=f"Tool execution timed out after {self._timeout} seconds",
                    data={"timeout": self._timeout}
                )]

            # Check memory pressure after execution
            await self._release_memory_under_pressure()

            # Monitor memory after execution
            self._monitor_memory()

        except Exception as e:
            logging.error("Error during tool execution: %s", e)
            raise
        finally:
            # Clean callbacks after each run
            self._clean_callbacks()

    @abstractmethod
    @validate_tool_output
    async def run(self, arguments: T) -> ResponseType:
        """
        Execute the tool with the given arguments.
        This is the method that tool developers should implement.

        Args:
            arguments: Input arguments. Can be either a dict or SimpleInputModel instance.

        Returns:
            Tool execution results. Must be a sequence of valid content types.
        """
        raise NotImplementedError("Subclass must implement run()")

    def _auto_track_large_object(self, obj: Any) -> None:
        """
        Automatically track object if it exceeds the size threshold.
        This is called internally - no user intervention needed.
        """
        try:
            obj_size = sys.getsizeof(obj)
            if obj_size > LARGE_OBJECT_THRESHOLD:
                self._large_objects.add(obj)
                logging.debug(
                    "Auto-tracking large object of type %s (size: %.2fMB)",
                    type(obj).__name__,
                    obj_size / 1024 / 1024
                )
        except Exception as e:
            logging.debug("Error checking object size: %s", e)

    async def _register_resource(self, resource: Any) -> None:
        """
        Register a resource for automatic cleanup.
        Resources will be cleaned up in reverse order of registration.

        Args:
            resource: The resource to register. Must have close() or __aclose__() method.
        """
        if not resource:
            return

        if not (hasattr(resource, 'close') or hasattr(resource, '__aclose__')):
            logging.warning("Resource %s has no close or __aclose__ method", resource)
            return

        self._resources.append(resource)
        if hasattr(resource, '__aclose__'):
            await self._exit_stack.enter_async_context(resource)
        else:
            self._exit_stack.push(resource)

        logging.debug("Registered resource: %s", resource)

    async def _close_resource(self, resource: Any) -> None:
        """
        Safely close a single resource.

        Args:
            resource: The resource to close
        """
        try:
            if hasattr(resource, '__aclose__'):
                await resource.__aclose__()
            elif hasattr(resource, 'close'):
                resource.close()
        except Exception as e:
            logging.error("Error closing resource %s: %s", resource, e)

    async def _close_all_resources(self) -> None:
        """
        Close all registered resources in reverse order.
        Ensures all resources are attempted to be closed even if some fail.
        """
        errors = []

        # Close resources in reverse order (LIFO)
        while self._resources:
            resource = self._resources.pop()
            try:
                await self._close_resource(resource)
            except Exception as e:
                errors.append(e)
                logging.error("Error during resource cleanup: %s", e)

        if errors:
            logging.error("Encountered %d errors during resource cleanup", len(errors))

    async def __aenter__(self):
        """
        Async context manager entry point for resource initialization
        - Proper initialization of resources
        - Guaranteed cleanup of resources, even if exceptions occur
        - Deterministic resource lifecycle management
        """
        await self._exit_stack.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        """
        Async context manager exit point for resource cleanup.
        Ensures all resources are properly closed in reverse order.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred

        Returns:
            bool: False to propagate exceptions, True to suppress them
        """
        try:
            # First, run explicit cleanup
            await self.cleanup()

            # Then close all resources in reverse order
            await self._close_all_resources()

            # Finally, exit the AsyncExitStack
            await self._exit_stack.__aexit__(exc_type, exc_val, exc_tb)

        except Exception as e:
            logging.error("Error during __aexit__: %s", e)
            # Re-raise the original exception if there was one
            if exc_type is not None:
                return False
            raise
        finally:
            # Clear resource list
            self._resources.clear()

        # Don't suppress exceptions
        return False

    async def cleanup(self) -> None:
        """Explicit cleanup of resources and memory"""
        try:
            # First try to release memory under pressure
            await self._release_memory_under_pressure()

            # Clean callbacks first
            self._clean_callbacks()

            # Clear any large data structures
            if hasattr(self, 'input_schema') and isinstance(self.input_schema, dict):
                self.input_schema.clear()
            if hasattr(self, 'output_schema') and isinstance(self.output_schema, dict):
                self.output_schema.clear()

            # Clear any cached properties
            cached_attrs = [attr for attr in self.__dict__ if attr.startswith('_cached_')]
            for attr in cached_attrs:
                delattr(self, attr)

            # Clear callbacks
            self._callbacks.clear()

            # Clear large objects tracking
            self._large_objects.clear()

            # Force garbage collection
            gc.collect()

            # Final memory check
            self._monitor_memory()

        except Exception as e:
            logging.error("Error during cleanup: %s", e)
            raise

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
            "name": str(self.name),
            "description": str(self.description),
            "input_schema": sorted_input_schema,
            "output_schema": self.output_schema
        }).encode("utf-8").decode("unicode_escape")

    def __repr__(self):
        # Create a SimpleToolResponseModel internally
        response_model = SimpleToolResponseModel(
            name=self.name,
            description=self.description,
            input_schema=self.input_schema,
            output_schema=self.output_schema
        )
        # Get the original repr
        original_repr = repr(response_model)
        # Replace with the actual child class name
        return original_repr.replace("SimpleToolResponseModel", self.__class__.__name__)

    def add_callback(self, callback: Callable) -> None:
        """Add callback using weak reference to prevent memory leaks"""
        if callback is None:
            return
        # Use WeakMethod for bound methods, ref for regular functions
        weak_cb = WeakMethod(callback) if hasattr(callback, '__self__') else ref(callback)
        self._callbacks.append(weak_cb)

    def _clean_callbacks(self) -> None:
        """Clean up dead callback references"""
        self._callbacks = [cb for cb in self._callbacks if cb() is not None]

    def _monitor_memory(self) -> None:
        """Monitor memory usage and log warning if exceeding limit"""
        try:
            mem_info = self._process.memory_info()
            if mem_info.rss > self._memory_limit:
                logging.warning(
                    "Memory usage warning: Current usage %.2fMB exceeds limit %.2fMB",
                    mem_info.rss / 1024 / 1024,
                    self._memory_limit / 1024 / 1024
                )
        except Exception as e:
            logging.error("Error monitoring memory: %s", e)

    async def _release_memory_under_pressure(self) -> None:
        """
        Release memory when under pressure.
        This method is called automatically when memory usage exceeds 90% of the limit.
        """
        current_memory = self._process.memory_info().rss
        if current_memory > self._memory_limit * 0.9:  # 90% of limit
            logging.warning(
                "Memory pressure detected: Current usage %.2fMB exceeds 90%% of limit %.2fMB",
                current_memory / 1024 / 1024,
                self._memory_limit / 1024 / 1024
            )

            # Force collection of all generations
            for generation in range(3):
                gc.collect(generation)

            # Clear any dead references in our tracking sets
            self._clean_callbacks()

            # Log remaining large objects
            remaining_objects = len(self._large_objects)
            if remaining_objects > 0:
                logging.warning("Still tracking %d large objects after cleanup", remaining_objects)

    def to_json(self, input_model: Type[BaseModel], schema: Literal["full", "no_title_description"] = "no_title_description"):
        """Convert the InputModel to JSON schema."""
        if schema == "no_title_description":
            return input_model.model_json_schema(schema_generator=NoTitleDescriptionJsonSchema)
        return input_model.model_json_schema()

    @property
    def info(self) -> Dict[str, Any]:
        """Return a dictionary representation of the tool."""
        sorted_input_schema = self._sort_input_schema(self.input_schema)
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": sorted_input_schema,
            "output_schema": self.output_schema
        }

    @property
    def to_dict(self) -> Dict[str, Any]:
        """Convert content to a dictionary representation"""
        sorted_input_schema = self._sort_input_schema(self.input_schema)
        return {
            "name": self.name,
            "description": str(self.description),
            "input_schema": sorted_input_schema
        }

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

    def __reduce__(self):
        """Make SimpleTool picklable by only serializing essential attributes."""
        # Get module name from the module path
        module = sys.modules.get(self.__class__.__module__)
        module_file = getattr(module, '__file__', None) if module else None
        if module_file and isinstance(module_file, str):
            # Use the actual module file name without .py extension
            module_name = Path(module_file).stem
            self.__class__.__module__ = module_name
        else:
            # Fallback to tool name only if we really have to
            self.__class__.__module__ = self.name

        return (self.__class__, (), {
            'name': self.name,
            'description': self.description,
            'input_schema': getattr(self, 'input_schema', None),
            'output_schema': getattr(self, 'output_schema', None),
            '_timeout': getattr(self, '_timeout', self.DEFAULT_TIMEOUT)
        })

    def __setstate__(self, state):
        """Restore state after unpickling."""
        for key, value in state.items():
            setattr(self, key, value)

    def _select_random_api_key(self, env_name: str, env_value: str) -> str:
        """ Select random api key from env_value only if env_name contains 'API' and 'KEY' """
        if 'API' in env_name.upper() and 'KEY' in env_name.upper():
            api_keys = list(filter(bool, [key.strip() for key in env_value.split(',')]))
            if not api_keys:
                return ""
            return api_keys[0] if len(api_keys) == 1 else random.choice(api_keys)
        return env_value  # return original value if not an API key

    def get_env(self, arguments: dict, prefix: Union[str, List[str], None] = None) -> Dict[str, str]:
        """Check if arguments contains `env` and merge them with os.environ"""
        envs = {}

        # 1) lets take os env first
        for key, value in os.environ.items():
            envs[key] = value

        # 2) lets take arguments `env` and override os env
        if isinstance(arguments.get('env', None), dict):
            for key, value in arguments['env'].items():
                envs[key] = str(value)

        # 3) Placeholder

        # 4) lets keep only those envs with prefixes
        if prefix is None:
            pass
        elif isinstance(prefix, str):
            envs = {k: v for k, v in envs.items() if k.startswith(prefix)}
        elif isinstance(prefix, list):
            envs = {k: v for k, v in envs.items() if any(k.startswith(pre) for pre in prefix)}

        # 5) lets replace API_KEYS with random selected one if it is a list of multiple keys
        for key, value in envs.items():
            envs[key] = self._select_random_api_key(key, value)

        return envs

    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        input_model: Type[SimpleInputModel],
        run_fn: Callable[[SimpleInputModel], Awaitable[ResponseType]]
    ) -> 'SimpleTool':
        """
        Create a SimpleTool instance without subclassing..f

        Args:
            name: Name of the tool
            description: Description of the tool
            input_model: Input model class (must inherit from SimpleInputModel)
            run_fn: Async function that implements the tool's logic

        Returns:
            SimpleTool instance

        Example:
            ```python
            async def my_run(arguments: MyInputModel) -> List[TextContent]:
                return [TextContent(text=f"You said: {arguments.text}")]

            my_tool = SimpleTool.create(
                name="my_tool",
                description="A tool for testing",
                input_model=MyInputModel,
                run_fn=my_run
            )
            ```
        """
        # Create a new dynamic class
        tool_cls = type(
            f"Dynamic{name.title()}Tool",
            (cls,),
            {
                "name": name,
                "description": description,
                "input_model": input_model,
                "run": staticmethod(run_fn)
            }
        )

        # Return an instance
        return tool_cls()


__all__ = [
    'SimpleTool',
    'Content',
    'TextContent',
    'ImageContent',
    'FileContent',
    'ResourceContent',
    'BoolContent',
    'ErrorContent',
    'ContentType',
    'ResponseType',
    'List',
    'Dict',
    'Any',
    'Union',
    'Optional',
    'get_valid_content_types',
    'validate_tool_output',
    'set_timeout'
]
