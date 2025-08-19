# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""
Assets API client.

This module provides a client for the Assets API.
"""

from __future__ import annotations

from frequenz.api.assets.v1 import assets_pb2, assets_pb2_grpc
from frequenz.client.base.client import BaseApiClient, call_stub_method

from frequenz.client.assets.types import Microgrid

from .exceptions import ClientNotConnected


class AssetsApiClient(BaseApiClient[assets_pb2_grpc.PlatformAssetsStub]):
    """A client for the Assets API."""

    def __init__(
        self,
        server_url: str,
        auth_key: str | None,
        sign_secret: str | None,
        connect: bool = True,
    ) -> None:
        """
        Initialize the AssetsApiClient.

        Args:
            server_url: The URL of the server to connect to.
            auth_key: The API key to use when connecting to the service.
            sign_secret: The secret to use when creating message HMAC.
            connect: Whether to connect to the server as soon as a client instance is created.
        """
        super().__init__(
            server_url,
            assets_pb2_grpc.PlatformAssetsStub,
            connect=connect,
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

    async def get_microgrid_details(  # noqa: DOC502 (raises ApiClientError indirectly)
        self, microgrid_id: int
    ) -> Microgrid:
        """
        Get the details of a microgrid.

        Args:
            microgrid_id: The ID of the microgrid to get the details of.

        Returns:
            The details of the microgrid.

        Raises:
            ApiClientError: If there are any errors communicating with the Assets API,
                most likely a subclass of [GrpcError][frequenz.client.assets.GrpcError].
        """
        request = assets_pb2.GetMicrogridRequest(microgrid_id=microgrid_id)
        response = await call_stub_method(
            self,
            lambda: self.stub.GetMicrogrid(request),
            method_name="GetMicrogrid",
        )

        return Microgrid.from_protobuf(response.microgrid)
