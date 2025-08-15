# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""
Assets API client.

This module provides a client for the Assets API.
"""

from typing import Awaitable, Optional, cast

import grpc
from frequenz.api.assets.v1.assets_pb2 import (
    GetMicrogridRequest as PBGetMicrogridRequest,
)
from frequenz.api.assets.v1.assets_pb2 import (
    GetMicrogridResponse as PBGetMicrogridResponse,
)
from frequenz.api.assets.v1.assets_pb2_grpc import PlatformAssetsStub
from frequenz.client.base.client import BaseApiClient
from frequenz.client.base.exception import ClientNotConnected
from grpc import StatusCode

from frequenz.client.assets.exceptions import (
    AssetsApiError,
    AuthenticationError,
    NotFoundError,
    ServiceUnavailableError,
)
from frequenz.client.assets.types import Microgrid


class AssetsApiClient(BaseApiClient[PlatformAssetsStub]):
    """A client for the Assets API."""

    def __init__(
        self,
        server_url: str,
        auth_key: Optional[str],
        sign_secret: Optional[str],
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
            PlatformAssetsStub,
            connect=connect,
            auth_key=auth_key,
            sign_secret=sign_secret,
        )

    @property
    def stub(self) -> PlatformAssetsStub:
        """
        The gRPC stub for the Assets API.

        Returns:
            The gRPC stub for the Assets API.

        Raises:
            ClientNotConnected: If the client is not connected to the server.
        """
        if self._channel is None or self._stub is None:
            raise ClientNotConnected(server_url=self.server_url, operation="stub")
        return self._stub

    async def get_microgrid_details(self, microgrid_id: int) -> Microgrid:
        """
        Get the details of a microgrid.

        Args:
            microgrid_id: The ID of the microgrid to get the details of.

        Returns:
            The details of the microgrid.

        Raises:
            NotFoundError: If the microgrid is not found.
            AuthenticationError: If the authentication fails.
            ServiceUnavailableError: If the service is unavailable.
            AssetsApiError: If the API returns an error.
            Exception: If an unexpected error occurs.
        """
        try:
            request = PBGetMicrogridRequest(microgrid_id=microgrid_id)
            response = await cast(
                Awaitable[PBGetMicrogridResponse],
                self.stub.GetMicrogrid(request),
            )

            if response.microgrid is None:
                raise NotFoundError(microgrid_id)

            return Microgrid.from_protobuf(response.microgrid)
        except grpc.aio.AioRpcError as e:
            if e.code() == StatusCode.NOT_FOUND:
                raise NotFoundError(microgrid_id) from e
            if e.code() == StatusCode.UNAUTHENTICATED:
                raise AuthenticationError(e.details()) from e
            if e.code() == StatusCode.UNAVAILABLE:
                raise ServiceUnavailableError(e.details()) from e
            raise AssetsApiError(
                message=f"gRPC error: {e.details() or 'Unknown error'}",
                status_code=e.code().name,
                details=e.details(),
            ) from e
        except Exception as e:
            if not isinstance(e, AssetsApiError):
                raise AssetsApiError(
                    message=str(e),
                    status_code=None,
                    details=None,
                ) from e
            raise e
