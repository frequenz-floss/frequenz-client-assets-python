# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Time interval filters."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, kw_only=True)
class Interval:
    """A half-open time interval: `[start, end)`."""

    start: datetime | None = None
    """The inclusive start of the interval."""

    end: datetime | None = None
    """The exclusive end of the interval."""

    def __post_init__(self) -> None:
        """Validate this interval."""
        if self.start is not None and self.end is not None and self.start > self.end:
            raise ValueError(
                f"Start ({self.start}) must be before or equal to end ({self.end})"
            )
