# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Client for requests to the PlatformAssets API."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Optional

# pylint: disable=no-name-in-module
from frequenz.api.assets.v1.assets_pb2 import (
    GetMicrogridRequest as PBGetMicrogridRequest,
)
from frequenz.api.assets.v1.assets_pb2 import (
    GetMicrogridResponse as PBGetMicrogridResponse,
)
from frequenz.api.assets.v1.assets_pb2 import (
    ListMicrogridElectricalComponentConnectionsRequest as PBLMECCRequest,
)
from frequenz.api.assets.v1.assets_pb2 import (
    ListMicrogridElectricalComponentConnectionsResponse as PBLMECCResponse,
)
from frequenz.api.assets.v1.assets_pb2 import (
    ListMicrogridElectricalComponentsRequest as PBListMicrogridElectricalComponentsRequest,
)
from frequenz.api.assets.v1.assets_pb2 import (
    ListMicrogridElectricalComponentsResponse as PBListMicrogridElectricalComponentsResponse,
)
from frequenz.api.assets.v1.assets_pb2_grpc import PlatformAssetsStub
from frequenz.api.common.v1.grid.delivery_area_pb2 import DeliveryArea as PBDeliveryArea
from frequenz.api.common.v1.grid.delivery_area_pb2 import (
    EnergyMarketCodeType as PBEnergyMarketCodeType,
)
from frequenz.api.common.v1.location_pb2 import Location as PBLocation
from frequenz.api.common.v1.microgrid.electrical_components.electrical_components_pb2 import (
    ElectricalComponent as PBElectricalComponent,
)
from frequenz.api.common.v1.microgrid.electrical_components.electrical_components_pb2 import (
    ElectricalComponentCategory as PBElectricalComponentCategory,
)
from frequenz.api.common.v1.microgrid.electrical_components.electrical_components_pb2 import (
    ElectricalComponentCategorySpecificInfo as PBElectricalComponentCategorySpecificInfo,
)
from frequenz.api.common.v1.microgrid.electrical_components.electrical_components_pb2 import (
    ElectricalComponentConnection as PBElectricalComponentConnection,
)
from frequenz.api.common.v1.microgrid.microgrid_pb2 import Microgrid as PBMicrogrid
from frequenz.api.common.v1.microgrid.microgrid_pb2 import (
    MicrogridStatus as PBMicrogridStatus,
)
from frequenz.client.base.client import BaseApiClient, call_stub_method
from frequenz.client.base.exception import ClientNotConnected

# pylint: enable=no-name-in-module


# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True)
class Microgrid:
    """Structured wrapper for a microgrid object.

    Attributes:
        id: The ID of the microgrid.
        enterprise_id: The ID of the enterprise that owns the microgrid.
        name: The name of the microgrid.
        delivery_area_code: The code of the delivery area.
        delivery_area_code_type: The type of the delivery area code.
        latitude: The latitude of the microgrid.
        longitude: The longitude of the microgrid.
        country_code: The country code of the microgrid.
        status: The status of the microgrid.
        create_time: The timestamp when the microgrid was created.
    """

    id: int
    enterprise_id: int
    name: str
    delivery_area_code: str | None
    delivery_area_code_type: str | None
    latitude: float | None
    longitude: float | None
    country_code: str | None
    status: str
    create_time: datetime

    @staticmethod
    def from_proto(pb: PBMicrogrid) -> "Microgrid":
        """Convert a protobuf Microgrid object to a Microgrid dataclass."""
        delivery_area: Optional[PBDeliveryArea] = (
            pb.delivery_area if pb.HasField("delivery_area") else None
        )
        location: Optional[PBLocation] = (
            pb.location if pb.HasField("location") else None
        )
        return Microgrid(
            id=pb.id,
            enterprise_id=pb.enterprise_id,
            name=pb.name,
            delivery_area_code=delivery_area.code if delivery_area else None,
            delivery_area_code_type=(
                PBEnergyMarketCodeType.Name(delivery_area.code_type)
                if delivery_area
                else None
            ),
            latitude=location.latitude if location else None,
            longitude=location.longitude if location else None,
            country_code=location.country_code if location else None,
            status=PBMicrogridStatus.Name(pb.status),
            create_time=pb.create_timestamp.ToDatetime().replace(tzinfo=timezone.utc),
        )


# pylint: disable=too-many-instance-attributes
@dataclass
class ElectricalComponent:
    """Structured wrapper for an electrical component object.

    Attributes:
        id: The ID of the electrical component.
        microgrid_id: The ID of the microgrid this component belongs to.
        name: The name of the electrical component.
        category: The category of the electrical component.
        category_specific_info: Specific information about the component's category.
        manufacturer: The manufacturer of the electrical component.
        model_name: The model name of the electrical component.
        control_mode: The control mode of the electrical component.
        start_time: The start time of the component's operational lifetime.
        end_time: The end time of the component's operational lifetime.
        metric_config_bounds: Configuration bounds for metrics associated
        with the component.
    """

    id: int
    microgrid_id: int
    name: str
    category: str
    category_specific_info: dict[str, Any]
    manufacturer: str
    model_name: str
    control_mode: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    metric_config_bounds: list[dict[str, Any]]

    @classmethod
    def from_proto(cls, pb: PBElectricalComponent) -> "ElectricalComponent":
        """Convert a protobuf object to an ElectricalComponent dataclass."""
        category_specific_info = cls._parse_category_specific_info(
            pb.category_specific_info
        )
        lifetime = pb.operational_lifetime
        metric_bounds = [
            {
                "metric": b.metric.name,
                "lower_bound": (
                    b.config_bounds.lower.value
                    if b.config_bounds.HasField("lower")
                    else None
                ),
                "upper_bound": (
                    b.config_bounds.upper.value
                    if b.config_bounds.HasField("upper")
                    else None
                ),
            }
            for b in pb.metric_config_bounds
        ]

        return cls(
            id=pb.id,
            microgrid_id=pb.microgrid_id,
            name=pb.name,
            category=PBElectricalComponentCategory.Name(pb.category),
            category_specific_info=category_specific_info,
            manufacturer=pb.manufacturer,
            model_name=pb.model_name,
            control_mode=(
                pb.control_mode.name
                if hasattr(pb, "control_mode") and pb.control_mode is not None
                else "ELECTRICAL_COMPONENT_CONTROL_MODE_UNSPECIFIED"
            ),
            start_time=(
                lifetime.start_timestamp.ToDatetime()
                if lifetime.HasField("start_timestamp")
                else None
            ),
            end_time=(
                lifetime.end_timestamp.ToDatetime()
                if lifetime.HasField("end_timestamp")
                else None
            ),
            metric_config_bounds=metric_bounds,
        )

    @staticmethod
    def _parse_category_specific_info(
        variant: PBElectricalComponentCategorySpecificInfo,
    ) -> dict[str, Any]:
        field = variant.WhichOneof("kind")
        if field is None:
            return {}
        return {"kind": field}


