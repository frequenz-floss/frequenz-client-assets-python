# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Conversion of GridpoolEnergySchedule objects from protobuf messages."""

from frequenz.api.platformassets.v1alpha1 import platformassets_pb2
from frequenz.client.base import conversion
from frequenz.client.common.proto import enum_from_proto

from ._balancing_group_proto import balancing_group_from_proto
from ._delivery_area_proto import delivery_area_from_proto
from ._gridpool_energy_schedule import (
    DeliveryDuration,
    GridpoolEnergySchedule,
    GridpoolEnergyScheduleDirection,
    GridpoolEnergyScheduleTimeSeriesEntry,
)
from ._interval_proto import interval_from_proto


def gridpool_energy_schedule_time_series_entry_from_proto(
    message: platformassets_pb2.GridpoolEnergyScheduleTimeSeriesEntry,
) -> GridpoolEnergyScheduleTimeSeriesEntry:
    """Convert a protobuf schedule time-series entry to a domain object."""
    return GridpoolEnergyScheduleTimeSeriesEntry(
        start_time=(
            conversion.to_datetime(message.start_time)
            if message.HasField("start_time")
            else None
        ),
        active_power_w=message.active_power_w,
    )


def gridpool_energy_schedule_from_proto(
    message: platformassets_pb2.GridpoolEnergySchedule,
) -> GridpoolEnergySchedule:
    """Convert a protobuf gridpool energy schedule to a domain object."""
    return GridpoolEnergySchedule(
        gridpool_id=message.gridpool_id,
        schedule_id=message.schedule_id,
        name=message.name or None,
        counterparty_balancing_group=(
            balancing_group_from_proto(message.counterparty_balancing_group)
            if message.HasField("counterparty_balancing_group")
            else None
        ),
        counterparty_delivery_area=(
            delivery_area_from_proto(message.counterparty_delivery_area)
            if message.HasField("counterparty_delivery_area")
            else None
        ),
        frequenz_delivery_area=(
            delivery_area_from_proto(message.frequenz_delivery_area)
            if message.HasField("frequenz_delivery_area")
            else None
        ),
        direction=enum_from_proto(message.direction, GridpoolEnergyScheduleDirection),
        validity_period=(
            interval_from_proto(message.validity_period)
            if message.HasField("validity_period")
            else None
        ),
        cancel_time=(
            conversion.to_datetime(message.cancel_time)
            if message.HasField("cancel_time")
            else None
        ),
        delivery_duration=enum_from_proto(message.delivery_duration, DeliveryDuration),
        time_series=[
            gridpool_energy_schedule_time_series_entry_from_proto(entry)
            for entry in message.time_series
        ],
    )
