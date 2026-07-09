# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Conversion of MarketTopologyRelation objects from protobuf messages."""

from frequenz.api.platformassets.v1alpha1 import platformassets_pb2
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.proto import enum_from_proto

from ._delivery_area_proto import delivery_area_from_proto
from ._interval_proto import interval_from_proto
from ._market_location_proto import market_location_from_proto
from ._market_topology import (
    MarketParticipation,
    MarketParticipationType,
    MarketTopologyRelation,
)


def market_participation_from_proto(
    message: platformassets_pb2.MarketParticipation,
) -> MarketParticipation:
    """Convert a protobuf market participation message to a domain object."""
    return MarketParticipation(
        type=enum_from_proto(message.type, MarketParticipationType),
        validity_period=(
            interval_from_proto(message.validity_period)
            if message.HasField("validity_period")
            else None
        ),
    )


def market_topology_relation_from_proto(
    message: platformassets_pb2.MarketTopologyRelation,
) -> MarketTopologyRelation:
    """Convert a protobuf market topology relation message to a domain object."""
    return MarketTopologyRelation(
        microgrid_id=(
            MicrogridId(message.microgrid_id)
            if message.HasField("microgrid_id")
            else None
        ),
        market_location=(
            market_location_from_proto(message.market_location)
            if message.HasField("market_location")
            else None
        ),
        gridpool_id=message.gridpool_id if message.HasField("gridpool_id") else None,
        delivery_area=(
            delivery_area_from_proto(message.delivery_area)
            if message.HasField("delivery_area")
            else None
        ),
        participations=[
            market_participation_from_proto(participation)
            for participation in message.participations
        ],
    )
