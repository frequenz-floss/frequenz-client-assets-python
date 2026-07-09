# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Conversion of Interval objects to/from protobuf messages."""

from frequenz.api.common.v1alpha8.types import interval_pb2
from frequenz.client.base import conversion

from ._interval import Interval


def interval_from_proto(message: interval_pb2.Interval) -> Interval:
    """Convert a protobuf interval message to an interval object."""
    return Interval(
        start=(
            conversion.to_datetime(message.start_time)
            if message.HasField("start_time")
            else None
        ),
        end=(
            conversion.to_datetime(message.end_time)
            if message.HasField("end_time")
            else None
        ),
    )


def interval_to_proto(interval: Interval) -> interval_pb2.Interval:
    """Convert an interval object to a protobuf interval message."""
    message = interval_pb2.Interval()
    if interval.start is not None:
        message.start_time.CopyFrom(conversion.to_timestamp(interval.start))
    if interval.end is not None:
        message.end_time.CopyFrom(conversion.to_timestamp(interval.end))
    return message
