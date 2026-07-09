# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Market location definitions."""

import enum
from dataclasses import dataclass

from frequenz.api.common.v1alpha8.grid import market_location_pb2


@enum.unique
class MarketLocationIdType(enum.Enum):
    """External market identifier types used for market locations."""

    UNSPECIFIED = market_location_pb2.MARKET_LOCATION_ID_TYPE_UNSPECIFIED
    """The market location ID type is unspecified."""

    MALO_ID = market_location_pb2.MARKET_LOCATION_ID_TYPE_MALO_ID
    """Germany Marktlokations-ID."""

    ZAEHLPUNKT = market_location_pb2.MARKET_LOCATION_ID_TYPE_ZAEHLPUNKT
    """Austria Zaehlpunktbezeichnung."""

    MPAN = market_location_pb2.MARKET_LOCATION_ID_TYPE_MPAN
    """United Kingdom Meter Point Administration Number."""

    POD = market_location_pb2.MARKET_LOCATION_ID_TYPE_POD
    """Italy Point of Delivery."""

    CUPS = market_location_pb2.MARKET_LOCATION_ID_TYPE_CUPS
    """Spain Codigo Universal de Punto de Suministro."""

    PRM = market_location_pb2.MARKET_LOCATION_ID_TYPE_PRM
    """France Point de Reference et Mesure."""

    EAN = market_location_pb2.MARKET_LOCATION_ID_TYPE_EAN
    """European Article Number."""

    GSRN = market_location_pb2.MARKET_LOCATION_ID_TYPE_GSRN
    """GS1 Global Service Relation Number."""

    ESI_ID = market_location_pb2.MARKET_LOCATION_ID_TYPE_ESI_ID
    """United States Electric Service Identifier."""

    NMI = market_location_pb2.MARKET_LOCATION_ID_TYPE_NMI
    """Australia National Metering Identifier."""

    ICP = market_location_pb2.MARKET_LOCATION_ID_TYPE_ICP
    """New Zealand Installation Control Point."""

    SPN = market_location_pb2.MARKET_LOCATION_ID_TYPE_SPN
    """Japan Supply Point Number."""

    OTHER = market_location_pb2.MARKET_LOCATION_ID_TYPE_OTHER
    """Generic identifier for markets not modeled explicitly."""


@dataclass(frozen=True, kw_only=True)
class MarketLocationId:
    """A market-standard identifier for a market location."""

    value: str | None
    """The official market location identifier value."""

    type: MarketLocationIdType | int
    """The type of official market identifier."""


@dataclass(frozen=True, kw_only=True)
class MarketLocation:
    """A market-facing metering point in a specific market area."""

    market_area: int
    """The market area in which this market location is registered."""

    market_location_id: MarketLocationId | None
    """The official market location identifier."""
