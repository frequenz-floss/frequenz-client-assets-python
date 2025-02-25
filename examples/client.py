# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Examples usage of PlatformAssets API."""

import argparse
import asyncio
from pprint import pprint

from frequenz.client.assets._client import AssetsApiClient


async def main(
    microgrid_id: int,
    component_ids: list[int],
    categories: list[int] | None,
    source_component_ids: list[int] | None,
    destination_component_ids: list[int] | None,
) -> None:
    """Test the AssetsApiClient.

    Args:
        microgrid_id: The ID of the microgrid to query.
        component_ids: List of component IDs to filter.
        categories: List of component categories to filter.
        source_component_ids: List of source component IDs to filter.
        destination_component_ids: List of destination component IDs to filter.
    """
    server_url = "localhost:50052"
    client = AssetsApiClient(server_url)

    print("########################################################")
    print("Fetching microgrid details")

    microgrid_details = await client.get_microgrid_details(microgrid_id)
    pprint(microgrid_details)

    print("########################################################")
    print("Listing microgrid components")

    components = await client.list_microgrid_component_connections(
        microgrid_id, component_ids, categories
    )
    pprint(components)

    print("########################################################")
    print("Listing microgrid component connections")

    connections = await client.list_microgrid_component_connections(
        microgrid_id, source_component_ids, destination_component_ids
    )
    pprint(connections)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("microgrid_id", type=int, help="Microgrid ID")
    parser.add_argument(
        "component_ids", nargs="*", type=int, help="List of component IDs to filter"
    )
    parser.add_argument(
        "categories", nargs="*", type=str, help="List of component categories to filter"
    )
    parser.add_argument(
        "source_component_ids",
        nargs="*",
        type=int,
        help="List of source component IDs to filter",
    )
    parser.add_argument(
        "destination_component_ids",
        nargs="*",
        type=int,
        help="List of destination component IDs to filter",
    )

    args = parser.parse_args()
    asyncio.run(
        main(
            args.microgrid_id,
            args.component_ids,
            args.categories,
            args.source_component_ids,
            args.destination_component_ids,
        )
    )
