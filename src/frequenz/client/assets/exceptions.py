# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Exceptions raised by the assets API client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from frequenz.client.base.exception import (
    ApiClientError,
    ClientNotConnected,
    DataLoss,
    EntityAlreadyExists,
    EntityNotFound,
    GrpcError,
    InternalError,
    InvalidArgument,
    OperationAborted,
    OperationCancelled,
    OperationNotImplemented,
    OperationOutOfRange,
    OperationPreconditionFailed,
    OperationTimedOut,
    OperationUnauthenticated,
    PermissionDenied,
    ResourceExhausted,
    ServiceUnavailable,
    UnknownError,
    UnrecognizedGrpcStatus,
)

if TYPE_CHECKING:
    from ._microgrid import Microgrid
    from .electrical_component._connection import ComponentConnection
    from .electrical_component._electrical_component import ElectricalComponent

__all__ = [
    "ApiClientError",
    "ClientNotConnected",
    "DataLoss",
    "EntityAlreadyExists",
    "EntityNotFound",
    "GrpcError",
    "InternalError",
    "InvalidArgument",
    "InvalidConnectionError",
    "InvalidElectricalComponentError",
    "InvalidMicrogridError",
    "OperationAborted",
    "OperationCancelled",
    "OperationNotImplemented",
    "OperationOutOfRange",
    "OperationPreconditionFailed",
    "OperationTimedOut",
    "OperationUnauthenticated",
    "PermissionDenied",
    "ResourceExhausted",
    "ServiceUnavailable",
    "UnknownError",
    "UnrecognizedGrpcStatus",
    "ValidationError",
]


class ValidationError(Exception):
    """Base error for protobuf message validation failures.

    This exception is raised when ``raise_on_errors=True`` is passed to
    client methods and validation issues are detected in the protobuf message.
    """

    major_issues: list[str]
    """List of major issues found during validation."""

    minor_issues: list[str]
    """List of minor issues found during validation."""

    raw_message: Any
    """The original protobuf message that was being validated."""

    def __init__(
        self,
        *,
        major_issues: list[str],
        minor_issues: list[str],
        raw_message: Any,
    ) -> None:
        """Create a new ValidationError.

        Args:
            major_issues: List of major issues found during validation.
            minor_issues: List of minor issues found during validation.
            raw_message: The protobuf message that failed validation.
        """
        issues_summary = ", ".join(major_issues)
        message = (
            f"Validation failed: {issues_summary}"
            if issues_summary
            else "Validation failed"
        )
        super().__init__(message)
        self.major_issues = major_issues
        self.minor_issues = minor_issues
        self.raw_message = raw_message


class InvalidMicrogridError(ValidationError):
    """Raised when a microgrid message has validation issues."""

    microgrid: Microgrid
    """The partially validated microgrid object."""

    def __init__(
        self,
        *,
        microgrid: Microgrid,
        major_issues: list[str],
        minor_issues: list[str],
        raw_message: Any,
    ) -> None:
        """Create a new InvalidMicrogridError.

        Args:
            microgrid: The partially validated microgrid object.
            major_issues: List of major issues found during validation.
            minor_issues: List of minor issues found during validation.
            raw_message: The protobuf message that failed validation.
        """
        super().__init__(
            major_issues=major_issues,
            minor_issues=minor_issues,
            raw_message=raw_message,
        )
        self.microgrid = microgrid


class InvalidElectricalComponentError(ValidationError):
    """Raised when a single electrical component has validation issues."""

    component: ElectricalComponent
    """The partially validated electrical component."""

    def __init__(
        self,
        *,
        component: ElectricalComponent,
        major_issues: list[str],
        minor_issues: list[str],
        raw_message: Any,
    ) -> None:
        """Create a new InvalidElectricalComponentError.

        Args:
            component: The partially validated electrical component.
            major_issues: List of major issues found during validation.
            minor_issues: List of minor issues found during validation.
            raw_message: The protobuf message that failed validation.
        """
        super().__init__(
            major_issues=major_issues,
            minor_issues=minor_issues,
            raw_message=raw_message,
        )
        self.component = component


class InvalidConnectionError(ValidationError):
    """Raised when a single connection has validation issues."""

    connection: ComponentConnection | None
    """The partially validated connection, or None if completely invalid."""

    def __init__(
        self,
        *,
        connection: ComponentConnection | None,
        major_issues: list[str],
        minor_issues: list[str],
        raw_message: Any,
    ) -> None:
        """Create a new InvalidConnectionError.

        Args:
            connection: The partially validated connection, or None.
            major_issues: List of major issues found during validation.
            minor_issues: List of minor issues found during validation.
            raw_message: The protobuf message that failed validation.
        """
        super().__init__(
            major_issues=major_issues,
            minor_issues=minor_issues,
            raw_message=raw_message,
        )
        self.connection = connection
