# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Test data for successful gridpool energy schedule listing."""

from datetime import datetime, timezone
from typing import Any

from frequenz.api.common.v1alpha8.grid import (
    balancing_group_pb2,
    delivery_area_pb2,
    delivery_duration_pb2,
)
from frequenz.api.common.v1alpha8.types import interval_pb2
from frequenz.api.platformassets.v1alpha1 import platformassets_pb2 as assets_pb2
from frequenz.client.base.conversion import to_timestamp

from frequenz.client.assets import (
    BalancingGroup,
    DeliveryArea,
    DeliveryDuration,
    EnergyMarketCodeType,
    GridpoolEnergySchedule,
    GridpoolEnergyScheduleDirection,
    GridpoolEnergyScheduleTimeSeriesEntry,
    Interval,
)


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        assets_pb2.ListGridpoolEnergySchedulesRequest(
            gridpool_id=7,
            filter=assets_pb2.ListGridpoolEnergySchedulesRequest.GridpoolEnergySchedulesFilter(
                schedule_ids=[42],
                directions=[
                    assets_pb2.GRIDPOOL_ENERGY_SCHEDULE_DIRECTION_IMPORT,
                ],
                time_series_interval=interval_pb2.Interval(
                    start_time=to_timestamp(filter_start),
                    end_time=to_timestamp(filter_end),
                ),
                effective_validity_period=interval_pb2.Interval(
                    start_time=to_timestamp(validity_start),
                    end_time=to_timestamp(validity_end),
                ),
            ),
        ),
        timeout=60.0,
    )


filter_start = datetime(2026, 1, 1, tzinfo=timezone.utc)
filter_end = datetime(2026, 1, 2, tzinfo=timezone.utc)
validity_start = datetime(2025, 12, 1, tzinfo=timezone.utc)
validity_end = datetime(2026, 2, 1, tzinfo=timezone.utc)
cancel_time = datetime(2026, 1, 15, tzinfo=timezone.utc)
entry_start = datetime(2026, 1, 1, 0, 15, tzinfo=timezone.utc)

client_args = (7,)
client_kwargs = {
    "schedule_ids": [42],
    "directions": [GridpoolEnergyScheduleDirection.IMPORT],
    "time_series_interval": Interval(start=filter_start, end=filter_end),
    "effective_validity_period": Interval(start=validity_start, end=validity_end),
}
grpc_response = assets_pb2.ListGridpoolEnergySchedulesResponse(
    gridpool_id=7,
    schedules=[
        assets_pb2.GridpoolEnergySchedule(
            gridpool_id=7,
            schedule_id=42,
            name="OTC baseline",
            counterparty_balancing_group=balancing_group_pb2.BalancingGroup(
                code="11XCOUNTER",
                code_type=delivery_area_pb2.ENERGY_MARKET_CODE_TYPE_EUROPE_EIC,
            ),
            counterparty_delivery_area=delivery_area_pb2.DeliveryArea(
                code="10YDE-1",
                code_type=delivery_area_pb2.ENERGY_MARKET_CODE_TYPE_EUROPE_EIC,
            ),
            frequenz_delivery_area=delivery_area_pb2.DeliveryArea(
                code="10YDE-2",
                code_type=delivery_area_pb2.ENERGY_MARKET_CODE_TYPE_EUROPE_EIC,
            ),
            direction=assets_pb2.GRIDPOOL_ENERGY_SCHEDULE_DIRECTION_IMPORT,
            validity_period=interval_pb2.Interval(
                start_time=to_timestamp(validity_start),
                end_time=to_timestamp(validity_end),
            ),
            cancel_time=to_timestamp(cancel_time),
            delivery_duration=delivery_duration_pb2.DELIVERY_DURATION_15,
            time_series=[
                assets_pb2.GridpoolEnergyScheduleTimeSeriesEntry(
                    start_time=to_timestamp(entry_start),
                    active_power_w=1234.5,
                )
            ],
        )
    ],
)


def assert_client_result(result: Any) -> None:
    """Assert that the client result matches the expected schedule list."""
    assert result == [
        GridpoolEnergySchedule(
            gridpool_id=7,
            schedule_id=42,
            name="OTC baseline",
            counterparty_balancing_group=BalancingGroup(
                code="11XCOUNTER", code_type=EnergyMarketCodeType.EUROPE_EIC
            ),
            counterparty_delivery_area=DeliveryArea(
                code="10YDE-1", code_type=EnergyMarketCodeType.EUROPE_EIC
            ),
            frequenz_delivery_area=DeliveryArea(
                code="10YDE-2", code_type=EnergyMarketCodeType.EUROPE_EIC
            ),
            direction=GridpoolEnergyScheduleDirection.IMPORT,
            validity_period=Interval(start=validity_start, end=validity_end),
            cancel_time=cancel_time,
            delivery_duration=DeliveryDuration.MINUTES_15,
            time_series=[
                GridpoolEnergyScheduleTimeSeriesEntry(
                    start_time=entry_start,
                    active_power_w=1234.5,
                )
            ],
        )
    ]
