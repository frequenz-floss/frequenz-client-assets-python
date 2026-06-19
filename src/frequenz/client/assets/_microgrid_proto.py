# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Loading of MicrogridInfo objects from protobuf messages."""

import logging

from frequenz.api.common.v1alpha8.microgrid import microgrid_pb2
from frequenz.client.base import conversion
from frequenz.client.common.microgrid import EnterpriseId, MicrogridId
from frequenz.client.common.proto import enum_from_proto

from ._delivery_area import DeliveryArea
from ._delivery_area_proto import delivery_area_from_proto
from ._location import Location
from ._location_proto import location_from_proto
from ._microgrid import Microgrid, MicrogridStatus

_logger = logging.getLogger(__name__)


def microgrid_from_proto(message: microgrid_pb2.Microgrid) -> Microgrid:
    """Convert a protobuf microgrid message to a microgrid object.

    Args:
        message: The protobuf message to convert.

    Returns:
        The resulting microgrid object.
    """
    major_issues: list[str] = []
    minor_issues: list[str] = []

    microgrid = microgrid_from_proto_with_issues(
        message, major_issues=major_issues, minor_issues=minor_issues
    )

    if major_issues:
        _logger.warning(
            "Found issues in microgrid: %s | Protobuf message:\n%s",
            ", ".join(major_issues),
            message,
        )

    if minor_issues:
        _logger.debug(
            "Found minor issues in microgrid: %s | Protobuf message:\n%s",
            ", ".join(minor_issues),
            message,
        )

    return microgrid


def microgrid_from_proto_with_issues(
    message: microgrid_pb2.Microgrid,
    *,
    major_issues: list[str],
    minor_issues: list[str],
) -> Microgrid:
    """Convert a protobuf microgrid message to a microgrid object, collecting issues.

    This function is useful when you want to collect issues during parsing
    rather than logging them immediately.

    Args:
        message: The protobuf message to convert.
        major_issues: A list to collect major issues found during validation.
        minor_issues: A list to collect minor issues found during validation.

    Returns:
        The resulting microgrid object.
    """
    delivery_area: DeliveryArea | None = None
    if message.HasField("delivery_area"):
        delivery_area = delivery_area_from_proto(message.delivery_area)
    else:
        major_issues.append("delivery_area is missing")

    location: Location | None = None
    if message.HasField("location"):
        location = location_from_proto(message.location)
    else:
        major_issues.append("location is missing")

    name = message.name or None
    if name is None:
        minor_issues.append("name is empty")

    status = enum_from_proto(message.status, MicrogridStatus)
    if status is MicrogridStatus.UNSPECIFIED:
        major_issues.append("status is unspecified")
    elif isinstance(status, int):
        major_issues.append("status is unrecognized")

    return Microgrid(
        id=MicrogridId(message.id),
        enterprise_id=EnterpriseId(message.enterprise_id),
        name=message.name or None,
        delivery_area=delivery_area,
        location=location,
        status=status,
        create_timestamp=conversion.to_datetime(message.create_timestamp),
    )
