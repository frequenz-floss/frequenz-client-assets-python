# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Test data for successful sensor listing."""

from datetime import datetime, timezone
from typing import Any

from frequenz.api.common.v1alpha8.microgrid import lifetime_pb2
from frequenz.api.common.v1alpha8.microgrid.sensors import sensors_pb2
from frequenz.api.platformassets.v1alpha1 import platformassets_pb2 as assets_pb2
from frequenz.client.base.conversion import to_timestamp
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.sensors import SensorId

from frequenz.client.assets import Lifetime, Sensor


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        assets_pb2.ListMicrogridSensorsRequest(
            microgrid_id=1234,
            filter=assets_pb2.ListMicrogridSensorsRequest.MicrogridSensorsFilter(
                sensor_ids=[5]
            ),
        ),
        timeout=60.0,
    )


lifetime_start = datetime(2024, 1, 1, tzinfo=timezone.utc)
client_args = (MicrogridId(1234),)
client_kwargs = {"sensor_ids": [SensorId(5)]}
grpc_response = assets_pb2.ListMicrogridSensorsResponse(
    microgrid_id=1234,
    sensors=[
        sensors_pb2.Sensor(
            id=5,
            microgrid_id=1234,
            name="Weather station",
            model="Vaisala WXT",
            operational_lifetime=lifetime_pb2.Lifetime(
                start_timestamp=to_timestamp(lifetime_start)
            ),
        )
    ],
)


def assert_client_result(result: Any) -> None:
    """Assert that the client result matches the expected sensor list."""
    assert result == [
        Sensor(
            id=SensorId(5),
            microgrid_id=MicrogridId(1234),
            name="Weather station",
            model="Vaisala WXT",
            operational_lifetime=Lifetime(start=lifetime_start),
        )
    ]
