# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Microgrid sensor definitions."""

from dataclasses import dataclass

from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.sensors import SensorId

from ._lifetime import Lifetime


@dataclass(frozen=True, kw_only=True)
class Sensor:
    """A sensor that measures a physical metric in a microgrid environment."""

    id: SensorId
    """The unique identifier of the sensor."""

    microgrid_id: MicrogridId
    """The unique identifier of the parent microgrid."""

    name: str | None
    """The human-readable sensor name."""

    model: str | None
    """The sensor model name."""

    operational_lifetime: Lifetime | None
    """The operational lifetime of the sensor."""
