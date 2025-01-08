"""
Pytest tests for simpletool.schema module.
"""
from pydantic import BaseModel, Field, ConfigDict
from simpletool.schema import NoTitleDescriptionJsonSchema


class TestModel(BaseModel):
    test_field: str = Field(description="A test field with description")
    another_field: int = Field(title="Another Field")

    model_config = ConfigDict(title=None, description=None)  # type: ignore


def test_no_title_description_json_schema():
    """Test NoTitleDescriptionJsonSchema removes titles and descriptions."""
    # Generate schema using custom JSON schema generator
    schema_generator = NoTitleDescriptionJsonSchema()
    schema = schema_generator.generate(TestModel)

    # Assert no top-level description or title
    assert 'description' not in schema
    assert 'title' not in schema

    # Assert no property-level titles or descriptions
    assert 'properties' in schema
    for prop in schema['properties'].values():
        assert 'description' not in prop
        assert 'title' not in prop
