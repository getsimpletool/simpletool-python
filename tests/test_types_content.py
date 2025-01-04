import base64
from simpletool.types import Content, TextContent, ImageContent, EmbeddedResource, TextResourceContents, FileContent, ResourceContents
import pytest


def test_content_base():
    """Test the base content type."""
    content = Content(type="text")
    assert content.type in ["text", "image", "resource", "file"]


def test_text_content():
    """Test text content type."""
    text_content = TextContent(type="text", text="Hello, world!")
    assert text_content.type == "text"
    assert text_content.text == "Hello, world!"

    # Test model validator with no changes
    text_content_with_extra = TextContent(type="text", text="Hello, world!", extra_field="test")
    assert text_content_with_extra.type == "text"
    assert text_content_with_extra.text == "Hello, world!"


def test_image_content():
    """Test image content type."""
    base64_image = base64.b64encode(b"test image content").decode('utf-8')
    image_content = ImageContent(type="image", data=base64_image, mime_type="image/jpeg")
    assert image_content.type == "image"
    assert image_content.data == base64_image
    assert image_content.mime_type == "image/jpeg"

    # Test model validator with mimeType
    image_content_camel = ImageContent(type="image", data=base64_image, mimeType="image/jpeg")
    assert image_content_camel.type == "image"
    assert image_content_camel.data == base64_image
    assert image_content_camel.mime_type == "image/jpeg"

    # Test base64 validation
    valid_data = base64.b64encode(b"test image content").decode('utf-8')
    image_content_valid = ImageContent(type="image", data=valid_data, mime_type="image/png")
    assert image_content_valid.data == valid_data

    # Test base64 validation failure
    with pytest.raises(ValueError, match="Data must be a valid base64 encoded string"):
        ImageContent(type="image", data="invalid base64 data", mime_type="image/png")


def test_file_content():
    """Test file content type."""

    base64_file = base64.b64encode(b"test file content").decode('utf-8')

    file_content = FileContent(type="file", data=base64_file, mime_type="application/pdf", file_name="document.pdf")
    assert file_content.type == "file"
    assert file_content.data == base64_file
    assert file_content.mime_type == "application/pdf"
    assert file_content.file_name == "document.pdf"

    # Test model validator with camelCase keys
    file_content_camel = FileContent(type="file", data=base64_file, mimeType="application/pdf", fileName="document.pdf")
    assert file_content_camel.type == "file"
    assert file_content_camel.data == base64_file
    assert file_content_camel.mime_type == "application/pdf"
    assert file_content_camel.file_name == "document.pdf"

    # Test base64 validation
    valid_data = base64.b64encode(b"test content").decode('utf-8')
    file_content_valid = FileContent(type="file", data=valid_data, mime_type="text/plain")
    assert file_content_valid.data == valid_data

    # Test base64 validation failure
    with pytest.raises(ValueError, match="Data must be a valid base64 encoded string"):
        FileContent(type="file", data="invalid base64 data", mime_type="text/plain")


def test_resource_contents():
    """Test resource contents."""
    text_resource = TextResourceContents(
        uri="https://example.com/main_document.txt",
        name="MyMainDocument",
        mime_type="text/plain",
        text="Sample text content"
    )

    resource = EmbeddedResource(
        type="resource",
        resource=text_resource
    )

    assert resource.type == "resource"
    assert str(resource.resource.uri) == "https://example.com/main_document.txt"
    assert resource.resource.mime_type == "text/plain"
    assert resource.resource.name == "MyMainDocument"
    assert resource.resource.text == "Sample text content"

    # Test model validator with mimeType
    text_resource_camel = TextResourceContents(
        uri="https://example.com/main_document.txt",
        name="MyMainDocument",
        mime_type="text/plain",
        text="Sample text content"
    )
    assert text_resource_camel.mime_type == "text/plain"


def test_text_resource_contents():
    """Test text resource contents."""
    text_resource = TextResourceContents(
        uri="https://example.com/document.txt",
        name="TestDocument",
        text="Sample text content"
    )

    assert str(text_resource.uri) == "https://example.com/document.txt"
    assert text_resource.name == "TestDocument"
    assert text_resource.text == "Sample text content"
    assert text_resource.description is None
    assert text_resource.mime_type is None

    # Test with description and mime_type
    text_resource_with_details = TextResourceContents(
        uri="https://example.com/document.txt",
        name="TestDocument",
        text="Sample text content",
        description="A test document",
        mime_type="text/plain"
    )

    assert str(text_resource_with_details.uri) == "https://example.com/document.txt"
    assert text_resource_with_details.name == "TestDocument"
    assert text_resource_with_details.text == "Sample text content"
    assert text_resource_with_details.description == "A test document"
    assert text_resource_with_details.mime_type == "text/plain"


def test_resource_contents_camel_to_snake_conversion():
    """Test the camel to snake case conversion for ResourceContents."""
    # Test conversion of mimeType to mime_type
    resource_camel = ResourceContents(
        uri="https://example.com/resource",
        name="TestResource",
        mimeType="application/json"
    )

    assert str(resource_camel.uri) == "https://example.com/resource"
    assert resource_camel.name == "TestResource"
    assert resource_camel.mime_type == "application/json"
    assert "mimeType" not in resource_camel.model_dump()


def test_get_valid_content_types():
    """Test that get_valid_content_types returns the correct content types."""
    from simpletool import get_valid_content_types
    from simpletool.types import ImageContent, TextContent, FileContent, EmbeddedResource, ErrorData

    valid_types = get_valid_content_types()
    assert set(valid_types) == {ImageContent, TextContent, FileContent, EmbeddedResource, ErrorData}


def test_file_content_base64_validation():
    """Test the base64 validation for FileContent."""
    from simpletool.types import FileContent

    # Valid base64 encoded data
    valid_data = base64.b64encode(b"test content").decode('utf-8')
    file_content = FileContent(type="file", data=valid_data, mime_type="text/plain")
    assert file_content.data == valid_data

    # Invalid base64 data
    with pytest.raises(ValueError, match="Data must be a valid base64 encoded string"):
        FileContent(type="file", data="invalid base64 data", mime_type="text/plain")
