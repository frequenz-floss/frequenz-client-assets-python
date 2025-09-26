# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test data for successful microgrid retrieval."""

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock

from frequenz.api.assets.v1 import assets_pb2
from frequenz.api.common.v1alpha8.microgrid import microgrid_pb2
from frequenz.client.common.microgrid import EnterpriseId, MicrogridId

from frequenz.client.assets import Microgrid, MicrogridStatus


def assert_stub_method_call(stub_method: AsyncMock) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        assets_pb2.GetMicrogridRequest(microgrid_id=1), timeout=60.0
    )


client_args = (1,)
create_timestamp = datetime(2023, 1, 1, tzinfo=timezone.utc)
grpc_response = assets_pb2.GetMicrogridResponse(microgrid=microgrid_pb2.Microgrid())


def assert_client_result(result: Any) -> None:
    """Assert that the client result matches the expected Microgrid."""
    assert result == Microgrid(
        id=MicrogridId(0),
        enterprise_id=EnterpriseId(0),
        name=None,
        status=MicrogridStatus.UNSPECIFIED,
        location=None,
        delivery_area=None,
        create_timestamp=datetime(1970, 1, 1, 0, 0, tzinfo=timezone.utc),
    )
    assert result.is_active
