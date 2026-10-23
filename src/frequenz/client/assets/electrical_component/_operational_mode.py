# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Electrical component operational modes."""

import enum

from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)


@enum.unique
class ElectricalComponentOperationalMode(enum.Enum):
    """The known operational modes of an electrical component."""

    UNSPECIFIED = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_OPERATIONAL_MODE_UNSPECIFIED
    )
    """The operational mode is not set or is not available."""

    INACTIVE = electrical_components_pb2.ELECTRICAL_COMPONENT_OPERATIONAL_MODE_INACTIVE
    """The component provides no telemetry and accepts no control commands."""

    TELEMETRY_ONLY = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_OPERATIONAL_MODE_TELEMETRY_ONLY
    )
    """The component provides telemetry and accepts no control commands."""

    CONTROL_ONLY = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_OPERATIONAL_MODE_CONTROL_ONLY
    )
    """The component accepts control commands and provides no telemetry."""

    CONTROL_AND_TELEMETRY = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_OPERATIONAL_MODE_CONTROL_AND_TELEMETRY
    )
    """The component provides telemetry and accepts control commands."""
