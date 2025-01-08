from simpletool import SimpleTool, Field, List
from simpletool.types import TextContent
from simpletool.models import SimpleInputModel
import asyncio


class MyInputModel(SimpleInputModel):
    """Input model for the MyTool"""
    text: str = Field(description="An input field for testing")


class MyTool(SimpleTool):
    name = "my_tool"
    description = "A tool for testing"
    input_model = MyInputModel

    async def run(self, arguments: dict) -> List[TextContent]:
        """Execute the tool with the given arguments"""
        # Validate input using Pydantic model
        arg: MyInputModel = MyInputModel(**arguments)
        return [TextContent(text=f"You said: {arg.text}")]


async def main(t: str):
    my_tool = MyTool()
    return my_tool, await my_tool.run({"text": t})


my_tool, r = asyncio.run(main("Hello, world!"))

print("----------------------------------------------------------------------")
print("MyTool Return Value:")
print(f"type: {type(r)}")
print(str(r))

print("----------------------------------------------------------------------")
# Demonstrate different ways of accessing tool information
print("String Representation - str(my_tool):")
print(f"Type: {type(str(my_tool))}")
print(str(my_tool))

print("\nTool Details - my_tool.info:")
print(f"Type: {type(my_tool.info)}")
print(my_tool.info)

print("\nDictionary Representation - my_tool.to_dict:")
print(f"Type: {type(my_tool.to_dict)}")
print(my_tool.to_dict)


print("----------------------------------------------------------------------")
# Demonstrate in/out - model/schema
print("Input: MODEL:")
print(f"Type: {type(my_tool.input_model)}")
print(my_tool.input_model)

print("\nInput: SCHEMA:")
print(f"Type: {type(my_tool.input_schema)}")
print(my_tool.input_schema)

print("\nOutput: MODEL:")
print(f"Type: {type(my_tool.output_model)}")
print(my_tool.output_model)

print("\nOutput: SCHEMA:")
print(f"Type: {type(my_tool.output_schema)}")
print(my_tool.output_schema)
print("----------------------------------------------------------------------")
