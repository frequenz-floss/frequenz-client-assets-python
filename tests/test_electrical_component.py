# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Tests for electrical component conversion."""

import pytest
from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)

from frequenz.client.assets.electrical_component import (
    ElectricalComponentOperationalMode,
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

    component = electrical_component_proto(message)

    assert component.operational_mode is ElectricalComponentOperationalMode.CONTROL_ONLY
