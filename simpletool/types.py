""" Type definitions for the simpletool package."""
from typing import Literal, Any
from pydantic import BaseModel, ConfigDict, Field
from pydantic.networks import AnyUrl


class Content(BaseModel):
    """Base class for content types."""
    type: Literal["text", "image", "resource"]
    model_config = ConfigDict(extra="allow")


class TextContent(BaseModel):
    """Text content for a message."""
    type: Literal["text"]
    text: str
    model_config = ConfigDict(extra="allow")


class ImageContent(BaseModel):
    """Image content for a message."""
    type: Literal["image"]
    data: str
    mime_type: str = Field(alias="mimeType")
    model_config = ConfigDict(extra="allow")


class ResourceContents(BaseModel):
    """The contents of a resource, embedded into a prompt or tool call result."""
    uri: AnyUrl
    mime_type: str | None = Field(None, alias="mimeType")
    model_config = ConfigDict(extra="allow")


class TextResourceContents(ResourceContents):
    """ Tee contents of a text resource, embedded into a prompt or tool call result."""
    text: str


class BlobResourceContents(ResourceContents):
    """ The contents of a blob resource, embedded into a prompt or tool call result."""
    blob: str


class EmbeddedResource(BaseModel):
    """
    The contents of a resource, embedded into a prompt or tool call result.

    It is up to the client how best to render embedded resources for the benefit
    of the LLM and/or the user.
    """
    type: Literal["resource"]
    resource: TextResourceContents | BlobResourceContents
    model_config = ConfigDict(extra="allow")


class ErrorData(BaseModel):
    """Error information for JSON-RPC error responses."""
    code: int = Field(description="A number that indicates the error type that occurred.")
    message: str = Field(description="A short description of the error. The message SHOULD be limited to a concise single sentence.")
    data: Any | None = Field(default=None, description="Additional information about the error.")
    model_config = ConfigDict(extra="allow")
