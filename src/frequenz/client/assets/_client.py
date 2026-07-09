# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""
Assets API client.

This module provides a client for the Assets API.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from enum import Enum
from typing import TypeVar

from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)
from frequenz.api.platformassets.v1alpha1 import (
    platformassets_pb2,
    platformassets_pb2_grpc,
)
from frequenz.client.base import channel
from frequenz.client.base.client import BaseApiClient, call_stub_method
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.electrical_components import ElectricalComponentId
from frequenz.client.common.microgrid.sensors import SensorId

from ._delivery_area import DeliveryArea
from ._delivery_area_proto import delivery_area_to_proto
from ._gridpool import Gridpool
from ._gridpool_energy_schedule import (
    GridpoolEnergySchedule,
    GridpoolEnergyScheduleDirection,
)
from ._gridpool_energy_schedule_proto import gridpool_energy_schedule_from_proto
from ._gridpool_proto import gridpool_from_proto
from ._interval import Interval
from ._interval_proto import interval_to_proto
from ._market_location_proto import market_location_id_value_to_proto
from ._market_topology import MarketParticipationType, MarketTopologyRelation
from ._market_topology_proto import market_topology_relation_from_proto
from ._microgrid import Microgrid
from ._microgrid_proto import microgrid_from_proto, microgrid_from_proto_with_issues
from ._sensor import Sensor
from ._sensor_proto import sensor_from_proto
from .electrical_component._category import ElectricalComponentCategory
from .electrical_component._connection import ComponentConnection
from .electrical_component._connection_proto import (
    component_connection_from_proto,
    component_connection_from_proto_with_issues,
)
from .electrical_component._electrical_component import ElectricalComponent
from .electrical_component._electrical_component_proto import (
    electrical_component_from_proto_with_issues,
    electrical_component_proto,
)
from .exceptions import (
    ClientNotConnected,
    InvalidConnectionError,
    InvalidElectricalComponentError,
    InvalidMicrogridError,
)

DEFAULT_GRPC_CALL_TIMEOUT = 60.0
"""The default timeout for gRPC calls made by this client (in seconds)."""

_ProtoEnumValue = TypeVar("_ProtoEnumValue", bound=int)


def _enum_value(value: Enum | int) -> int:
    """Return the integer value for an enum or integer filter argument."""
    return value.value if isinstance(value, Enum) else value


def _proto_enum_values(
    values: Iterable[Enum | int],
    value_type: Callable[[int], _ProtoEnumValue],
) -> list[_ProtoEnumValue]:
    """Return protobuf enum values for enum or integer filter arguments."""
    return [value_type(_enum_value(value)) for value in values]


