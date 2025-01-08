"""
Pytest tests for simpletool.errors module.
"""
import pytest
from simpletool.errors import SimpleToolError, ValidationError


def test_simple_tool_error():
    """Test SimpleToolError initialization and attributes."""
    error = SimpleToolError(
        message="Test error", 
        code=501, 
        details={"context": "test"}
    )
    
    assert str(error) == "Test error"
    assert error.message == "Test error"
    assert error.code == 501
    assert error.details == {"context": "test"}


def test_simple_tool_error_default_values():
    """Test SimpleToolError with default values."""
    error = SimpleToolError("Default error")
    
    assert str(error) == "Default error"
    assert error.message == "Default error"
    assert error.code == 500
    assert error.details == {}


def test_validation_error():
    """Test ValidationError initialization."""
    error = ValidationError(field="test_field", reason="Invalid input")
    
    assert str(error) == "Validation failed for field 'test_field': Invalid input"
    assert error.message == "Validation failed for field 'test_field': Invalid input"
    assert error.code == 400
    assert error.details == {
        "field": "test_field",
        "reason": "Invalid input"
    }
