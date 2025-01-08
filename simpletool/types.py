""" Type definitions for the simpletool package."""
from typing import Literal, Any, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic.networks import AnyUrl
import base64

# -------------------------------------------------------------------------------------------------
# --- CONTENT CLASSES -----------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------


class Content(BaseModel):
    """Base class for content types."""
    type: Literal["text", "image", "resource", "file", "error", "video", "audio", "bool"]
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    @model_validator(mode='before')
    @classmethod
    def _convert_camel_to_snake_names(cls, data):
        if isinstance(data, dict) and 'mimeType' in data:
            data['mime_type'] = data.pop('mimeType')
        if isinstance(data, dict) and 'fileName' in data:
            data['file_name'] = data.pop('fileName')
        return data


class TextContent(Content):
    """Text content for a message."""
    type: Literal["text"] = "text"       # type: ignore
    text: str

    @model_validator(mode='before')
    @classmethod
    def validate_or_convert(cls, data):
        # If a string is passed directly, convert it to a dict with 'text' key
        if isinstance(data, str):
            return {"text": data}
        return data


class ImageContent(Content):
    """Image content for a message."""
    type: Literal["image"] = "image"  # type: ignore
    data: str
    mime_type: str | None = None
    description: Optional[str] | None = None

    @model_validator(mode='before')
    @classmethod
    def validate_or_convert(cls, data):
        # If a string is passed directly, assume it's base64 data
        if isinstance(data, str):
            # Validate base64 encoding
            try:
                base64.b64decode(data, validate=True)
                return {"data": data}
            except Exception as e:
                raise ValueError("Data must be a valid base64 encoded string") from e
        return data

    @field_validator('data')
    @classmethod
    def validate_base64(cls, value):
        try:
            base64.b64decode(value, validate=True)
            return value
        except Exception as e:
            raise ValueError("Data must be a valid base64 encoded string") from e


class FileContent(Content):
    type: Literal["file"] = "file"    # type: ignore
    data: str
    mime_type: str | None = None
    file_name: Optional[str] | None = None
    description: Optional[str] | None = None

    @model_validator(mode='before')
    @classmethod
    def validate_or_convert(cls, data):
        # If a string is passed directly, assume it's base64 data
        if isinstance(data, str):
            # Validate base64 encoding
            try:
                base64.b64decode(data, validate=True)
                return {"data": data}
            except Exception as e:
                raise ValueError("Data must be a valid base64 encoded string") from e
        return data

    @field_validator('data')
    @classmethod
    def validate_base64(cls, value):
        try:
            base64.b64decode(value, validate=True)
            return value
        except Exception as e:
            raise ValueError("Data must be a valid base64 encoded string") from e


class ResourceContent(Content):
    type: Literal["resource"] = "resource"  # type: ignore
    uri: AnyUrl
    name: str
    description: Optional[str] | None = None
    mime_type: str | None = None

    @model_validator(mode='before')
    @classmethod
    def validate_or_convert(cls, data):
        # If a string (URL) is passed, try to convert it to a dict
        if isinstance(data, (str, AnyUrl)):
            return {"uri": data, "name": str(data)}
        return data


class ErrorContent(Content):
    """Error information for JSON-RPC error responses."""
    type: Literal["error"] = "error"    # type: ignore
    code: int = Field(description="A number that indicates the error type that occurred.")
    message: str = Field(description="A short description of the error. The message SHOULD be limited to a concise single sentence.")
    data: Any | None = Field(default=None, description="Additional information about the error.")
    model_config = ConfigDict(extra="allow")


class BoolContents(Content):
    type: Literal["blob"] = "blob"  # type: ignore
    bool: bool
    description: Optional[str] | None = None

    @model_validator(mode='before')
    @classmethod
    def validate_or_convert(cls, data):
        # If a boolean is passed directly, convert it to a dict with 'bool' key
        if isinstance(data, bool):
            return {"bool": data}
        return data
