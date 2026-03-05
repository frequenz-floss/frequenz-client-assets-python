# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""
Assets API client.

This module provides a client for the Assets API.
"""

from __future__ import annotations

from collections.abc import Iterable

from frequenz.api.assets.v1 import assets_pb2, assets_pb2_grpc
from frequenz.client.base import channel
from frequenz.client.base.client import BaseApiClient, call_stub_method
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.electrical_components import ElectricalComponentId

from ._microgrid import Microgrid
from ._microgrid_proto import microgrid_from_proto, microgrid_from_proto_with_issues
from .electrical_component._connection import ComponentConnection
from .electrical_component._connection_proto import (
    component_connection_from_proto,
    component_connection_from_proto_with_issues,
)
from .electrical_component._electrical_component import ElectricalComponent
from .electrical_component._electrical_component_proto import (
    electrical_component_from_proto_with_issues,
    electrical_component_proto,
)
from .exceptions import (
    ClientNotConnected,
    InvalidConnectionError,
    InvalidConnectionErrorGroup,
    InvalidElectricalComponentError,
    InvalidElectricalComponentErrorGroup,
    InvalidMicrogridError,
)

DEFAULT_GRPC_CALL_TIMEOUT = 60.0
"""The default timeout for gRPC calls made by this client (in seconds)."""


class AssetsApiClient(
    BaseApiClient[assets_pb2_grpc.PlatformAssetsStub]
):  # pylint: disable=too-many-arguments
    """A client for the Assets API."""

    def __init__(
        self,
        server_url: str,
        *,
        auth_key: str | None = None,
        sign_secret: str | None = None,
        channel_defaults: channel.ChannelOptions = channel.ChannelOptions(),
        connect: bool = True,
    ) -> None:
        """
        Initialize the AssetsApiClient.

        Args:
            server_url: The location of the microgrid API server in the form of a URL.
                The following format is expected:
                "grpc://hostname{:`port`}{?ssl=`ssl`}",
                where the `port` should be an int between 0 and 65535 (defaulting to
                9090) and `ssl` should be a boolean (defaulting to `true`).
                For example: `grpc://localhost:1090?ssl=true`.
            auth_key: The authentication key to use for the connection.
            sign_secret: The secret to use for signing requests.
            channel_defaults: The default options use to create the channel when not
                specified in the URL.
            connect: Whether to connect to the server as soon as a client instance is
                created. If `False`, the client will not connect to the server until
                [connect()][frequenz.client.base.client.BaseApiClient.connect] is
                called.
        """
        super().__init__(
            server_url,
            assets_pb2_grpc.PlatformAssetsStub,
            connect=connect,
            channel_defaults=channel_defaults,
            auth_key=auth_key,
            sign_secret=sign_secret,
        )

    @property
    def stub(self) -> assets_pb2_grpc.PlatformAssetsAsyncStub:
        """
        The gRPC stub for the Assets API.

        Returns:
            The gRPC stub for the Assets API.

        Raises:
            ClientNotConnected: If the client is not connected to the server.
        """
        if self._channel is None or self._stub is None:
            raise ClientNotConnected(server_url=self.server_url, operation="stub")
        # This type: ignore is needed because the stub is a sync stub, but we need to
        # use the async stub, so we cast the sync stub to the async stub.
        return self._stub  # type: ignore

    async def get_microgrid(  # noqa: DOC502,DOC503 (raises indirectly)
        self,
        microgrid_id: MicrogridId,
        *,
        raise_on_errors: bool = False,
    ) -> Microgrid:
        """
        Get the details of a microgrid.

        Args:
            microgrid_id: The ID of the microgrid to get the details of.
            raise_on_errors: If True, raise an
                [InvalidMicrogridError][frequenz.client.assets.exceptions.InvalidMicrogridError]
                when major validation issues are found instead of just
                logging them.

        Returns:
            The details of the microgrid.

        Raises:
            ApiClientError: If there are any errors communicating with the Assets API,
                most likely a subclass of [GrpcError][frequenz.client.base.exception.GrpcError].
            InvalidMicrogridError: If `raise_on_errors` is True and major
                validation issues are found.
        """
        response = await call_stub_method(
            self,
            lambda: self.stub.GetMicrogrid(
                assets_pb2.GetMicrogridRequest(microgrid_id=int(microgrid_id)),
                timeout=DEFAULT_GRPC_CALL_TIMEOUT,
            ),
            method_name="GetMicrogrid",
        )

        if raise_on_errors:
            major_issues: list[str] = []
            minor_issues: list[str] = []
            microgrid = microgrid_from_proto_with_issues(
                response.microgrid,
                major_issues=major_issues,
                minor_issues=minor_issues,
            )
            if major_issues:
                raise InvalidMicrogridError(
                    microgrid=microgrid,
                    major_issues=major_issues,
                    minor_issues=minor_issues,
                    raw_message=response.microgrid,
                )
            return microgrid

        return microgrid_from_proto(response.microgrid)

    async def list_microgrid_electrical_components(
        self,
        microgrid_id: MicrogridId,
        *,
        raise_on_errors: bool = False,
    ) -> list[ElectricalComponent]:
        """
        Get the electrical components of a microgrid.

        Args:
            microgrid_id: The ID of the microgrid to get the electrical components of.
            raise_on_errors: If True, raise an
                [InvalidElectricalComponentErrorGroup][frequenz.client.assets.exceptions.InvalidElectricalComponentErrorGroup]
                when major validation issues are found in any component instead
                of just logging them.

        Returns:
            The electrical components of the microgrid.

        Raises:
            InvalidElectricalComponentErrorGroup: If `raise_on_errors` is True
                and major validation issues are found.
        """
        response = await call_stub_method(
            self,
            lambda: self.stub.ListMicrogridElectricalComponents(
                assets_pb2.ListMicrogridElectricalComponentsRequest(
                    microgrid_id=int(microgrid_id),
                ),
                timeout=DEFAULT_GRPC_CALL_TIMEOUT,
            ),
            method_name="ListMicrogridElectricalComponents",
        )

        if raise_on_errors:
            components: list[ElectricalComponent] = []
            exceptions: list[InvalidElectricalComponentError] = []
            for component_pb in response.components:
                major_issues: list[str] = []
                minor_issues: list[str] = []
                component = electrical_component_from_proto_with_issues(
                    component_pb,
                    major_issues=major_issues,
                    minor_issues=minor_issues,
                )
                if major_issues:
                    exceptions.append(
                        InvalidElectricalComponentError(
                            component=component,
                            major_issues=major_issues,
                            minor_issues=minor_issues,
                            raw_message=component_pb,
                        )
                    )
                else:
                    components.append(component)
            if exceptions:
                raise InvalidElectricalComponentErrorGroup(
                    valid_components=components,
                    exceptions=exceptions,
                )
            return components

        return [
            electrical_component_proto(component) for component in response.components
        ]

    async def list_microgrid_electrical_component_connections(
        self,
        microgrid_id: MicrogridId,
        source_component_ids: Iterable[ElectricalComponentId] = (),
        destination_component_ids: Iterable[ElectricalComponentId] = (),
        *,
        raise_on_errors: bool = False,
    ) -> list[ComponentConnection | None]:
        """
        Get the electrical component connections of a microgrid.

        Args:
            microgrid_id: The ID of the microgrid to get the electrical
                component connections of.
            source_component_ids: Only return connections that originate from
                these component IDs. If None or empty, no filtering is applied.
            destination_component_ids: Only return connections that terminate at
                these component IDs. If None or empty, no filtering is applied.
            raise_on_errors: If True, raise an
                [InvalidConnectionErrorGroup][frequenz.client.assets.exceptions.InvalidConnectionErrorGroup]
                when major validation issues are found in any connection instead
                of just logging them.

        Returns:
            The electrical component connections of the microgrid.

        Raises:
            InvalidConnectionErrorGroup: If `raise_on_errors` is True and
                major validation issues are found.
        """
        request = assets_pb2.ListMicrogridElectricalComponentConnectionsRequest(
            microgrid_id=int(microgrid_id),
            source_component_ids=(int(c) for c in source_component_ids),
            destination_component_ids=(int(c) for c in destination_component_ids),
        )

        response = await call_stub_method(
            self,
            lambda: self.stub.ListMicrogridElectricalComponentConnections(
                request,
                timeout=DEFAULT_GRPC_CALL_TIMEOUT,
            ),
            method_name="ListMicrogridElectricalComponentConnections",
        )

        if raise_on_errors:
            valid_connections: list[ComponentConnection] = []
            exceptions: list[InvalidConnectionError] = []
            for conn_pb in filter(bool, response.connections):
                major_issues: list[str] = []
                connection = component_connection_from_proto_with_issues(
                    conn_pb, major_issues=major_issues
                )
                if major_issues:
                    exceptions.append(
                        InvalidConnectionError(
                            connection=connection,
                            major_issues=major_issues,
                            minor_issues=[],
                            raw_message=conn_pb,
                        )
                    )
                elif connection is not None:
                    valid_connections.append(connection)
            if exceptions:
                raise InvalidConnectionErrorGroup(
                    valid_connections=valid_connections,
                    exceptions=exceptions,
                )
            return valid_connections  # type: ignore[return-value]

        return list(
            map(
                component_connection_from_proto,
                filter(bool, response.connections),
            )
        )
