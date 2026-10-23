# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Tests for electrical components and protobuf conversion."""

import pytest
from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.electrical_components import ElectricalComponentId

from frequenz.client.assets.electrical_component import (
    ElectricalComponentOperationalMode,
    SteamBoiler,
)
from frequenz.client.assets.electrical_component._electrical_component_proto import (
    electrical_component_proto,
)


@pytest.mark.parametrize(
    "category", [*electrical_components_pb2.ElectricalComponentCategory.values(), 99]
)
@pytest.mark.parametrize("subcategory", [0, 99])
def test_operational_mode_for_all_component_types(
    category: int, subcategory: int
) -> None:
    """Preserve the mode for known and unknown component categories and types."""
    mode = electrical_components_pb2.ELECTRICAL_COMPONENT_OPERATIONAL_MODE_CONTROL_ONLY
    message = electrical_components_pb2.ElectricalComponent(
        id=1,
        microgrid_id=1234,
        category=electrical_components_pb2.ElectricalComponentCategory.ValueType(
            category
        ),
        operational_mode=mode,
    )
    match category:
        case electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_BATTERY:
            message.category_specific_info.battery.type = (
                electrical_components_pb2.BatteryType.ValueType(subcategory)
            )
        case electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_EV_CHARGER:
            message.category_specific_info.ev_charger.type = (
                electrical_components_pb2.EvChargerType.ValueType(subcategory)
            )
        case electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_INVERTER:
            message.category_specific_info.inverter.type = (
                electrical_components_pb2.InverterType.ValueType(subcategory)
            )
        case _:
            pass

    component = electrical_component_proto(message)

    assert component.operational_mode is ElectricalComponentOperationalMode.CONTROL_ONLY
    assert component.provides_telemetry() is False
    assert component.accepts_control() is True


@pytest.mark.parametrize(
    ("mode", "telemetry", "control"),
    [
        (ElectricalComponentOperationalMode.INACTIVE, False, False),
        (ElectricalComponentOperationalMode.TELEMETRY_ONLY, True, False),
        (ElectricalComponentOperationalMode.CONTROL_ONLY, False, True),
        (ElectricalComponentOperationalMode.CONTROL_AND_TELEMETRY, True, True),
    ],
)
def test_operational_mode_helpers(
    mode: ElectricalComponentOperationalMode, telemetry: bool, control: bool
) -> None:
    """Derive telemetry and control flags from each known requested mode."""
    component = SteamBoiler(
        id=ElectricalComponentId(1),
        microgrid_id=MicrogridId(1234),
        operational_mode=mode,
    )

    assert component.provides_telemetry() is telemetry
    assert component.accepts_control() is control


@pytest.mark.parametrize("mode", [ElectricalComponentOperationalMode.UNSPECIFIED, 99])
def test_operational_mode_helpers_raise_for_unknown_mode(
    mode: ElectricalComponentOperationalMode | int,
) -> None:
    """Reject unspecified and unrecognized operational modes."""
    component = SteamBoiler(
        id=ElectricalComponentId(1),
        microgrid_id=MicrogridId(1234),
        operational_mode=mode,
    )

    with pytest.raises(ValueError, match="Telemetry"):
        component.provides_telemetry()
    with pytest.raises(ValueError, match="Control"):
        component.accepts_control()


def test_operational_mode_helpers_without_mode() -> None:
    """Reject components constructed without an operational mode."""
    component = SteamBoiler(id=ElectricalComponentId(1), microgrid_id=MicrogridId(1234))

    with pytest.raises(ValueError, match="Telemetry"):
        component.provides_telemetry()
    with pytest.raises(ValueError, match="Control"):
        component.accepts_control()