class AssetsApiClient(
    BaseApiClient[platformassets_pb2_grpc.PlatformAssetsServiceStub]
):  # pylint: disable=too-many-arguments
    """A client for the Assets API."""

    def __init__(
        self,
        server_url: str,
        *,
        auth_key: str | None = None,
        sign_secret: str | None = None,
        channel_defaults: channel.ChannelOptions = channel.ChannelOptions(),
        connect: bool = True,
    ) -> None:
        """
        Initialize the AssetsApiClient.

        Args:
            server_url: The location of the microgrid API server in the form of a URL.
                The following format is expected:
                "grpc://hostname{:`port`}{?ssl=`ssl`}",
                where the `port` should be an int between 0 and 65535 (defaulting to
                9090) and `ssl` should be a boolean (defaulting to `true`).
                For example: `grpc://localhost:1090?ssl=true`.
            auth_key: The authentication key to use for the connection.
            sign_secret: The secret to use for signing requests.
            channel_defaults: The default options use to create the channel when not
                specified in the URL.
            connect: Whether to connect to the server as soon as a client instance is
                created. If `False`, the client will not connect to the server until
                [connect()][frequenz.client.base.client.BaseApiClient.connect] is
                called.
        """
        super().__init__(
            server_url,
            platformassets_pb2_grpc.PlatformAssetsServiceStub,
            connect=connect,
            channel_defaults=channel_defaults,
            auth_key=auth_key,
            sign_secret=sign_secret,
        )

    @property
    def stub(self) -> platformassets_pb2_grpc.PlatformAssetsServiceAsyncStub:
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

    async def list_gridpools(  # noqa: DOC502 (raises indirectly)
        self,
        gridpool_ids: Iterable[int] = (),
    ) -> list[Gridpool]:
        """
        List gridpools within the current enterprise scope.

        Args:
            gridpool_ids: Only return gridpools whose IDs are included in this list.
                If empty, no filtering is applied.

        Returns:
            The matching gridpools.

        Raises:
            ApiClientError: If there are any errors communicating with the Assets API,
                most likely a subclass of [GrpcError][frequenz.client.base.exception.GrpcError].
        """
        request = platformassets_pb2.ListGridpoolsRequest()
        if ids := [int(gridpool_id) for gridpool_id in gridpool_ids]:
            request.filter.gridpool_ids.extend(ids)

        response = await call_stub_method(
            self,
            lambda: self.stub.ListGridpools(
                request,
                timeout=DEFAULT_GRPC_CALL_TIMEOUT,
            ),
            method_name="ListGridpools",
        )

        return [gridpool_from_proto(gridpool) for gridpool in response.gridpools]

    async def list_gridpool_energy_schedules(  # noqa: DOC502 (raises indirectly)
        self,
        gridpool_id: int,
        schedule_ids: Iterable[int] = (),
        directions: Iterable[GridpoolEnergyScheduleDirection | int] = (),
        *,
        time_series_interval: Interval | None = None,
        effective_validity_period: Interval | None = None,
    ) -> list[GridpoolEnergySchedule]:
        """
        List energy schedules for a gridpool.

        Args:
            gridpool_id: The ID of the gridpool whose schedules should be listed.
            schedule_ids: Only return schedules whose IDs are included in this list.
                If empty, no schedule-ID filtering is applied.
            directions: Only return schedules with one of these directions. If empty,
                no direction filtering is applied.
            time_series_interval: Restrict returned time-series entries to delivery
                periods that overlap this interval.
            effective_validity_period: Only return schedules whose effective validity
                period overlaps this interval.

        Returns:
            The matching gridpool energy schedules.

        Raises:
            ApiClientError: If there are any errors communicating with the Assets API,
                most likely a subclass of [GrpcError][frequenz.client.base.exception.GrpcError].
        """
        request = platformassets_pb2.ListGridpoolEnergySchedulesRequest(
            gridpool_id=int(gridpool_id),
        )
        if ids := [int(schedule_id) for schedule_id in schedule_ids]:
            request.filter.schedule_ids.extend(ids)
        if direction_values := _proto_enum_values(
            directions,
            platformassets_pb2.GridpoolEnergyScheduleDirection.ValueType,
        ):
            request.filter.directions.extend(direction_values)
        if time_series_interval is not None:
            request.filter.time_series_interval.CopyFrom(
                interval_to_proto(time_series_interval)
            )
        if effective_validity_period is not None:
            request.filter.effective_validity_period.CopyFrom(
                interval_to_proto(effective_validity_period)
            )

        response = await call_stub_method(
            self,
            lambda: self.stub.ListGridpoolEnergySchedules(
                request,
                timeout=DEFAULT_GRPC_CALL_TIMEOUT,
            ),
            method_name="ListGridpoolEnergySchedules",
        )

        return [
            gridpool_energy_schedule_from_proto(schedule)
            for schedule in response.schedules
        ]

    async def list_market_topology_relations(  # noqa: DOC502 (raises indirectly)
        self,
        *,
        gridpool_ids: Iterable[int] = (),
        microgrid_ids: Iterable[MicrogridId] = (),
        market_location_id_values: Iterable[str] = (),
        delivery_areas: Iterable[DeliveryArea] = (),
        participation_types: Iterable[MarketParticipationType | int] = (),
    ) -> list[MarketTopologyRelation]:
        """
        List market-topology relations within the current enterprise scope.

        Args:
            gridpool_ids: Only return relations involving any of these gridpools.
            microgrid_ids: Only return relations involving any of these microgrids.
            market_location_id_values: Only return relations involving market
                locations whose ID values match any of these values.
            delivery_areas: Only return relations applying to any of these delivery
                areas.
            participation_types: Only return relations that include at least one
                participation with one of these types.

        Returns:
            The matching market-topology relations.

        Raises:
            ApiClientError: If there are any errors communicating with the Assets API,
                most likely a subclass of [GrpcError][frequenz.client.base.exception.GrpcError].
        """
        request = platformassets_pb2.ListMarketTopologyRelationsRequest()
        if ids := [int(gridpool_id) for gridpool_id in gridpool_ids]:
            request.filter.gridpool_ids.extend(ids)
        if ids := [int(microgrid_id) for microgrid_id in microgrid_ids]:
            request.filter.microgrid_ids.extend(ids)
        if values := [
            market_location_id_value_to_proto(value)
            for value in market_location_id_values
        ]:
            request.filter.market_location_id_values.extend(values)
        if areas := [delivery_area_to_proto(area) for area in delivery_areas]:
            request.filter.delivery_areas.extend(areas)
        if types := _proto_enum_values(
            participation_types,
            platformassets_pb2.MarketParticipationType.ValueType,
        ):
            request.filter.participation_types.extend(types)

        response = await call_stub_method(
            self,
            lambda: self.stub.ListMarketTopologyRelations(
                request,
                timeout=DEFAULT_GRPC_CALL_TIMEOUT,
            ),
            method_name="ListMarketTopologyRelations",
        )

        return [
            market_topology_relation_from_proto(relation)
            for relation in response.relations
        ]

    async def get_microgrid(  # noqa: DOC502,DOC503 (raises indirectly)
        self,
        microgrid_id: MicrogridId,
        *,
        raise_on_errors: bool = False,
    ) -> Microgrid:
        """
        Get the details of a microgrid.

        Args:
            microgrid_id: The ID of the microgrid to get the details of.
            raise_on_errors: If True, raise an
                [InvalidMicrogridError][frequenz.client.assets.exceptions.InvalidMicrogridError]
                when major validation issues are found instead of just
                logging them.

        Returns:
            The details of the microgrid.

        Raises:
            ApiClientError: If there are any errors communicating with the Assets API,
                most likely a subclass of [GrpcError][frequenz.client.base.exception.GrpcError].
            InvalidMicrogridError: If `raise_on_errors` is True and major
                validation issues are found.
        """
        response = await call_stub_method(
            self,
            lambda: self.stub.GetMicrogrid(
                platformassets_pb2.GetMicrogridRequest(microgrid_id=int(microgrid_id)),
                timeout=DEFAULT_GRPC_CALL_TIMEOUT,
            ),
            method_name="GetMicrogrid",
        )

        if raise_on_errors:
            major_issues: list[str] = []
            minor_issues: list[str] = []
            microgrid = microgrid_from_proto_with_issues(
                response.microgrid,
                major_issues=major_issues,
                minor_issues=minor_issues,
            )
            if major_issues:
                raise InvalidMicrogridError(
                    microgrid=microgrid,
                    major_issues=major_issues,
                    minor_issues=minor_issues,
                    raw_message=response.microgrid,
                )
            return microgrid

        return microgrid_from_proto(response.microgrid)

    async def list_microgrids(  # noqa: DOC502,DOC503 (raises indirectly)
        self,
        microgrid_ids: Iterable[MicrogridId] = (),
        gridpool_ids: Iterable[int] = (),
        *,
        raise_on_errors: bool = False,
    ) -> list[Microgrid]:
        """
        List microgrids within the current enterprise scope.

        Args:
            microgrid_ids: Only return microgrids whose IDs are included in this list.
                If empty, no microgrid-ID filtering is applied.
            gridpool_ids: Only return microgrids that are part of a market-topology
                relation involving any of these gridpools.
            raise_on_errors: If True, raise an `ExceptionGroup[InvalidMicrogridError]`
                when major validation issues are found in any microgrid instead of
                just logging them.

        Returns:
            The matching microgrids.

        Raises:
            ApiClientError: If there are any errors communicating with the Assets API,
                most likely a subclass of [GrpcError][frequenz.client.base.exception.GrpcError].
            ExceptionGroup: If `raise_on_errors` is True and major validation
                issues are found. All exceptions in the group are
                [InvalidMicrogridError][frequenz.client.assets.exceptions.InvalidMicrogridError].
        """
        request = platformassets_pb2.ListMicrogridsRequest()
        if ids := [int(microgrid_id) for microgrid_id in microgrid_ids]:
            request.filter.microgrid_ids.extend(ids)
        if ids := [int(gridpool_id) for gridpool_id in gridpool_ids]:
            request.filter.gridpool_ids.extend(ids)

        response = await call_stub_method(
            self,
            lambda: self.stub.ListMicrogrids(
                request,
                timeout=DEFAULT_GRPC_CALL_TIMEOUT,
            ),
            method_name="ListMicrogrids",
        )

        if raise_on_errors:
            microgrids: list[Microgrid] = []
            exceptions: list[InvalidMicrogridError] = []
            for microgrid_pb in response.microgrids:
                major_issues: list[str] = []
                minor_issues: list[str] = []
                microgrid = microgrid_from_proto_with_issues(
                    microgrid_pb,
                    major_issues=major_issues,
                    minor_issues=minor_issues,
                )
                if major_issues:
                    exceptions.append(
                        InvalidMicrogridError(
                            microgrid=microgrid,
                            major_issues=major_issues,
                            minor_issues=minor_issues,
                            raw_message=microgrid_pb,
                        )
                    )
                else:
                    microgrids.append(microgrid)
            if exceptions:
                raise ExceptionGroup(
                    f"{len(exceptions)} microgrid(s) failed validation",
                    exceptions,
                )
            return microgrids

        return [microgrid_from_proto(microgrid) for microgrid in response.microgrids]

    async def list_microgrid_electrical_components(
        self,
        microgrid_id: MicrogridId,
        component_ids: Iterable[ElectricalComponentId] = (),
        categories: Iterable[ElectricalComponentCategory | int] = (),
        *,
        raise_on_errors: bool = False,
    ) -> list[ElectricalComponent]:
        """
        Get the electrical components of a microgrid.

        Args:
            microgrid_id: The ID of the microgrid to get the electrical components of.
            component_ids: Only return components whose IDs are included in this list.
                If empty, no component-ID filtering is applied.
            categories: Only return components whose categories are included in this
                list. If empty, no category filtering is applied.
            raise_on_errors: If True, raise an
                `ExceptionGroup[InvalidElectricalComponentError]`
                when major validation issues are found in any component instead
                of just logging them.

        Returns:
            The electrical components of the microgrid.

        Raises:
            ExceptionGroup: If `raise_on_errors` is True and major validation
                issues are found. All exceptions in the group are
                [InvalidElectricalComponentError][frequenz.client.assets.exceptions.InvalidElectricalComponentError].
        """
        request = platformassets_pb2.ListMicrogridElectricalComponentsRequest(
            microgrid_id=int(microgrid_id),
        )
        if ids := [int(component_id) for component_id in component_ids]:
            request.filter.component_ids.extend(ids)
        if category_values := _proto_enum_values(
            categories,
            electrical_components_pb2.ElectricalComponentCategory.ValueType,
        ):
            request.filter.categories.extend(category_values)

        response = await call_stub_method(
            self,
            lambda: self.stub.ListMicrogridElectricalComponents(
                request,
                timeout=DEFAULT_GRPC_CALL_TIMEOUT,
            ),
            method_name="ListMicrogridElectricalComponents",
        )

        if raise_on_errors:
            components: list[ElectricalComponent] = []
            exceptions: list[InvalidElectricalComponentError] = []
            for component_pb in response.components:
                major_issues: list[str] = []
                minor_issues: list[str] = []
                component = electrical_component_from_proto_with_issues(
                    component_pb,
                    major_issues=major_issues,
                    minor_issues=minor_issues,
                )
                if major_issues:
                    exceptions.append(
                        InvalidElectricalComponentError(
                            component=component,
                            major_issues=major_issues,
                            minor_issues=minor_issues,
                            raw_message=component_pb,
                        )
                    )
                else:
                    components.append(component)
            if exceptions:
                raise ExceptionGroup(
                    f"{len(exceptions)} electrical component(s) failed validation",
                    exceptions,
                )
            return components

        return [
            electrical_component_proto(component) for component in response.components
        ]

    async def list_microgrid_electrical_component_connections(
        self,
        microgrid_id: MicrogridId,
        source_component_ids: Iterable[ElectricalComponentId] = (),
        destination_component_ids: Iterable[ElectricalComponentId] = (),
        *,
        raise_on_errors: bool = False,
    ) -> list[ComponentConnection]:
        """
        Get the electrical component connections of a microgrid.

        Args:
            microgrid_id: The ID of the microgrid to get the electrical
                component connections of.
            source_component_ids: Only return connections that originate from
                these component IDs. If None or empty, no filtering is applied.
            destination_component_ids: Only return connections that terminate at
                these component IDs. If None or empty, no filtering is applied.
            raise_on_errors: If True, raise an
                `ExceptionGroup[InvalidConnectionError]`
                when major validation issues are found in any connection instead
                of just logging them.

        Returns:
            The electrical component connections of the microgrid.

        Raises:
            ExceptionGroup: If `raise_on_errors` is True and major validation
                issues are found. All exceptions in the group are
                [InvalidConnectionError][frequenz.client.assets.exceptions.InvalidConnectionError].
        """
        source_ids = [int(c) for c in source_component_ids]
        destination_ids = [int(c) for c in destination_component_ids]
        request = platformassets_pb2.ListMicrogridElectricalComponentConnectionsRequest(
            microgrid_id=int(microgrid_id),
        )
        if source_ids or destination_ids:
            request.filter.source_component_ids.extend(source_ids)
            request.filter.destination_component_ids.extend(destination_ids)

        response = await call_stub_method(
            self,
            lambda: self.stub.ListMicrogridElectricalComponentConnections(
                request,
                timeout=DEFAULT_GRPC_CALL_TIMEOUT,
            ),
            method_name="ListMicrogridElectricalComponentConnections",
        )

        if raise_on_errors:
            valid_connections: list[ComponentConnection] = []
            exceptions: list[InvalidConnectionError] = []
            for conn_pb in filter(bool, response.connections):
                major_issues: list[str] = []
                connection = component_connection_from_proto_with_issues(
                    conn_pb, major_issues=major_issues
                )
                if major_issues:
                    exceptions.append(
                        InvalidConnectionError(
                            connection=connection,
                            major_issues=major_issues,
                            minor_issues=[],
                            raw_message=conn_pb,
                        )
                    )
                elif connection is not None:
                    valid_connections.append(connection)
            if exceptions:
                raise ExceptionGroup(
                    f"{len(exceptions)} connection(s) failed validation",
                    exceptions,
                )
            return valid_connections

        return [
            c
            for c in map(component_connection_from_proto, response.connections)
            if c is not None
        ]

    async def list_microgrid_sensors(  # noqa: DOC502 (raises indirectly)
        self,
        microgrid_id: MicrogridId,
        sensor_ids: Iterable[SensorId] = (),
    ) -> list[Sensor]:
        """
        List sensors in a microgrid.

        Args:
            microgrid_id: The ID of the microgrid whose sensors should be listed.
            sensor_ids: Only return sensors whose IDs are included in this list. If
                empty, no filtering is applied.

        Returns:
            The matching sensors.

        Raises:
            ApiClientError: If there are any errors communicating with the Assets API,
                most likely a subclass of [GrpcError][frequenz.client.base.exception.GrpcError].
        """
        request = platformassets_pb2.ListMicrogridSensorsRequest(
            microgrid_id=int(microgrid_id),
        )
        if ids := [int(sensor_id) for sensor_id in sensor_ids]:
            request.filter.sensor_ids.extend(ids)

        response = await call_stub_method(
            self,
            lambda: self.stub.ListMicrogridSensors(
                request,
                timeout=DEFAULT_GRPC_CALL_TIMEOUT,
            ),
            method_name="ListMicrogridSensors",
        )

        return [sensor_from_proto(sensor) for sensor in response.sensors]
