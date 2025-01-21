""" Type definitions for the simpletool package."""
from typing import Literal, Any, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic.networks import AnyUrl
import base64

__all__ = [
    'Content',
    'TextContent',
    'ImageContent',
    'FileContent',
    'ResourceContent',
    'BoolContent',
    'ErrorContent'
]


# -------------------------------------------------------------------------------------------------
# --- CONTENT CLASSES -----------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------


class Content(BaseModel):
    """Base class for content types."""
    type: Literal["text", "image", "resource", "file", "error", "video", "audio", "bool"]
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    @model_validator(mode='before')
    @classmethod
    def convert_field_names(cls, data: dict) -> dict:
        if not isinstance(data, dict):
            return data

        field_mappings = {
            'mimeType': 'mime_type',
            'fileName': 'file_name'
        }

        return {field_mappings.get(k, k): v for k, v in data.items()}


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
    image: str
    mime_type: str | None = None
    description: Optional[str] | None = None

    @model_validator(mode='before')
    @classmethod
    def validate_or_convert(cls, image):
        # If a string is passed directly, assume it's base64 data
        if isinstance(image, str):
            # Validate base64 encoding
            try:
                base64.b64decode(image, validate=True)
                return {"image": image}
            except Exception as e:
                raise ValueError("Image must be a valid base64 encoded string") from e
        return image

    @field_validator('image')
    @classmethod
    def validate_base64(cls, value):
        try:
            base64.b64decode(value, validate=True)
            return value
        except Exception as e:
            raise ValueError("Image must be a valid base64 encoded string") from e


class FileContent(Content):
    type: Literal["file"] = "file"    # type: ignore
    file: str
    mime_type: str | None = None
    file_name: Optional[str] | None = None
    description: Optional[str] | None = None

    @model_validator(mode='before')
    @classmethod
    def validate_or_convert(cls, file):
        # If a string is passed directly, assume it's base64 data
        if isinstance(file, str):
            # Validate base64 encoding
            try:
                base64.b64decode(file, validate=True)
                return {"file": file}
            except Exception as e:
                raise ValueError("File must be a valid base64 encoded string") from e
        return file

    @field_validator('file')
    @classmethod
    def validate_base64(cls, value):
        try:
            base64.b64decode(value, validate=True)
            return value
        except Exception as e:
            raise ValueError("File must be a valid base64 encoded string") from e


class ResourceContent(Content):
    type: Literal["resource"] = "resource"  # type: ignore
    uri: Union[str, AnyUrl]
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

    @field_validator('uri')
    @classmethod
    def validate_uri(cls, v: str) -> str:
        """Ensure URI is accessible and returns valid status"""
        # Add URI validation logic here
        return v


class ErrorContent(Content):
    """Error information for JSON-RPC error responses."""
    type: Literal["error"] = "error"    # type: ignore
    code: int = Field(description="A number that indicates the error type that occurred.")
    error: str = Field(description="A short description of the error. The message SHOULD be limited to a concise single sentence.")
    data: Any | None = Field(default=None, description="Additional information about the error.")
    model_config = ConfigDict(extra="allow")


class BoolContent(Content):
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
