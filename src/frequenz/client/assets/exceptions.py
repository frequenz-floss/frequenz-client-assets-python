# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Exceptions raised by the assets API client."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Self

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
    "InvalidConnectionErrorGroup",
    "InvalidElectricalComponentError",
    "InvalidElectricalComponentErrorGroup",
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
    "ValidationErrorGroup",
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
        super().__init__(f"Validation failed: {issues_summary}")
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


class ValidationErrorGroup(ValidationError, ExceptionGroup[ValidationError]):
    """Base group of validation errors.

    Inherits from both
    [ValidationError][frequenz.client.assets.exceptions.ValidationError]
    and `ExceptionGroup`, so all validation error groups can be caught with
    ``except ValidationError``.
    """

    def __new__(
        cls,
        message: str,
        exceptions: Sequence[ValidationError],
    ) -> Self:
        """Create a new ValidationErrorGroup.

        Args:
            message: The error message.
            exceptions: The validation errors in this group.

        Returns:
            The new exception group.
        """
        instance = super().__new__(cls, message, exceptions)
        instance.major_issues = []
        instance.minor_issues = []
        instance.raw_message = None
        return instance

    def derive(  # type: ignore[override]
        self, excs: Sequence[ValidationError]
    ) -> ValidationErrorGroup:
        """Derive a new group from a subset of exceptions.

        Args:
            excs: The subset of exceptions for the derived group.

        Returns:
            A new exception group.
        """
        return ValidationErrorGroup(self.message, excs)


class InvalidElectricalComponentErrorGroup(
    ValidationErrorGroup,
):
    """Raised when multiple electrical components have validation issues."""

    valid_components: list[ElectricalComponent]
    """The components that were successfully validated."""

    def __new__(
        cls,
        *,
        valid_components: list[ElectricalComponent],
        exceptions: Sequence[InvalidElectricalComponentError],
    ) -> InvalidElectricalComponentErrorGroup:
        """Create a new InvalidElectricalComponentErrorGroup.

        Args:
            valid_components: The components that passed validation.
            exceptions: The validation errors for components that failed.

        Returns:
            The new exception group.
        """
        instance = super().__new__(
            cls,
            f"{len(exceptions)} electrical component(s) failed validation",
            exceptions,
        )
        instance.valid_components = valid_components
        return instance

    def derive(  # type: ignore[override]
        self, excs: Sequence[InvalidElectricalComponentError]
    ) -> InvalidElectricalComponentErrorGroup:
        """Derive a new group from a subset of exceptions.

        Args:
            excs: The subset of exceptions for the derived group.

        Returns:
            A new exception group with the same valid components.
        """
        return InvalidElectricalComponentErrorGroup(
            valid_components=self.valid_components,
            exceptions=excs,
        )


class InvalidConnectionErrorGroup(ValidationErrorGroup):
    """Raised when multiple connections have validation issues."""

    valid_connections: list[ComponentConnection]
    """The connections that were successfully validated."""

    def __new__(
        cls,
        *,
        valid_connections: list[ComponentConnection],
        exceptions: Sequence[InvalidConnectionError],
    ) -> InvalidConnectionErrorGroup:
        """Create a new InvalidConnectionErrorGroup.

        Args:
            valid_connections: The connections that passed validation.
            exceptions: The validation errors for connections that failed.

        Returns:
            The new exception group.
        """
        instance = super().__new__(
            cls,
            f"{len(exceptions)} connection(s) failed validation",
            exceptions,
        )
        instance.valid_connections = valid_connections
        return instance

    def derive(  # type: ignore[override]
        self, excs: Sequence[InvalidConnectionError]
    ) -> InvalidConnectionErrorGroup:
        """Derive a new group from a subset of exceptions.

        Args:
            excs: The subset of exceptions for the derived group.

        Returns:
            A new exception group with the same valid connections.
        """
        return InvalidConnectionErrorGroup(
            valid_connections=self.valid_connections,
            exceptions=excs,
        )
