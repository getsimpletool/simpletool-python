"""
Pytest tests for simpletool.errors module.
"""
import pytest
from simpletool.errors import SimpleToolError, ValidationError


@pytest.mark.parametrize("error_class,input_data,expected", [
    (
        SimpleToolError,
        {"message": "Test error", "code": 501, "details": {"context": "test"}},
        {"str": "Test error", "code": 501, "details": {"context": "test"}}
    ),
    (
        SimpleToolError,
        {"message": "Default error"},
        {"str": "Default error", "code": 500, "details": {}}
    ),
])
def test_error_initialization(error_class, input_data, expected):
    """Test error class initialization with various inputs."""
    error = error_class(**input_data)

    assert str(error) == expected["str"]
    assert error.message == expected["str"]
    assert error.code == expected["code"]
    assert error.details == expected["details"]


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
