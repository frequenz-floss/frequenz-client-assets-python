# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Centralized test data and constants."""

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class MockData:  # pylint: disable=too-many-instance-attributes
    """Central place for all test data constants."""

    # Microgrid data
    microgrid_id: int = 123
    enterprise_id: int = 456
    microgrid_name: str = "Test Microgrid"
    microgrid_status: int = 1
    create_date: datetime = datetime(2023, 1, 1, tzinfo=timezone.utc)

    # Delivery area data
    delivery_area_code: str = "TEST_AREA"
    delivery_area_type: str = "TEST_TYPE"

    # Location data
    latitude: float = 52.5200
    longitude: float = 13.4050
    country_code: str = "DE"

    # Server config
    server_url: str = "grpc://test.example.com:443"
    auth_key: str = "test-key"
    sign_secret: str = "test-secret"
