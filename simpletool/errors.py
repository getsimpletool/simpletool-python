"""
Custom error classes for SimpleTool framework.
"""


class SimpleToolError(Exception):
    """
    Base exception for SimpleTool framework.

    Provides a standardized way to handle tool-related errors.
    """

    def __init__(self, message: str, code: int = 500, details: dict | None = None):
        """
        Initialize a SimpleToolError.

        Args:
            message (str): A human-readable error description
            code (int, optional): Error code. Defaults to 500 (Internal Server Error)
            details (dict, optional): Additional error details
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class ValidationError(SimpleToolError):
    """
    Raised when input validation fails.
    """

    def __init__(self, field: str, reason: str):
        """
        Initialize a ValidationError.

        Args:
            field (str): The field that failed validation
            reason (str): Reason for validation failure
        """
        super().__init__(
            f"Validation failed for field '{field}': {reason}",
            code=400,  # Bad Request
            details={
                "field": field,
                "reason": reason
            }
        )
