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

# Demonstrate different ways of accessing tool information
print("\nString Representation - str(my_tool):")
print(f"Type: {type(str(my_tool))}")
print(str(my_tool))

print("\nTool Details - my_tool.info:")
print(f"Type: {type(my_tool.info)}")
print(my_tool.info)

print("\nDictionary Representation - my_tool.to_dict:")
print(f"Type: {type(my_tool.to_dict)}")
print(my_tool.to_dict)
