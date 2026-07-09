# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Test data for filtered connection listing."""

from typing import Any

from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)
from frequenz.api.platformassets.v1alpha1 import platformassets_pb2 as assets_pb2
from frequenz.client.common.microgrid.electrical_components import ElectricalComponentId

from frequenz.client.assets.electrical_component import ComponentConnection


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    request_type = assets_pb2.ListMicrogridElectricalComponentConnectionsRequest
    filter_type = request_type.MicrogridElectricalComponentConnectionsFilter
    stub_method.assert_called_once_with(
        request_type(
            microgrid_id=1234,
            filter=filter_type(
                source_component_ids=[1],
                destination_component_ids=[2],
            ),
        ),
        timeout=60.0,
    )


client_args = (1234,)
client_kwargs = {
    "source_component_ids": [ElectricalComponentId(1)],
    "destination_component_ids": [ElectricalComponentId(2)],
}
grpc_response = assets_pb2.ListMicrogridElectricalComponentConnectionsResponse(
    connections=[
        electrical_components_pb2.ElectricalComponentConnection(
            source_electrical_component_id=1,
            destination_electrical_component_id=2,
        )
    ]
)


def assert_client_result(result: Any) -> None:
    """Assert that the client result matches the expected connections list."""
    assert list(result) == [
        ComponentConnection(
            source=ElectricalComponentId(1),
            destination=ElectricalComponentId(2),
        )
    ]
