# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test list_connections with no connections: result should be empty."""

from typing import Any

from frequenz.api.assets.v1 import assets_pb2

# No client_args or client_kwargs needed for this call


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        assets_pb2.ListMicrogridElectricalComponentConnectionsRequest(
            microgrid_id=1234, source_component_ids=[], destination_component_ids=[]
        ),
        timeout=60.0,
    )


client_args = (1234,)
grpc_response = assets_pb2.ListMicrogridElectricalComponentConnectionsResponse(
    connections=[]
)


def assert_client_result(result: Any) -> None:  # noqa: D103
    """Assert that the client result is an empty list."""
    assert not list(result)
