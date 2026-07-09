# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Conversion of Gridpool objects from protobuf messages."""

from frequenz.api.common.v1alpha8.gridpool import gridpool_pb2

from ._gridpool import Gridpool


def gridpool_from_proto(message: gridpool_pb2.Gridpool) -> Gridpool:
    """Convert a protobuf gridpool message to a gridpool object."""
    return Gridpool(id=message.id, name=message.name or None)
