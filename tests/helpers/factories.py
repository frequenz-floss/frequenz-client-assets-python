# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Factory functions for creating test objects."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

from frequenz.client.assets.types import DeliveryArea, Location, Microgrid

from .test_data import MockData


def create_microgrid_mock(
    microgrid_id: int = MockData.microgrid_id,
    enterprise_id: int = MockData.enterprise_id,
    name: str = MockData.microgrid_name,
    status: int = MockData.microgrid_status,
    **overrides: Any,
) -> AsyncMock:
    """Create microgrid mocks with defaults."""
    mock = AsyncMock(name="microgrid_mock", spec=Microgrid)
    mock.id = microgrid_id
    mock.enterprise_id = enterprise_id
    mock.name = name
    mock.status = status
    # Configure create_timestamp mock to return a datetime directly (not async)
    mock_timestamp = MagicMock()
    mock_timestamp.ToDatetime.return_value = MockData.create_date
    mock.create_timestamp = mock_timestamp

    # Configure HasField to be synchronous (not async)
    mock.HasField = MagicMock(return_value=False)

    # Apply any overrides
    for key, value in overrides.items():
        setattr(mock, key, value)

    return mock


def create_delivery_area_mock(
    code: str = MockData.delivery_area_code,
    code_type: str = MockData.delivery_area_type,
) -> AsyncMock:
    """Create delivery area mocks."""
    mock = AsyncMock(name="delivery_area_mock", spec=DeliveryArea)
    mock.code = code
    mock.code_type = code_type
    return mock


def create_location_mock(
    latitude: float = MockData.latitude,
    longitude: float = MockData.longitude,
    country_code: str = MockData.country_code,
) -> AsyncMock:
    """Create location mocks."""
    mock = AsyncMock(name="location_mock", spec=Location)
    mock.latitude = latitude
    mock.longitude = longitude
    mock.country_code = country_code
    return mock


def create_response_mock() -> AsyncMock:
    """Create response mocks."""
    return AsyncMock()
