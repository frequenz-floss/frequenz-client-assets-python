# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Steam boiler component."""

import dataclasses
from typing import Literal

from ._category import ElectricalComponentCategory
from ._electrical_component import ElectricalComponent


@dataclasses.dataclass(frozen=True, kw_only=True)
class SteamBoiler(ElectricalComponent):
    """A steam boiler."""

    category: Literal[ElectricalComponentCategory.STEAM_BOILER] = (
        ElectricalComponentCategory.STEAM_BOILER
    )
    """The category of this component."""
