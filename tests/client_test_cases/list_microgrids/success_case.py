# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Test data for successful microgrid listing."""

from datetime import datetime, timezone
from typing import Any

import pytest
from frequenz.api.common.v1alpha8.grid import delivery_area_pb2
from frequenz.api.common.v1alpha8.microgrid import microgrid_pb2
from frequenz.api.common.v1alpha8.types import location_pb2
from frequenz.api.platformassets.v1alpha1 import platformassets_pb2 as assets_pb2
from frequenz.client.base.conversion import to_timestamp
from frequenz.client.common.microgrid import EnterpriseId, MicrogridId

from frequenz.client.assets import (
    DeliveryArea,
    EnergyMarketCodeType,
    Location,
    Microgrid,
    MicrogridStatus,
)


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        assets_pb2.ListMicrogridsRequest(
            filter=assets_pb2.ListMicrogridsRequest.MicrogridsFilter(
                microgrid_ids=[1234], gridpool_ids=[7]
            )
        ),
        timeout=60.0,
    )


create_timestamp = datetime(2023, 1, 1, tzinfo=timezone.utc)
client_kwargs = {"microgrid_ids": [MicrogridId(1234)], "gridpool_ids": [7]}
grpc_response = assets_pb2.ListMicrogridsResponse(
    microgrids=[
        microgrid_pb2.Microgrid(
            id=1234,
            enterprise_id=5678,
            name="Test Microgrid",
            delivery_area=delivery_area_pb2.DeliveryArea(
                code="Test Delivery Area",
                code_type=delivery_area_pb2.ENERGY_MARKET_CODE_TYPE_EUROPE_EIC,
            ),
            location=location_pb2.Location(
                latitude=37.7749, longitude=-122.4194, country_code="DE"
            ),
            status=microgrid_pb2.MICROGRID_STATUS_ACTIVE,
            create_timestamp=to_timestamp(create_timestamp),
        )
    ]
)


def assert_client_result(result: Any) -> None:
    """Assert that the client result matches the expected Microgrid list."""
    assert result == [
        Microgrid(
            id=MicrogridId(1234),
            enterprise_id=EnterpriseId(5678),
            name="Test Microgrid",
            delivery_area=DeliveryArea(
                code="Test Delivery Area", code_type=EnergyMarketCodeType.EUROPE_EIC
            ),
            location=Location(
                latitude=pytest.approx(37.7749),  # type: ignore[arg-type]
                longitude=pytest.approx(-122.4194),  # type: ignore[arg-type]
                country_code="DE",
            ),
            status=MicrogridStatus.ACTIVE,
            create_timestamp=create_timestamp,
        )
    ]
