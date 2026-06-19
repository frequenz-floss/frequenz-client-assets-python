# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Conversion of Sensor objects from protobuf messages."""

from frequenz.api.common.v1alpha8.microgrid.sensors import sensors_pb2
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.sensors import SensorId

from ._lifetime_proto import lifetime_from_proto
from ._sensor import Sensor


def sensor_from_proto(message: sensors_pb2.Sensor) -> Sensor:
    """Convert a protobuf sensor message to a sensor object."""
    return Sensor(
        id=SensorId(message.id),
        microgrid_id=MicrogridId(message.microgrid_id),
        name=message.name or None,
        model=message.model or None,
        operational_lifetime=(
            lifetime_from_proto(message.operational_lifetime)
            if message.HasField("operational_lifetime")
            else None
        ),
    )