@dataclass
class ElectricalComponentConnection:
    """Structured wrapper for an electrical component connection object."""

    source_component_id: int
    destination_component_id: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]

    @classmethod
    def from_proto(
        cls, pb: PBElectricalComponentConnection
    ) -> "ElectricalComponentConnection":
        """Convert a protobuf object to an ElectricalComponentConnection dataclass."""
        lifetime = pb.operational_lifetime
        return cls(
            source_component_id=pb.source_component_id,
            destination_component_id=pb.destination_component_id,
            start_time=(
                lifetime.start_timestamp.ToDatetime()
                if lifetime.HasField("start_timestamp")
                else None
            ),
            end_time=(
                lifetime.end_timestamp.ToDatetime()
                if lifetime.HasField("end_timestamp")
                else None
            ),
        )


class AssetsApiClient(BaseApiClient[PlatformAssetsStub]):
    """A client for the Frequenz PlatformAssets service."""

    def __init__(
        self, server_url: str, key: str | None = None, connect: bool = True
    ) -> None:
        """Initialize the client.

        Args:
            server_url: The URL of the PlatformAssets service.
            key: The API key for authentication (optional).
            connect: Whether to establish a connection immediately.
        """
        super().__init__(server_url, PlatformAssetsStub, connect=connect)

        self._metadata = [("key", key)] if key else []

    @property
    def stub(self) -> PlatformAssetsStub:
        """Return the gRPC stub for the PlatformAssets service."""
        if self.channel is None or self._stub is None:
            raise ClientNotConnected(server_url=self.server_url, operation="stub")
        return self._stub

    async def get_microgrid_details(self, microgrid_id: int) -> Microgrid:
        """Fetch and parse a microgrid as a Microgrid dataclass."""
        pb_microgrid = await self._get_microgrid(microgrid_id)
        return Microgrid.from_proto(pb_microgrid)

    async def _get_microgrid(self, microgrid_id: int) -> PBMicrogrid:
        """Fetch details of a specific microgrid."""
        request = PBGetMicrogridRequest(microgrid_id=microgrid_id)

        response: PBGetMicrogridResponse = await call_stub_method(
            self, lambda: self.stub.GetMicrogrid(request, metadata=self._metadata)
        )
        return response.microgrid

    async def list_electrical_components(
        self,
        microgrid_id: int,
        component_ids: Optional[list[int]] = None,
        categories: Optional[Iterable[PBElectricalComponentCategory.ValueType]] = None,
    ) -> list[ElectricalComponent]:
        """List electrical components of a microgrid by iterating over component IDs.

        Args:
            microgrid_id: The ID of the microgrid to fetch components for.
            component_ids: The individual component IDs to fetch.
            categories: Optional categories to filter by.

        Returns:
            A list of ElectricalComponent dataclass instances.
        """
        request = PBListMicrogridElectricalComponentsRequest(
            microgrid_id=microgrid_id,
            component_ids=component_ids,
            categories=categories,
        )

        pb_response: PBListMicrogridElectricalComponentsResponse = (
            await call_stub_method(
                self,
                lambda: self.stub.ListMicrogridElectricalComponents(
                    request, metadata=self._metadata
                ),
            )
        )

        return [
            ElectricalComponent.from_proto(pb_component)
            for pb_component in pb_response.components
        ]

    async def list_microgrid_component_connections(
        self,
        microgrid_id: int,
        source_component_ids: Optional[list[int]] = None,
        destination_component_ids: Optional[list[int]] = None,
    ) -> list[ElectricalComponentConnection]:
        """List electrical connections between components in a microgrid.

        Args:
            microgrid_id: The ID of the microgrid to fetch component connections for.
            source_component_ids: The IDs of the source components to fetch connections for.
            destination_component_ids: The IDs of the destination components to fetch
                                    connections for.

        Returns:
            A list of ElectricalComponentConnection dataclass instances.
        """
        request = PBLMECCRequest(
            microgrid_id=microgrid_id,
            source_component_ids=source_component_ids,
            destination_component_ids=destination_component_ids,
        )

        pb_response: PBLMECCResponse = await call_stub_method(
            self,
            lambda: self.stub.ListMicrogridElectricalComponentConnections(
                request, metadata=self._metadata
            ),
        )

        return [
            ElectricalComponentConnection.from_proto(pb_conn)
            for pb_conn in pb_response.connections
        ]
