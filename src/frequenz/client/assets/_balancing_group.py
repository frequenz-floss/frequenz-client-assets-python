# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Balancing group definitions."""

from dataclasses import dataclass

from ._delivery_area import EnergyMarketCodeType


@dataclass(frozen=True, kw_only=True)
class BalancingGroup:
    """A market balancing group identified by its market code."""

    code: str | None
    """The balancing group code."""

    code_type: EnergyMarketCodeType | int
    """The type of market code used to identify the balancing group."""
