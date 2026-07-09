# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Conversion of BalancingGroup objects from protobuf messages."""

from frequenz.api.common.v1alpha8.grid import balancing_group_pb2
from frequenz.client.common.proto import enum_from_proto

from ._balancing_group import BalancingGroup
from ._delivery_area import EnergyMarketCodeType


def balancing_group_from_proto(
    message: balancing_group_pb2.BalancingGroup,
) -> BalancingGroup:
    """Convert a protobuf balancing group message to a balancing group object."""
    return BalancingGroup(
        code=message.code or None,
        code_type=enum_from_proto(message.code_type, EnergyMarketCodeType),
    )
