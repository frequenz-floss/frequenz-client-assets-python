# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Gridpool energy schedule definitions."""

import enum
from dataclasses import dataclass
from datetime import datetime

from frequenz.api.common.v1alpha8.grid import delivery_duration_pb2
from frequenz.api.platformassets.v1alpha1 import platformassets_pb2

from ._balancing_group import BalancingGroup
from ._delivery_area import DeliveryArea
from ._interval import Interval


@enum.unique
class DeliveryDuration(enum.Enum):
    """Delivery duration used by scheduled energy values."""

    UNSPECIFIED = delivery_duration_pb2.DELIVERY_DURATION_UNSPECIFIED
    """The delivery duration is unspecified."""

    MINUTES_5 = delivery_duration_pb2.DELIVERY_DURATION_5
    """A 5-minute delivery duration."""

    MINUTES_15 = delivery_duration_pb2.DELIVERY_DURATION_15
    """A 15-minute delivery duration."""

    MINUTES_30 = delivery_duration_pb2.DELIVERY_DURATION_30
    """A 30-minute delivery duration."""

    MINUTES_60 = delivery_duration_pb2.DELIVERY_DURATION_60
    """A 60-minute delivery duration."""


@enum.unique
class GridpoolEnergyScheduleDirection(enum.Enum):
    """Direction of a scheduled energy exchange."""

    UNSPECIFIED = platformassets_pb2.GRIDPOOL_ENERGY_SCHEDULE_DIRECTION_UNSPECIFIED
    """The direction is unspecified."""

    IMPORT = platformassets_pb2.GRIDPOOL_ENERGY_SCHEDULE_DIRECTION_IMPORT
    """Energy is imported into the Frequenz balancing group."""

    EXPORT = platformassets_pb2.GRIDPOOL_ENERGY_SCHEDULE_DIRECTION_EXPORT
    """Energy is exported from the Frequenz balancing group."""


@dataclass(frozen=True, kw_only=True)
class GridpoolEnergyScheduleTimeSeriesEntry:
    """A scheduled active-power value for one delivery period."""

    start_time: datetime | None
    """The inclusive start timestamp of the scheduled delivery value."""

    active_power_w: float
    """Scheduled active power in watts."""


@dataclass(frozen=True, kw_only=True)
class GridpoolEnergySchedule:  # pylint: disable=too-many-instance-attributes
    """A static energy schedule associated with a gridpool."""

    gridpool_id: int
    """The unique identifier of the gridpool this schedule belongs to."""

    schedule_id: int
    """The unique identifier of the energy schedule."""

    name: str | None
    """The human-readable schedule name."""

    counterparty_balancing_group: BalancingGroup | None
    """The third-party balancing group involved in the scheduled exchange."""

    counterparty_delivery_area: DeliveryArea | None
    """Delivery area of the counterparty side of the scheduled exchange."""

    frequenz_delivery_area: DeliveryArea | None
    """Delivery area of the Frequenz side of the scheduled exchange."""

    direction: GridpoolEnergyScheduleDirection | int
    """Direction of the scheduled exchange from the Frequenz perspective."""

    validity_period: Interval | None
    """Validity interval of the schedule configuration."""

    cancel_time: datetime | None
    """Timestamp at which the schedule was cancelled."""

    delivery_duration: DeliveryDuration | int
    """Delivery duration used by all time-series entries in this schedule."""

    time_series: list[GridpoolEnergyScheduleTimeSeriesEntry]
    """Scheduled active-power values."""
