# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Custom exceptions for the Assets API client.

This module provides custom exception classes for handling various error scenarios
that can occur when interacting with the Assets API. All exceptions inherit from
AssetsApiError, which provides a consistent interface for error handling and
JSON serialization.

Example:
    ```python
    from frequenz.client.assets import AssetsApiClient

    client = AssetsApiClient(
        server_url="grpc://localhost:8080",
        auth_key="key",
        sign_secret="secret",
    )
    try:
        microgrid = await client.get_microgrid_details(123)
    except NotFoundError as e:
        print(f"Resource not found: {e.message}")
        error_data = e.to_dict()  # For JSON serialization
    except AuthenticationError as e:
        print(f"Authentication failed: {e.message}")
    ```
"""

from typing import Any, Optional


class AssetsApiError(Exception):
    """Base exception for Assets API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[str] = None,
        details: Optional[str] = None,
    ):
        """
        Initialize the AssetsApiError.

        Args:
            message: The primary error message that describes what went wrong.
            status_code: Optional status code string (e.g., "NOT_FOUND", "UNAUTHORIZED").
            details: Optional additional error details or context information.
        """
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert exception to dictionary for JSON serialization.

        This method creates a structured dictionary representation of the error
        that can be easily serialized to JSON for API responses or logging.

        Returns:
            A dictionary containing the error details with the following keys:
            - error: The status code or "API_ERROR" if not specified
            - message: The error message
            - details: Additional error details (if available)

        Example:
            ```python
            error = NotFoundError(123)
            error_dict = error.to_dict()
            # Returns: {"error": "NOT_FOUND", "message": "Resource with ID 123 was not found", ...}
            ```
        """
        return {
            "error": self.status_code or "API_ERROR",
            "message": self.message,
            "details": self.details,
        }


class NotFoundError(AssetsApiError):
    """Raised when a requested resource is not found."""

    def __init__(self, resource_id: int, message: Optional[str] = None):
        """
        Initialize the NotFoundError.

        Args:
            resource_id: The ID of the resource that was not found.
            message: Optional custom error message. If not provided, a default
                message will be generated using the resource_id.
        """
        self.resource_id = resource_id
        self.message = message or f"Resource with ID {resource_id} was not found"
        super().__init__(self.message, "NOT_FOUND")

    def to_dict(self) -> dict[str, Any]:
        """
        Convert exception to dictionary for JSON serialization.

        Extends the base to_dict method to include the resource_id field
        for better error context.

        Returns:
            A dictionary containing the error details plus the resource_id.
        """
        base_dict = super().to_dict()
        base_dict["resource_id"] = self.resource_id
        return base_dict


class AuthenticationError(AssetsApiError):
    """Raised when authentication to the Assets API fails."""

    def __init__(self, message: Optional[str] = None):
        """Initialize the AuthenticationError.

        Args:
            message: Optional custom error message. If None, defaults to "Authentication failed".
        """
        super().__init__(message or "Authentication failed", "AUTHENTICATION_FAILED")


class ServiceUnavailableError(AssetsApiError):
    """Raised when the Assets API service is temporarily unavailable."""

    def __init__(self, message: Optional[str] = None):
        """
        Initialize the ServiceUnavailableError.

        Args:
            message: Optional custom error message. If None, defaults to "Service unavailable".
        """
        super().__init__(message or "Service unavailable", "SERVICE_UNAVAILABLE")
