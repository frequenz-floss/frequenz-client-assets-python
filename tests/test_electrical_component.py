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
@pytest.mark.parametrize(
    ("mode", "telemetry", "control"),
    [
        (0, None, None),
        (1, False, False),
        (2, True, False),
        (3, False, True),
        (4, True, True),
        (99, None, None),
    ],
)
def test_operational_mode_for_all_component_types(
    category: int,
    subcategory: int,
    mode: int,
    telemetry: bool | None,
    control: bool | None,
) -> None:
    """Initialize mode flags for known and unknown categories and types."""
    message = electrical_components_pb2.ElectricalComponent(
        id=1,
        microgrid_id=1234,
        category=electrical_components_pb2.ElectricalComponentCategory.ValueType(
            category
        ),
        operational_mode=electrical_components_pb2.ElectricalComponentOperationalMode.ValueType(
            mode
        ),
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

    if mode == 99:
        assert component.operational_mode == mode
    else:
        assert component.operational_mode is ElectricalComponentOperationalMode(mode)
    if telemetry is None:
        with pytest.raises(ValueError, match="telemetry availability is unknown"):
            component.provides_telemetry()
        with pytest.raises(ValueError, match="control availability is unknown"):
            component.accepts_control()
    else:
        assert component.provides_telemetry() is telemetry
        assert component.accepts_control() is control


@pytest.mark.parametrize(
    ("telemetry", "control"),
    [
        (False, False),
        (True, False),
        (False, True),
        (True, True),
    ],
)
def test_operational_mode_helpers(telemetry: bool, control: bool) -> None:
    """Return the stored telemetry and control flags."""
    component = SteamBoiler(
        id=ElectricalComponentId(1),
        microgrid_id=MicrogridId(1234),
        _provides_telemetry=telemetry,
        _accepts_control=control,
    )

    assert component.provides_telemetry() is telemetry
    assert component.accepts_control() is control


@pytest.mark.parametrize(
    ("telemetry", "control"), [(None, None), (True, None), (None, False)]
)
def test_operational_mode_helpers_with_unspecified_flags(
    telemetry: bool | None,
    control: bool | None,
) -> None:
    """Raise only when the requested flag is unspecified."""
    component = SteamBoiler(
        id=ElectricalComponentId(1),
        microgrid_id=MicrogridId(1234),
        _provides_telemetry=telemetry,
        _accepts_control=control,
    )

    if telemetry is None:
        with pytest.raises(ValueError, match="telemetry availability is unknown"):
            component.provides_telemetry()
    else:
        assert component.provides_telemetry() is telemetry
    if control is None:
        with pytest.raises(ValueError, match="control availability is unknown"):
            component.accepts_control()
    else:
        assert component.accepts_control() is control


def test_operational_mode_helpers_without_mode() -> None:
    """Reject components constructed without an operational mode."""
    component = SteamBoiler(id=ElectricalComponentId(1), microgrid_id=MicrogridId(1234))

    with pytest.raises(ValueError, match="telemetry availability is unknown"):
        component.provides_telemetry()
    with pytest.raises(ValueError, match="control availability is unknown"):
        component.accepts_control()
