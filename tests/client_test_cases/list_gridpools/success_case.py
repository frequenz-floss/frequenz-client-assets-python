# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Test data for successful gridpool listing."""

from typing import Any

from frequenz.api.common.v1alpha8.gridpool import gridpool_pb2
from frequenz.api.platformassets.v1alpha1 import platformassets_pb2 as assets_pb2

from frequenz.client.assets import Gridpool


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        assets_pb2.ListGridpoolsRequest(
            filter=assets_pb2.ListGridpoolsRequest.GridpoolsFilter(gridpool_ids=[7, 8])
        ),
        timeout=60.0,
    )


client_kwargs = {"gridpool_ids": [7, 8]}
grpc_response = assets_pb2.ListGridpoolsResponse(
    gridpools=[
        gridpool_pb2.Gridpool(id=7, name="North"),
        gridpool_pb2.Gridpool(id=8),
    ]
)


def assert_client_result(result: Any) -> None:
    """Assert that the client result matches the expected gridpool list."""
    assert result == [
        Gridpool(id=7, name="North"),
        Gridpool(id=8, name=None),
    ]
