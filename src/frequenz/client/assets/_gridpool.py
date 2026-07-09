# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Gridpool definitions."""

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class Gridpool:
    """A virtual balancing-group structure used for market interactions."""

    id: int
    """The unique identifier of the gridpool."""

    name: str | None
    """The human-readable gridpool name."""
