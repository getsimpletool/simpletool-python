from simpletool import SimpleTool, List
from simpletool.types import TextContent
from simpletool.models import SimpleInputModel
from pydantic import Field
import asyncio


class MyInputModel(SimpleInputModel):
    """Input model for the MyTool"""
    text: str = Field(description="An input field for testing")


# Define run function
async def my_run(arguments: dict) -> List[TextContent]:
    """Execute the tool with the given arguments"""
    # Convert dict to model
    args = MyInputModel(**arguments)
    return [TextContent(text=f"You said: {args.text}")]


# Create tool using factory method
my_tool = SimpleTool.create(
    name="my_tool",
    description="A tool for testing",
    input_model=MyInputModel,
    run_fn=my_run
)


async def main(t: str):
    return my_tool, await my_tool.run({"text": t})


if __name__ == "__main__":
    # Run the tool
    my_tool, r = asyncio.run(main("Hello, world!"))

    print("----------------------------------------------------------------------")
    print("MyTool Return Value:")
    print(f"type: {type(r)}")
    print(str(r))

    print("----------------------------------------------------------------------")
    print("String Representation - str(my_tool):")
    print(f"Type: {type(str(my_tool))}")
    print(str(my_tool))

    print("\nTool Details Print - my_tool.info:")
    print(f"Type: {type(my_tool.info)}")
    print(my_tool.info)
