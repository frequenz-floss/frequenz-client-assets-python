# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Type definitions for the Assets API client.

This module contains the core data types used by the Assets API client,
including data classes for representing assets, microgrids, and related entities.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from frequenz.api.common.v1alpha8.grid.delivery_area_pb2 import (
    DeliveryArea as PBDeliveryArea,
)
from frequenz.api.common.v1alpha8.microgrid.microgrid_pb2 import (
    Microgrid as PBMicrogrid,
)
from frequenz.api.common.v1alpha8.types.location_pb2 import Location as PBLocation
from frequenz.client.common.microgrid import EnterpriseId, MicrogridId


@dataclass(frozen=True)
class DeliveryArea:
    """A wrapper class for the protobuf DeliveryArea message.

    A delivery area is a geographical area that is served by a microgrid.
    """

    code: str
    code_type: str

    @staticmethod
    def from_protobuf(pb: PBDeliveryArea) -> "DeliveryArea":
        """
        Create a DeliveryArea instance from a protobuf message.

        Args:
            pb: The protobuf DeliveryArea message.

        Returns:
            A new DeliveryArea instance populated with data from the protobuf message.
        """
        return DeliveryArea(code=pb.code, code_type=str(pb.code_type))

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the DeliveryArea instance to a dictionary.

        Returns:
            A dictionary containing the delivery area details.
        """
        return {"code": self.code, "code_type": self.code_type}


@dataclass(frozen=True)
class Location:
    """A wrapper class for the protobuf Location message.

    A location is a geographical location that is served by a microgrid.
    """

    latitude: float
    longitude: float
    country_code: str

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the Location instance to a dictionary.

        Returns:
            A dictionary containing the location details.
        """
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "country_code": self.country_code,
        }

    @staticmethod
    def from_protobuf(pb: PBLocation) -> "Location":
        """
        Create a Location instance from a protobuf message.

        Args:
            pb: The protobuf Location message.

        Returns:
            A new Location instance populated with data from the protobuf message.
        """
        return Location(
            latitude=pb.latitude, longitude=pb.longitude, country_code=pb.country_code
        )


@dataclass(frozen=True)
class Microgrid:
    """A wrapper class for the protobuf Microgrid message.

    A microgrid is a localized group of electricity sources and loads that normally
    operates connected to and synchronous with the traditional wide area electrical
    grid (macrogrid), but is able to disconnect from the grid and operate autonomously.

    Attributes:
        id: Unique identifier for the microgrid.
        enterprise_id: ID of the enterprise that owns this microgrid.
        name: Human-readable name for the microgrid.
        delivery_area_code: Code identifying the delivery area.
        delivery_area_code_type: Type of delivery area code.
        latitude: Geographic latitude coordinate.
        longitude: Geographic longitude coordinate.
        country_code: ISO country code where the microgrid is located.
        status: Current operational status of the microgrid.
        create_time: Timestamp when the microgrid was created.
    """

    id: MicrogridId
    enterprise_id: EnterpriseId
    name: str
    delivery_area: Optional[DeliveryArea]
    location: Optional[Location]
    status: int
    create_time: datetime

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the Microgrid instance to a dictionary.

        Returns:
            A dictionary containing the microgrid details.
        """
        return {
            "id": int(self.id),
            "enterprise_id": int(self.enterprise_id),
            "name": self.name,
            "delivery_area": (
                self.delivery_area.to_dict() if self.delivery_area else None
            ),
            "location": self.location.to_dict() if self.location else None,
            "status": self.status,
            "create_time": self.create_time.isoformat() if self.create_time else None,
        }

    @staticmethod
    def from_protobuf(pb: PBMicrogrid) -> "Microgrid":
        """
        Create a Microgrid instance from a protobuf message.

        Args:
            pb: The protobuf Microgrid message.

        Returns:
            A new Microgrid instance populated with data from the protobuf message.
        """
        delivery_area: Optional[DeliveryArea] = None
        if pb.HasField("delivery_area"):
            delivery_area = DeliveryArea.from_protobuf(pb.delivery_area)

        location: Optional[Location] = None
        if pb.HasField("location"):
            location = Location.from_protobuf(pb.location)

        return Microgrid(
            id=MicrogridId(pb.id),
            enterprise_id=EnterpriseId(pb.enterprise_id),
            name=pb.name,
            delivery_area=delivery_area,
            location=location,
            status=pb.status,
            create_time=pb.create_timestamp.ToDatetime().replace(tzinfo=timezone.utc),
        )
