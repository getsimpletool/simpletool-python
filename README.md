# Simpletool

A Python package for creating simple tool class with a base class and data type definitions.

## Overview

This package provides a `BaseTool` class that serves as the foundation for building various tools. It includes functionalities for:

-   Executing tools with input arguments.
-   Handling environment variables.
-   Generating JSON schemas for input models.

The package also defines data types for content, resources, and errors, ensuring consistency and clarity in tool development.

## Core Components

### `BaseTool` Class

The `BaseTool` class is an abstract base class that all tools should inherit from. It provides the following methods:

-   `run(arguments)`: Executes the tool with the given arguments. This method should be overridden by subclasses to implement the tool's logic.
-   `execute(arguments)`: An alternative name for the `run` method.
-   `get_env(arguments, prefix)`: Retrieves environment variables from arguments, `os.environ`, and resources, optionally filtering by a prefix.
-   `to_json(input_model, schema)`: Converts an input model to a JSON schema.

### Data Types

The `types.py` file defines the following data types:

-   `Content`: Base class for content types.
-   `TextContent`: Represents text content.
-   `ImageContent`: Represents image content.
-   `ResourceContents`: Represents the contents of a resource.
-   `TextResourceContents`: Represents the contents of a text resource.
-   `BlobResourceContents`: Represents the contents of a blob resource.
-   `EmbeddedResource`: Represents an embedded resource.
-   `ErrorData`: Represents error information.

## Installation

To install the package, use pip:

```bash
pip install simpletool
```

## Usage

To create a new tool, inherit from the `BaseTool` class and implement the `run` or `execute` method. The input schema can be automatically generated from a Pydantic model using the `to_json` method.

### Example 1: Input schema as a dictionary

```python
from simpletool import BaseTool, TextContent
from typing import Dict, Any, List, Union

class MyTool(BaseTool):
    name = "my_tool"
    description = "A simple example tool"
    input_schema = {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "The message to print"
            }
        },
        "required": ["message"]
    }

    async def run(self, arguments: Dict[str, Any]) -> Union[List[TextContent], ErrorData]:
        message = arguments["message"]
        return [TextContent(type="text", text=f"You said: {message}")]
```

### Example 2: Input schema as a Pydantic model

```python
from simpletool import BaseTool, TextContent, NoTitleDescriptionJsonSchema
from typing import Dict, Any, List, Union
from pydantic import BaseModel, Field

class InputModel(BaseModel):
    """Input model for time conversion."""
    date_time_str: str = Field(
        description="The time to convert. Can be 'NOW' or a specific date and time in a format like 'YYYY-MM-DD HH:MM:SS'."
    )
    from_timezone: str = Field(
        default="",
        description="Source timezone (default: local timezone)"
    )
    to_timezone: str = Field(
        default="UTC", 
        description="Target timezone (default: UTC)"
    )
args_schema = InputModel.model_json_schema(schema_generator=NoTitleDescriptionJsonSchema)

class MyTool2(BaseTool):
    name = "my_tool2"
    description = "A second simple example tool"
    input_schema = InputModel2.model_json_schema(schema_generator=NoTitleDescriptionJsonSchema)

class InputModel2(BaseModel):
    """Input model for another tool."""
    name: str = Field(description="The name of the user.")
    age: int = Field(description="The age of the user.")

    async def run(self, arguments: Dict[str, Any]) -> Union[List[TextContent], ErrorData]:
        message = arguments["message"]
        return [TextContent(type="text", text=f"You said: {message}")]
```

### Accessing Tool Information

The `BaseTool` class provides several ways to access tool information:

-   `str(my_tool)`: Returns a one-line JSON string representation of the tool.
-   `my_tool.details`: Returns a one-line JSON string representation of the tool.
-   `my_tool.to_dict`: Returns a dictionary representation of the tool. Note that `my_tool.__dict__` is not the same as would return a dictionary containing all attributes of the object, including internal ones.

```python
from simpletool import BaseTool, NoTitleDescriptionJsonSchema
from simpletool.types import TextContent, ImageContent, EmbeddedResource, ErrorData
from pydantic import BaseModel, Field
from typing import List, Union


class InputSchema(BaseModel):
    """Input model for the MyTool"""
    message: str = Field(description="The message to print")


class MyTool(BaseTool):
    name = "my_tool"
    description = "A simple example tool"
    input_schema = InputSchema.model_json_schema(schema_generator=NoTitleDescriptionJsonSchema)

    async def run(self, arguments: dict) -> Union[List[TextContent | ImageContent | EmbeddedResource], ErrorData]:
        """Execute the tool with the given arguments"""
        # Validate input using Pydantic model
        input_model = InputSchema(**arguments)
        message = input_model.message
        return [TextContent(type="text", text=f"You said: {message}")]


my_tool = MyTool()
```



```python
print("\nString Representation - str(my_tool):")
print(f"Type: {type(str(my_tool))}")
print(str(my_tool))
# output:
#String Representation - str(my_tool):
#Type: <class 'str'>
#{"name": "my_tool", "description": "A simple example tool", "input_schema": {"properties": {"message": {"type": "string"}}, "required": ["message"], "type": "object"}}
```

```python
print("\nTool Details - my_tool.info:")
print(f"Type: {type(my_tool.info)}")
print(my_tool.info)
# output:
#Tool Details - my_tool.info:
#Type: <class 'str'>
#{
#    "name": "my_tool",
#    "description": "A simple example tool",
#    "input_schema": {
#        "properties": {
#            "message": {
#                "type": "string"
#            }
#        },
#        "required": [
#            "message"
#        ],
#        "type": "object"
#    }
#}
```

```python
print("\nDictionary Representation - my_tool.to_dict:")
print(f"Type: {type(my_tool.to_dict)}")
print(my_tool.to_dict)
# output:
#Dictionary Representation - my_tool.to_dict:
#Type: <class 'dict'>
#{'name': 'my_tool', 'description': 'A simple example tool', 'input_schema': {'properties': {'message': {'type': 'string'}}, 'required': ['message'], 'type': 'object'}}
```

## Dependencies

-   `pydantic>=2.0.0`
-   `typing-extensions`

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please submit a pull request with your changes.
