# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Helper functions for common assertions."""

from frequenz.client.assets.types import Microgrid

from .test_data import MockData


def assert_microgrid_basic_fields(
    result: Microgrid,
    expected_id: int = MockData.microgrid_id,
    expected_enterprise_id: int = MockData.enterprise_id,
    expected_name: str = MockData.microgrid_name,
) -> None:
    """Assert basic microgrid fields are correct."""
    assert str(result.id) == f"MID{expected_id}"
    assert str(result.enterprise_id) == f"EID{expected_enterprise_id}"
    assert result.name == expected_name


def assert_delivery_area_present(
    result: Microgrid, expected_code: str = MockData.delivery_area_code
) -> None:
    """Assert delivery area is present and correct."""
    assert result.delivery_area is not None
    assert result.delivery_area.code == expected_code


def assert_delivery_area_absent(result: Microgrid) -> None:
    """Assert delivery area is not present."""
    assert result.delivery_area is None


def assert_location_present(
    result: Microgrid,
    expected_country: str = MockData.country_code,
    expected_latitude: float = MockData.latitude,
) -> None:
    """Assert location is present and correct."""
    assert result.location is not None
    assert result.location.country_code == expected_country
    assert result.location.latitude == expected_latitude


def assert_location_absent(result: Microgrid) -> None:
    """Assert location is not present."""
    assert result.location is None
