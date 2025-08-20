# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Global test configuration and fixtures."""

from collections.abc import Iterator
from dataclasses import dataclass
from unittest.mock import AsyncMock

import pytest

from frequenz.client.assets import AssetsApiClient

from .helpers.factories import (
    create_delivery_area_mock,
    create_location_mock,
    create_microgrid_mock,
    create_response_mock,
)
from .helpers.test_data import MockData


@dataclass
class ClientSetup:  # pylint: disable=too-many-instance-attributes
    """Parameters for setting up the client."""

    client: AssetsApiClient
    mock_stub: AsyncMock
    microgrid_id: int
    enterprise_id: int
    test_name: str
    mock_microgrid: AsyncMock
    mock_delivery_area: AsyncMock
    mock_location: AsyncMock
    mock_response: AsyncMock


@pytest.fixture
def client_setup() -> Iterator[ClientSetup]:
    """
    Generate a setup parameters for the client.

    This fixture is used to set up the client and the mock stub.
    """
    client = AssetsApiClient(
        server_url=MockData.server_url,
        auth_key=MockData.auth_key,
        sign_secret=MockData.sign_secret,
        connect=False,
    )

    mock_stub = AsyncMock()
    client._stub = mock_stub  # pylint: disable=protected-access
    client._channel = AsyncMock()  # pylint: disable=protected-access

    # Create all mocks using factories
    mock_microgrid = create_microgrid_mock()
    mock_delivery_area = create_delivery_area_mock()
    mock_location = create_location_mock()
    mock_response = create_response_mock()

    yield ClientSetup(
        client=client,
        mock_stub=mock_stub,
        microgrid_id=MockData.microgrid_id,
        enterprise_id=MockData.enterprise_id,
        test_name=MockData.microgrid_name,
        mock_microgrid=mock_microgrid,
        mock_delivery_area=mock_delivery_area,
        mock_location=mock_location,
        mock_response=mock_response,
    )
