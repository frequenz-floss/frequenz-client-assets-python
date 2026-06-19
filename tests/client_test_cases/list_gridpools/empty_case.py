# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Empty case for gridpool listing."""

from typing import Any

from frequenz.api.platformassets.v1alpha1 import platformassets_pb2 as assets_pb2


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        assets_pb2.ListGridpoolsRequest(),
        timeout=60.0,
    )


grpc_response = assets_pb2.ListGridpoolsResponse(gridpools=[])


def assert_client_result(result: Any) -> None:  # noqa: D103
    assert not result
