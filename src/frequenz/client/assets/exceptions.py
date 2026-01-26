# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Exceptions raised by the assets API client."""

from typing import Any

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

__all__ = [
    "ApiClientError",
    "ClientNotConnected",
    "DataLoss",
    "EntityAlreadyExists",
    "EntityNotFound",
    "GrpcError",
    "InternalError",
    "InvalidArgument",
    "OperationAborted",
    "OperationCancelled",
    "OperationNotImplemented",
    "OperationOutOfRange",
    "OperationPreconditionFailed",
    "OperationTimedOut",
    "OperationUnauthenticated",
    "ParsingError",
    "PermissionDenied",
    "ResourceExhausted",
    "ServiceUnavailable",
    "UnknownError",
    "UnrecognizedGrpcStatus",
]


class ParsingError(Exception):
    """Error raised when parsing protobuf messages fails with major issues.

    This exception is raised when `raise_on_errors=True` is passed to parsing
    functions and major issues are detected in the protobuf message.
    """

    major_issues: list[str]
    """List of major issues that indicate serious data problems."""

    minor_issues: list[str]
    """List of minor/informational issues."""

    raw_message: Any
    """The original protobuf message that was being parsed."""

    def __init__(
        self,
        *,
        major_issues: list[str],
        minor_issues: list[str],
        raw_message: Any,
    ) -> None:
        """Create a new ParsingError.

        Args:
            major_issues: List of major issues found during parsing.
            minor_issues: List of minor issues found during parsing.
            raw_message: The protobuf message that failed parsing.
        """
        issues_summary = ", ".join(major_issues)
        super().__init__(f"Parsing failed with major issues: {issues_summary}")
        self.major_issues = major_issues
        self.minor_issues = minor_issues
        self.raw_message = raw_message
