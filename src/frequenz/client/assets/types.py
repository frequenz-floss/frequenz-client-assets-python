# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Type definitions for the Assets API client.

This module contains the core data types used by the Assets API client,
including data classes for representing assets, microgrids, and related entities.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone

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
        return DeliveryArea(
            code=pb.code,
            code_type=str(pb.code_type),
        )


@dataclass(frozen=True)
class Location:
    """A wrapper class for the protobuf Location message.

    A location is a geographical location that is served by a microgrid.
    """

    latitude: float
    longitude: float
    country_code: str

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
            latitude=pb.latitude,
            longitude=pb.longitude,
            country_code=pb.country_code,
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
    delivery_area: DeliveryArea | None
    location: Location | None
    status: int
    create_time: datetime

    @staticmethod
    def from_protobuf(pb: PBMicrogrid) -> "Microgrid":
        """
        Create a Microgrid instance from a protobuf message.

        Args:
            pb: The protobuf Microgrid message.

        Returns:
            A new Microgrid instance populated with data from the protobuf message.
        """
        delivery_area: DeliveryArea = None
        if pb.HasField("delivery_area"):
            delivery_area = DeliveryArea.from_protobuf(pb.delivery_area)

        location: Location = None
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

    def to_json(self) -> str:
        """Convert the Microgrid instance to a JSON string."""
        microgrid_dict = asdict(self)
        microgrid_dict["id"] = int(self.id)
        microgrid_dict["enterprise_id"] = int(self.enterprise_id)
        microgrid_dict["create_time"] = self.create_time.isoformat()

        return json.dumps(microgrid_dict, indent=2)
