# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Test data for successful market topology relation listing."""

from datetime import datetime, timezone
from typing import Any

from frequenz.api.common.v1alpha8.grid import delivery_area_pb2, market_location_pb2
from frequenz.api.common.v1alpha8.market import market_area_pb2
from frequenz.api.common.v1alpha8.types import interval_pb2
from frequenz.api.platformassets.v1alpha1 import platformassets_pb2 as assets_pb2
from frequenz.client.base.conversion import to_timestamp
from frequenz.client.common.microgrid import MicrogridId

from frequenz.client.assets import (
    DeliveryArea,
    EnergyMarketCodeType,
    Interval,
    MarketLocation,
    MarketLocationId,
    MarketLocationIdType,
    MarketParticipation,
    MarketParticipationType,
    MarketTopologyRelation,
)


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        assets_pb2.ListMarketTopologyRelationsRequest(
            filter=assets_pb2.ListMarketTopologyRelationsRequest.MarketTopologyRelationsFilter(
                gridpool_ids=[7],
                microgrid_ids=[1234],
                market_location_id_values=[
                    market_location_pb2.MarketLocationIdValue(value="DE001")
                ],
                delivery_areas=[
                    delivery_area_pb2.DeliveryArea(
                        code="10YDE-1",
                        code_type=delivery_area_pb2.ENERGY_MARKET_CODE_TYPE_EUROPE_EIC,
                    )
                ],
                participation_types=[
                    assets_pb2.MARKET_PARTICIPATION_TYPE_ENERGY_TRADING
                ],
            )
        ),
        timeout=60.0,
    )


validity_start = datetime(2026, 1, 1, tzinfo=timezone.utc)
delivery_area = DeliveryArea(code="10YDE-1", code_type=EnergyMarketCodeType.EUROPE_EIC)
client_kwargs = {
    "gridpool_ids": [7],
    "microgrid_ids": [MicrogridId(1234)],
    "market_location_id_values": ["DE001"],
    "delivery_areas": [delivery_area],
    "participation_types": [MarketParticipationType.ENERGY_TRADING],
}
grpc_response = assets_pb2.ListMarketTopologyRelationsResponse(
    relations=[
        assets_pb2.MarketTopologyRelation(
            microgrid_id=1234,
            market_location=market_location_pb2.MarketLocation(
                market_area=market_area_pb2.MarketArea.ValueType(1),
                market_location_id=market_location_pb2.MarketLocationId(
                    id=market_location_pb2.MarketLocationIdValue(value="DE001"),
                    type=market_location_pb2.MARKET_LOCATION_ID_TYPE_MALO_ID,
                ),
            ),
            gridpool_id=7,
            delivery_area=delivery_area_pb2.DeliveryArea(
                code="10YDE-1",
                code_type=delivery_area_pb2.ENERGY_MARKET_CODE_TYPE_EUROPE_EIC,
            ),
            participations=[
                assets_pb2.MarketParticipation(
                    type=assets_pb2.MARKET_PARTICIPATION_TYPE_ENERGY_TRADING,
                    validity_period=interval_pb2.Interval(
                        start_time=to_timestamp(validity_start)
                    ),
                )
            ],
        )
    ],
)


def assert_client_result(result: Any) -> None:
    """Assert that the client result matches the expected relation list."""
    assert result == [
        MarketTopologyRelation(
            microgrid_id=MicrogridId(1234),
            market_location=MarketLocation(
                market_area=1,
                market_location_id=MarketLocationId(
                    value="DE001", type=MarketLocationIdType.MALO_ID
                ),
            ),
            gridpool_id=7,
            delivery_area=delivery_area,
            participations=[
                MarketParticipation(
                    type=MarketParticipationType.ENERGY_TRADING,
                    validity_period=Interval(start=validity_start),
                )
            ],
        )
    ]
