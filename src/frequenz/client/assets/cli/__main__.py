# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Command-line interface for the Frequenz Assets API client.

This module provides a CLI interface for interacting with the Assets API,
allowing users to query microgrid information and other assets data
from the command line.

The CLI supports both interactive and scripted usage, with options for
authentication via command-line arguments or environment variables.

Example:
    ```bash
    # Basic usage with command-line arguments
    assets-cli \
        --url "grpc://api.example.com:443" \
        --auth-key "your-key" \
        --sign-secret "your-secret" \
        microgrid 123

    # Using environment variables
    export ASSETS_API_URL="grpc://api.example.com:5555"
    export ASSETS_API_AUTH_KEY="your-key"
    export ASSETS_API_SIGN_SECRET="your-secret"
    assets-cli microgrid 123
    ```

Environment Variables:
    ASSETS_API_URL: The URL of the Assets API server
    ASSETS_API_AUTH_KEY: API authentication key
    ASSETS_API_SIGN_SECRET: API signing secret for HMAC authentication
"""

import asyncio
import json

import asyncclick as click

from frequenz.client.assets._client import AssetsApiClient
from frequenz.client.assets.exceptions import ApiClientError

from ._utils import (
    print_component_connections,
    print_electrical_components,
    print_microgrid_details,
)


@click.group(invoke_without_command=True)
@click.option(
    "--url",
    help="Assets API Url",
    envvar="ASSETS_API_URL",
    show_envvar=True,
)
@click.option(
    "--auth-key",
    help="API auth key for authentication",
    envvar="ASSETS_API_AUTH_KEY",
    show_envvar=True,
    required=False,
)
@click.option(
    "--sign-secret",
    help="API signing secret for authentication",
    envvar="ASSETS_API_SIGN_SECRET",
    show_envvar=True,
    required=False,
    default=None,
)
@click.pass_context
async def cli(
    ctx: click.Context,
    url: str,
    auth_key: str | None,
    sign_secret: str | None,
) -> None:
    """
    Set up the main CLI group for the Assets API client.

    This function sets up the main CLI interface and handles global
    configuration including server URL and authentication credentials.
    It validates required parameters and initializes the API client
    for use by subcommands.

    Args:
        ctx: Click context object for storing shared state.
        url: The URL of the Assets API server (e.g., "grpc://api.example.com:5555").
        auth_key: API authentication key for accessing the service.
        sign_secret: API signing secret for HMAC authentication.

    Raises:
        click.BadParameter: If required authentication parameters are missing.
    """
    if ctx.obj is None:
        ctx.obj = {}

    if not auth_key:
        raise click.BadParameter(
            "You must provide an API auth key using --auth-key or "
            "the ASSETS_API_AUTH_KEY environment variable."
        )

    if not sign_secret:
        raise click.BadParameter(
            "You must provide an API signing secret using --sign-secret or "
            "the ASSETS_API_SIGN_SECRET environment variable."
        )

    ctx.obj["client"] = AssetsApiClient(
        server_url=url, auth_key=auth_key, sign_secret=sign_secret, connect=True
    )


@cli.command("microgrid")
@click.pass_context
@click.argument("microgrid-id", required=True, type=int)
async def get_microgrid(
    ctx: click.Context,
    microgrid_id: int,
) -> None:
    """
    Get and display microgrid details by ID.

    This command fetches detailed information about a specific microgrid
    from the Assets API and displays it in JSON format. The output can
    be piped to other tools for further processing.

    Args:
        ctx: Click context object containing the initialized API client.
        microgrid_id: The unique identifier of the microgrid to retrieve.

    Raises:
        click.Abort: If there is an error printing the microgrid details.

    Example:
        ```bash
        # Get details for microgrid with ID 123
        assets-cli microgrid 123

        # Pipe output to jq for filtering
        assets-cli microgrid 123 | jq ".name"
        ```
    """
    try:
        client = ctx.obj["client"]
        microgrid_details = await client.get_microgrid(microgrid_id)
        print_microgrid_details(microgrid_details)
    except ApiClientError as e:
        error_dict = {
            "error_type": type(e).__name__,
            "server_url": e.server_url,
            "operation": e.operation,
            "description": e.description,
        }
        click.echo(json.dumps(error_dict, indent=2))
        raise click.Abort()


@cli.command("electrical-components")
@click.pass_context
@click.argument("microgrid-id", required=True, type=int)
async def list_microgrid_electrical_components(
    ctx: click.Context,
    microgrid_id: int,
) -> None:
    """
    Get and display electrical components by microgrid ID.

    This command fetches detailed information about all electrical components
    in a specific microgrid from the Assets API and displays it in JSON format.
    The output can be piped to other tools for further processing.

    Args:
        ctx: Click context object containing the initialized API client.
        microgrid_id: The unique identifier of the microgrid to retrieve.

    Raises:
        click.Abort: If there is an error printing the electrical components.

    Example:
        ```bash
        # Get details for microgrid with ID 123
        assets-cli electrical-components 123

        # Pipe output to jq for filtering
        assets-cli electrical-components 123 | jq ".id"
        ```
    """
    try:
        client = ctx.obj["client"]
        electrical_components = await client.list_microgrid_electrical_components(
            microgrid_id
        )
        print_electrical_components(electrical_components)
    except ApiClientError as e:
        error_dict = {
            "error_type": type(e).__name__,
            "server_url": e.server_url,
            "operation": e.operation,
            "description": e.description,
        }
        click.echo(json.dumps(error_dict, indent=2))
        raise click.Abort()


@cli.command("component-connections")
@click.pass_context
@click.argument("microgrid-id", required=True, type=int)
@click.option(
    "--source",
    "source_component_ids",
    help="Filter connections by source component ID(s). Can be specified multiple times.",
    type=int,
    multiple=True,
    required=False,
)
@click.option(
    "--destination",
    "destination_component_ids",
    help="Filter connections by destination component ID(s). Can be specified multiple times.",
    type=int,
    multiple=True,
    required=False,
)
async def list_microgrid_electrical_component_connections(
    ctx: click.Context,
    microgrid_id: int,
    source_component_ids: tuple[int, ...],
    destination_component_ids: tuple[int, ...],
) -> None:
    """
    Get and display electrical component connections by microgrid ID.

    This command fetches detailed information about all electrical component connections
    in a specific microgrid from the Assets API and displays it in JSON format.
    The output can be piped to other tools for further processing.

    Args:
        ctx: Click context object containing the initialized API client.
        microgrid_id: The unique identifier of the microgrid to retrieve.
        source_component_ids: Optional filter for connections from specific
            source component IDs.
        destination_component_ids: Optional filter for connections to specific
            destination component IDs.

    Raises:
        click.Abort: If there is an error printing the electrical component connections.

    Example:
        ```bash
        # Get all connections for microgrid with ID 123
        assets-cli component-connections 123

        # Filter by source component
        assets-cli component-connections 123 --source 5

        # Filter by destination component
        assets-cli component-connections 123 --destination 10

        # Filter by both source and destination
        assets-cli component-connections 123 --source 5 --destination 10

        # Filter by multiple source components
        assets-cli component-connections 123 --source 5 --source 6 --source 7

        # Pipe output to jq for filtering
        assets-cli component-connections 123 | jq ".[]"
        ```
    """
    try:
        client = ctx.obj["client"]
        component_connections = (
            await client.list_microgrid_electrical_component_connections(
                microgrid_id,
                source_component_ids=(
                    list(source_component_ids) if source_component_ids else None
                ),
                destination_component_ids=(
                    list(destination_component_ids)
                    if destination_component_ids
                    else None
                ),
            )
        )
        print_component_connections(component_connections)
    except ApiClientError as e:
        error_dict = {
            "error_type": type(e).__name__,
            "server_url": e.server_url,
            "operation": e.operation,
            "description": e.description,
        }
        click.echo(json.dumps(error_dict, indent=2))
        raise click.Abort()


def main() -> None:
    """
    Initialize and run the CLI application.

    This function serves as the entry point when the module is run
    directly. It initializes the asyncio event loop and runs the
    main CLI application.

    The function handles the setup and teardown of the asyncio event
    loop, ensuring proper cleanup of resources.
    """
    asyncio.run(cli.main())


if __name__ == "__main__":
    main()
