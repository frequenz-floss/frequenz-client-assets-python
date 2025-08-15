# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for the frequenz.client package."""

from unittest.mock import AsyncMock

import pytest
from grpc import StatusCode
from grpc.aio import AioRpcError

from frequenz.client.assets.exceptions import NotFoundError

from .conftest import ClientSetup
from .helpers.assertions import AssertionHelpers


def setup_microgrid_with_fields(
    mock_microgrid: AsyncMock,
    has_delivery_area: bool = False,
    has_location: bool = False,
    delivery_area: AsyncMock | None = None,
    location: AsyncMock | None = None,
) -> None:
    """Set up microgrid mock with optional fields."""

    def has_field_side_effect(field_name: str) -> bool:
        if field_name == "delivery_area":
            return has_delivery_area
        if field_name == "location":
            return has_location
        return False

    mock_microgrid.HasField.side_effect = has_field_side_effect

    if has_delivery_area and delivery_area:
        mock_microgrid.delivery_area = delivery_area

    if has_location and location:
        mock_microgrid.location = location


def create_microgrid_response(
    mock_microgrid: AsyncMock,
    mock_response: AsyncMock,
) -> AsyncMock:
    """Create a complete response with microgrid."""
    mock_response.microgrid = mock_microgrid
    return mock_response


@pytest.mark.parametrize(
    "has_delivery_area,has_location",
    [
        (False, False),
        (True, False),
        (False, True),
        (True, True),
    ],
    ids=[
        "without optional fields",
        "with delivery area only",
        "with location only",
        "with all optional fields",
    ],
)
async def test_get_microgrid_details_optional_fields(
    client_setup: ClientSetup,
    has_delivery_area: bool,
    has_location: bool,
) -> None:
    """Test get_microgrid_details with different combinations of optional fields."""
    client, mock_stub = client_setup.client, client_setup.mock_stub

    # Setup
    setup_microgrid_with_fields(
        client_setup.mock_microgrid,
        has_delivery_area=has_delivery_area,
        has_location=has_location,
        delivery_area=client_setup.mock_delivery_area if has_delivery_area else None,
        location=client_setup.mock_location if has_location else None,
    )
    response = create_microgrid_response(
        client_setup.mock_microgrid, client_setup.mock_response
    )
    mock_stub.GetMicrogrid.return_value = response

    # Execute
    result = await client.get_microgrid_details(client_setup.microgrid_id)

    # Assert basic fields always present
    AssertionHelpers.assert_microgrid_basic_fields(result)

    # Assert optional fields based on parameters
    if has_delivery_area:
        AssertionHelpers.assert_delivery_area_present(result)
    else:
        AssertionHelpers.assert_delivery_area_absent(result)

    if has_location:
        AssertionHelpers.assert_location_present(result)
    else:
        AssertionHelpers.assert_location_absent(result)

    # Verify stub was called correctly
    mock_stub.GetMicrogrid.assert_called_once()


async def test_get_microgrid_details_basic_functionality(
    client_setup: ClientSetup,
) -> None:
    """Test basic successful microgrid details retrieval functionality."""
    client, mock_stub = client_setup.client, client_setup.mock_stub

    # Setup basic response without optional fields
    setup_microgrid_with_fields(
        client_setup.mock_microgrid,
        has_delivery_area=False,
        has_location=False,
    )
    response = create_microgrid_response(
        client_setup.mock_microgrid, client_setup.mock_response
    )
    mock_stub.GetMicrogrid.return_value = response

    # Execute
    result = await client.get_microgrid_details(client_setup.microgrid_id)

    # Assert
    AssertionHelpers.assert_microgrid_basic_fields(result)
    AssertionHelpers.assert_delivery_area_absent(result)
    AssertionHelpers.assert_location_absent(result)
    mock_stub.GetMicrogrid.assert_called_once()


async def test_get_microgrid_details_not_found(
    client_setup: ClientSetup,
) -> None:
    """Test get_microgrid_details when microgrid is not found."""
    client, mock_stub = client_setup.client, client_setup.mock_stub

    # Setup mock to raise NOT_FOUND error
    class MockAioRpcError(AioRpcError):  # pylint: disable=too-few-public-methods
        """Mock AioRpcError for testing NOT_FOUND scenarios."""

        def __init__(self) -> None:
            # Don't call super().__init__() # pylint: disable=super-init-not-called
            pass

        def code(self) -> StatusCode:
            return StatusCode.NOT_FOUND

        def details(self) -> str:
            return "Microgrid not found"

    mock_stub.GetMicrogrid.side_effect = MockAioRpcError()

    # Execute and assert exception is raised
    with pytest.raises(NotFoundError) as exc_info:
        await client.get_microgrid_details(client_setup.microgrid_id)

    # Assert exception details
    assert exc_info.value.resource_id == client_setup.microgrid_id
    assert exc_info.value.status_code == "NOT_FOUND"
    assert "not found" in exc_info.value.message.lower()

    # Verify stub was called correctly
    mock_stub.GetMicrogrid.assert_called_once()
