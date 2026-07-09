# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Conversion of MarketLocation objects to/from protobuf messages."""

from frequenz.api.common.v1alpha8.grid import market_location_pb2
from frequenz.client.common.proto import enum_from_proto

from ._market_location import MarketLocation, MarketLocationId, MarketLocationIdType


def market_location_id_from_proto(
    message: market_location_pb2.MarketLocationId,
) -> MarketLocationId:
    """Convert a protobuf market location ID message to a domain object."""
    return MarketLocationId(
        value=message.id.value if message.HasField("id") else None,
        type=enum_from_proto(message.type, MarketLocationIdType),
    )


def market_location_from_proto(
    message: market_location_pb2.MarketLocation,
) -> MarketLocation:
    """Convert a protobuf market location message to a domain object."""
    return MarketLocation(
        market_area=message.market_area,
        market_location_id=(
            market_location_id_from_proto(message.market_location_id)
            if message.HasField("market_location_id")
            else None
        ),
    )


def market_location_id_value_to_proto(
    value: str,
) -> market_location_pb2.MarketLocationIdValue:
    """Convert a market location ID value string to a protobuf message."""
    return market_location_pb2.MarketLocationIdValue(value=value)
