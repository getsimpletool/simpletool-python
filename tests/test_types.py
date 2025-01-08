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
    ErrorContent
)


def test_text_content():
    """Test TextContent model."""
    text_content = TextContent(type="text", text="Hello, World!")
    assert text_content.type == "text"
    assert text_content.text == "Hello, World!"


def test_image_content_valid():
    """Test valid ImageContent."""
    # Create a base64 encoded image
    base64_image = base64.b64encode(b"test image data").decode('utf-8')
    image_content = ImageContent(
        type="image",
        data=base64_image,
        mime_type="image/png"
    )
    assert image_content.type == "image"
    assert image_content.data == base64_image
    assert image_content.mime_type == "image/png"


def test_image_content_camel_case_conversion():
    """Test camelCase to snake_case conversion for ImageContent."""
    image_content = ImageContent(**{
        "type": "image",
        "data": base64.b64encode(b"test").decode('utf-8'),
        "mimeType": "image/jpeg"
    })
    assert image_content.mime_type == "image/jpeg"


def test_image_content_invalid_base64():
    """Test ImageContent with invalid base64 data."""
    with pytest.raises(PydanticValidationError):
        ImageContent(type="image", data="not-base64-data")


def test_file_content_valid():
    """Test valid FileContent."""
    base64_file = base64.b64encode(b"test file data").decode('utf-8')
    file_content = FileContent(
        type="file",
        data=base64_file,
        file_name="test.txt",
        mime_type="text/plain"
    )
    assert file_content.type == "file"
    assert file_content.data == base64_file
    assert file_content.file_name == "test.txt"
    assert file_content.mime_type == "text/plain"


def test_file_content_camel_case_conversion():
    """Test camelCase to snake_case conversion for FileContent."""
    base64_file = base64.b64encode(b"test").decode('utf-8')
    file_content = FileContent(**{
        "type": "file",
        "data": base64_file,
        "fileName": "test.txt",
        "mimeType": "text/plain"
    })
    assert file_content.file_name == "test.txt"
    assert file_content.mime_type == "text/plain"


def test_file_content_invalid_base64():
    """Test FileContent with invalid base64 data."""
    with pytest.raises(PydanticValidationError):
        FileContent(type="file", data="not-base64-data")


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


def test_error_data():
    """Test ErrorContent model."""
    error = ErrorContent(
        code=404,
        message="Resource not found",
        data={"details": "Additional error info"}
    )
    assert error.code == 404
    assert error.message == "Resource not found"
    assert error.data == {"details": "Additional error info"}
