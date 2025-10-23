# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""JSON encoder for ComponentConnection objects."""

import json
from dataclasses import asdict

from .._utils import AssetsJSONEncoder
from ._connection import ComponentConnection


def component_connections_to_json(
    component_connections: list[ComponentConnection],
) -> str:
    """Convert a list of ElectricalComponent objects to a JSON string."""
    return json.dumps(
        [asdict(connection) for connection in component_connections],
        cls=AssetsJSONEncoder,
        indent=2,
    )
