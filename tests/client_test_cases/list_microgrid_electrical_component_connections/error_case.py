# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test list_electrical_components with error."""

from typing import Any

from frequenz.api.platformassets.v1alpha1 import platformassets_pb2 as assets_pb2
from grpc import StatusCode

from frequenz.client.assets.exceptions import PermissionDenied
from tests.util import make_grpc_error


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        assets_pb2.ListMicrogridElectricalComponentConnectionsRequest(
            microgrid_id=1234
        ),
        timeout=60.0,
    )


client_args = (1234,)
grpc_response = make_grpc_error(StatusCode.PERMISSION_DENIED)


def assert_client_exception(exception: Exception) -> None:
    """Assert that the client exception matches the expected error."""
    assert isinstance(exception, PermissionDenied)
    assert exception.grpc_error == grpc_response
