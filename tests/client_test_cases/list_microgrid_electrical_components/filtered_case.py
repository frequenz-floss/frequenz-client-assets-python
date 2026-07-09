# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Test data for filtered electrical component listing."""

from typing import Any

from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)
from frequenz.api.platformassets.v1alpha1 import platformassets_pb2 as assets_pb2
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.electrical_components import ElectricalComponentId

from frequenz.client.assets.electrical_component import (
    ElectricalComponentCategory,
    SteamBoiler,
)


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    request_type = assets_pb2.ListMicrogridElectricalComponentsRequest
    filter_type = request_type.MicrogridElectricalComponentsFilter
    stub_method.assert_called_once_with(
        request_type(
            microgrid_id=1234,
            filter=filter_type(
                component_ids=[1],
                categories=[
                    electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_STEAM_BOILER
                ],
            ),
        ),
        timeout=60.0,
    )


client_args = (1234,)
client_kwargs = {
    "component_ids": [ElectricalComponentId(1)],
    "categories": [ElectricalComponentCategory.STEAM_BOILER],
}
grpc_response = assets_pb2.ListMicrogridElectricalComponentsResponse(
    components=[
        electrical_components_pb2.ElectricalComponent(
            id=1,
            microgrid_id=1234,
            category=electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_STEAM_BOILER,
            name="Steam Boiler",
        )
    ]
)


def assert_client_result(result: Any) -> None:
    """Assert that the client result matches the expected component list."""
    assert list(result) == [
        SteamBoiler(
            id=ElectricalComponentId(1),
            microgrid_id=MicrogridId(1234),
            name="Steam Boiler",
            manufacturer=None,
            model_name=None,
        )
    ]
