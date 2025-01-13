"""
Pytest tests for simpletool.types module.
"""
import base64
import pytest
from pydantic import ValidationError as PydanticValidationError
from simpletool.types import (
    TextContent,
    ImageContent,
    FileContent,
    ResourceContent,
    ErrorContent,
    BoolContent
)


def test_text_content():
    """Test TextContent model."""
    text_content = TextContent(type="text", text="Hello, World!")
    assert text_content.type == "text"
    assert text_content.text == "Hello, World!"

    # Test string input validation
    text_content_from_str = TextContent.validate_or_convert("Direct string input")
    assert text_content_from_str == {"text": "Direct string input"}


def test_image_content_valid():
    """Test valid ImageContent."""
    # Create a base64 encoded image
    base64_image = base64.b64encode(b"test image data").decode('utf-8')
    image_content = ImageContent(
        type="image",
        image=base64_image,
        mime_type="image/png"
    )
    assert image_content.type == "image"
    assert image_content.image == base64_image
    assert image_content.mime_type == "image/png"


def test_image_content_camel_case_conversion():
    """Test camelCase to snake_case conversion for ImageContent."""
    image_content = ImageContent(**{
        "type": "image",
        "image": base64.b64encode(b"test").decode('utf-8'),
        "mimeType": "image/jpeg"
    })
    assert image_content.mime_type == "image/jpeg"


def test_image_content_invalid_base64():
    """Test ImageContent with invalid base64 data."""
    with pytest.raises(PydanticValidationError):
        ImageContent(type="image", image="not-base64-data")


def test_image_content_direct_base64():
    """Test ImageContent with direct base64 string input."""
    base64_str = base64.b64encode(b"test direct data").decode('utf-8')
    image_data = ImageContent.validate_or_convert(base64_str)
    assert image_data == {"image": base64_str}

    # Test invalid base64 input
    with pytest.raises(ValueError, match="Image must be a valid base64 encoded string"):
        ImageContent.validate_or_convert("invalid base64 string")


def test_file_content_valid():
    """Test valid FileContent."""
    base64_file = base64.b64encode(b"test file data").decode('utf-8')
    file_content = FileContent(
        type="file",
        file=base64_file,
        file_name="test.txt",
        mime_type="text/plain"
    )
    assert file_content.type == "file"
    assert file_content.file == base64_file
    assert file_content.file_name == "test.txt"
    assert file_content.mime_type == "text/plain"


def test_file_content_camel_case_conversion():
    """Test camelCase to snake_case conversion for FileContent."""
    base64_file = base64.b64encode(b"test").decode('utf-8')
    file_content = FileContent(**{
        "type": "file",
        "file": base64_file,
        "fileName": "test.txt",
        "mimeType": "text/plain"
    })
    assert file_content.file_name == "test.txt"
    assert file_content.mime_type == "text/plain"


def test_file_content_invalid_base64():
    """Test FileContent with invalid base64 data."""
    with pytest.raises(PydanticValidationError):
        FileContent(type="file", file="not-base64-data")


def test_file_content_direct_base64():
    """Test FileContent with direct base64 string input."""
    base64_str = base64.b64encode(b"test direct file data").decode('utf-8')
    file_data = FileContent.validate_or_convert(base64_str)
    assert file_data == {"file": base64_str}

    # Test invalid base64 input
    with pytest.raises(ValueError, match="File must be a valid base64 encoded string"):
        FileContent.validate_or_convert("invalid base64 string")


def test_resource_contents():
    """Test ResourceContent model."""
    resource = ResourceContent(
        uri="https://example.com/resource",
        name="Test Resource",
        description="A test resource",
        mime_type="application/json"
    )
    assert str(resource.uri) == "https://example.com/resource"
    assert resource.name == "Test Resource"
    assert resource.description == "A test resource"
    assert resource.mime_type == "application/json"


def test_text_resource_contents():
    """Test TextResourceContents model."""
    text_resource = ResourceContent(
        uri="https://example.com/text",
        name="Text Resource",
        text="Sample text content"
    )
    assert str(text_resource.uri) == "https://example.com/text"
    assert text_resource.name == "Text Resource"
    assert text_resource.text == "Sample text content"


def test_blob_resource_contents():
    """Test BlobResourceContents model."""
    blob_resource = ResourceContent(
        uri="https://example.com/blob",
        name="Blob Resource",
        blob=base64.b64encode(b"blob data").decode('utf-8')
    )
    assert str(blob_resource.uri) == "https://example.com/blob"
    assert blob_resource.name == "Blob Resource"
    assert blob_resource.blob is not None


def test_resource_content_direct_input():
    """Test ResourceContent with direct string input."""
    uri = "https://example.com/resource"
    resource_data = ResourceContent.validate_or_convert(uri)
    assert resource_data == {"uri": uri, "name": uri}


def test_error_data():
    """Test ErrorContent model."""
    error = ErrorContent(
        code=404,
        error="Resource not found",
        data={"details": "Additional error info"}
    )
    assert error.code == 404
    assert error.error == "Resource not found"
    assert error.data == {"details": "Additional error info"}


def test_bool_content():
    """Test BoolContent model."""
    bool_content = BoolContent(type="blob", bool=True)
    assert bool_content.type == "blob"
    assert bool_content.bool is True

    bool_content_from_bool = BoolContent(**{"bool": True})
    assert bool_content_from_bool.bool is True

    bool_content_with_desc = BoolContent(
        type="blob", 
        bool=False, 
        description="A boolean content"
    )
    assert bool_content_with_desc.bool is False
    assert bool_content_with_desc.description == "A boolean content"


def test_bool_content_direct_input():
    """Test BoolContent with direct boolean input."""
    bool_data = BoolContent.validate_or_convert(True)
    assert bool_data == {"bool": True}

    bool_data_false = BoolContent.validate_or_convert(False)
    assert bool_data_false == {"bool": False}
