""" Type definitions for the simpletool package."""
from typing import Literal, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic.networks import AnyUrl
import base64


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
    mime_type: str | None = None
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    @model_validator(mode='before')
    @classmethod
    def _convert_camel_to_snake_names(cls, data):
        if isinstance(data, dict) and 'mimeType' in data:
            data['mime_type'] = data.pop('mimeType')
        return data

    @field_validator('data')
    def validate_base64(cls, value):
        try:
            # Attempt to decode the base64 data
            base64.b64decode(value, validate=True)
            return value
        except Exception:
            raise ValueError("Data must be a valid base64 encoded string")


class FileContent(BaseModel):
    """File content with verification of encoded base64 data and mime type for a message."""
    type: Literal["file"]
    data: str
    file_name: str | None = None
    mime_type: str | None = None
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    @model_validator(mode='before')
    @classmethod
    def _convert_camel_to_snake_names(cls, data):
        if isinstance(data, dict) and 'mimeType' in data:
            data['mime_type'] = data.pop('mimeType')
        if isinstance(data, dict) and 'fileName' in data:
            data['file_name'] = data.pop('fileName')
        return data

    @field_validator('data')
    def validate_base64(cls, value):
        try:
            # Attempt to decode the base64 data
            base64.b64decode(value, validate=True)
            return value
        except Exception:
            raise ValueError("Data must be a valid base64 encoded string")


class ResourceContents(BaseModel):
    """The contents of a resource, embedded into a prompt or tool call result."""
    uri: AnyUrl
    name: str
    description: str | None = None
    mime_type: str | None = None
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    @model_validator(mode='before')
    @classmethod
    def _convert_camel_to_snake_names(cls, data):
        if isinstance(data, dict) and 'mimeType' in data:
            data['mime_type'] = data.pop('mimeType')
        return data


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
