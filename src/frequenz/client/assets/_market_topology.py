# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Market topology relation definitions."""

import enum
from dataclasses import dataclass

from frequenz.api.platformassets.v1alpha1 import platformassets_pb2
from frequenz.client.common.microgrid import MicrogridId

from ._delivery_area import DeliveryArea
from ._interval import Interval
from ._market_location import MarketLocation


@enum.unique
class MarketParticipationType(enum.Enum):
    """Market-related use cases for topology relations."""

    UNSPECIFIED = platformassets_pb2.MARKET_PARTICIPATION_TYPE_UNSPECIFIED
    """The market participation type is unspecified."""

    ENERGY_TRADING = platformassets_pb2.MARKET_PARTICIPATION_TYPE_ENERGY_TRADING
    """Energy trading, supply, balancing, or settlement participation."""

    FLEX_MARKETS = platformassets_pb2.MARKET_PARTICIPATION_TYPE_FLEX_MARKETS
    """Flex-market or ancillary-service participation."""


@dataclass(frozen=True, kw_only=True)
class MarketParticipation:
    """A relation's participation in a specific market use case."""

    type: MarketParticipationType | int
    """The use case for which this relation participates."""

    validity_period: Interval | None
    """Configured validity interval for this participation."""


@dataclass(frozen=True, kw_only=True)
class MarketTopologyRelation:
    """A relation between a gridpool, microgrid, and market location."""

    microgrid_id: MicrogridId | None
    """The microgrid associated with this relation."""

    market_location: MarketLocation | None
    """The market location associated with this relation."""

    gridpool_id: int | None
    """The gridpool associated with this relation."""

    delivery_area: DeliveryArea | None
    """Delivery area in which this relation applies."""

    participations: list[MarketParticipation]
    """Use-case-specific participations for this relation."""
