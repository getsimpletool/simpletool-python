from simpletool.types import Content, TextContent, ImageContent, EmbeddedResource, TextResourceContents


def test_content_base():
    """Test the base content type."""
    content = Content(type="text")
    assert content.type in ["text", "image", "resource"]


def test_text_content():
    """Test text content type."""
    text_content = TextContent(type="text", text="Hello, world!")
    assert text_content.type == "text"
    assert text_content.text == "Hello, world!"


def test_image_content():
    """Test image content type."""
    image_content = ImageContent(type="image", data="base64_encoded_image", mimeType="image/jpeg")
    assert image_content.type == "image"
    assert image_content.data == "base64_encoded_image"
    assert image_content.mime_type == "image/jpeg"


def test_resource_contents():
    """Test resource contents."""
    text_resource = TextResourceContents(
        uri="https://example.com/document.txt",
        mimeType="text/plain",
        text="Sample text content"
    )

    resource = EmbeddedResource(
        type="resource",
        resource=text_resource
    )

    assert resource.type == "resource"
    assert str(resource.resource.uri) == "https://example.com/document.txt"
    assert resource.resource.mime_type == "text/plain"
    assert resource.resource.text == "Sample text content"
