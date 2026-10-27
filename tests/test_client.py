# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test for the Assets API client."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)
from frequenz.api.platformassets.v1alpha1 import (
    platformassets_pb2,
    platformassets_pb2_grpc,
)
from frequenz.client.common.microgrid import MicrogridId

from frequenz.client.assets import AssetsApiClient
from frequenz.client.assets.electrical_component import (
    ElectricalComponentOperationalMode,
)
from frequenz.client.assets.electrical_component._electrical_component_json import (
    electrical_components_to_json,
)

from .util import ApiClientTestCaseSpec, get_test_specs, patch_client_class

TESTS_DIR = Path(__file__).parent / "client_test_cases"


@pytest.fixture
async def client() -> AsyncIterator[AssetsApiClient]:
    """Fixture that provides a AssetsApiClient with a mock gRPC stub and channel."""
    with patch_client_class(
        AssetsApiClient, platformassets_pb2_grpc.PlatformAssetsServiceStub
    ):
        client = AssetsApiClient("grpc://localhost:1234")
        async with client:
            yield client


@pytest.mark.parametrize(
    "spec",
    get_test_specs("get_microgrid", tests_dir=TESTS_DIR),
    ids=str,
)
async def test_get_microgrid(
    client: AssetsApiClient, spec: ApiClientTestCaseSpec
) -> None:
    """Test get_microgrid method."""
    await spec.test_unary_unary_call(client, "GetMicrogrid")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "spec",
    get_test_specs("list_gridpools", tests_dir=TESTS_DIR),
    ids=str,
)
async def test_list_gridpools(
    client: AssetsApiClient, spec: ApiClientTestCaseSpec
) -> None:
    """Test list_gridpools method."""
    await spec.test_unary_unary_call(client, "ListGridpools")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "spec",
    get_test_specs("list_gridpool_energy_schedules", tests_dir=TESTS_DIR),
    ids=str,
)
async def test_list_gridpool_energy_schedules(
    client: AssetsApiClient, spec: ApiClientTestCaseSpec
) -> None:
    """Test list_gridpool_energy_schedules method."""
    await spec.test_unary_unary_call(client, "ListGridpoolEnergySchedules")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "spec",
    get_test_specs("list_market_topology_relations", tests_dir=TESTS_DIR),
    ids=str,
)
async def test_list_market_topology_relations(
    client: AssetsApiClient, spec: ApiClientTestCaseSpec
) -> None:
    """Test list_market_topology_relations method."""
    await spec.test_unary_unary_call(client, "ListMarketTopologyRelations")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "spec",
    get_test_specs("list_microgrids", tests_dir=TESTS_DIR),
    ids=str,
)
async def test_list_microgrids(
    client: AssetsApiClient, spec: ApiClientTestCaseSpec
) -> None:
    """Test list_microgrids method."""
    await spec.test_unary_unary_call(client, "ListMicrogrids")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "spec",
    get_test_specs("list_microgrid_electrical_components", tests_dir=TESTS_DIR),
    ids=str,
)
async def test_list_microgrid_electrical_components(
    client: AssetsApiClient, spec: ApiClientTestCaseSpec
) -> None:
    """Test list_microgrid_electrical_components method."""
    await spec.test_unary_unary_call(client, "ListMicrogridElectricalComponents")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "spec",
    get_test_specs(
        "list_microgrid_electrical_component_connections", tests_dir=TESTS_DIR
    ),
    ids=str,
)
async def test_list_connections(
    client: AssetsApiClient, spec: ApiClientTestCaseSpec
) -> None:
    """Test list_connections method."""
    await spec.test_unary_unary_call(
        client, "ListMicrogridElectricalComponentConnections"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "spec",
    get_test_specs("list_microgrid_sensors", tests_dir=TESTS_DIR),
    ids=str,
)
async def test_list_microgrid_sensors(
    client: AssetsApiClient, spec: ApiClientTestCaseSpec
) -> None:
    """Test list_microgrid_sensors method."""
    await spec.test_unary_unary_call(client, "ListMicrogridSensors")


@pytest.mark.parametrize("raise_on_errors", [False, True])
@pytest.mark.parametrize(
    ("proto_mode", "expected_mode"),
    [
        (0, ElectricalComponentOperationalMode.UNSPECIFIED),
        (1, ElectricalComponentOperationalMode.INACTIVE),
        (2, ElectricalComponentOperationalMode.TELEMETRY_ONLY),
        (3, ElectricalComponentOperationalMode.CONTROL_ONLY),
        (4, ElectricalComponentOperationalMode.CONTROL_AND_TELEMETRY),
        (99, 99),
    ],
)
async def test_list_components_operational_mode(
    client: AssetsApiClient,
    proto_mode: int,
    expected_mode: ElectricalComponentOperationalMode | int,
    raise_on_errors: bool,
) -> None:
    """Return requested modes in both validation paths and preserve unknown values."""
    proto_mode_type = electrical_components_pb2.ElectricalComponentOperationalMode
    client.stub.ListMicrogridElectricalComponents = AsyncMock(
        return_value=platformassets_pb2.ListMicrogridElectricalComponentsResponse(
            components=[
                electrical_components_pb2.ElectricalComponent(
                    id=1,
                    microgrid_id=1234,
                    category=electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_STEAM_BOILER,
                    operational_mode=proto_mode_type.ValueType(proto_mode),
                )
            ]
        )
    )

    components = await client.list_microgrid_electrical_components(
        MicrogridId(1234), raise_on_errors=raise_on_errors
    )

    assert len(components) == 1
    assert components[0].operational_mode == expected_mode
    component_json = json.loads(electrical_components_to_json(components))[0]
    assert component_json["operational_mode"] == proto_mode
    assert set(component_json) == {
        "id",
        "microgrid_id",
        "name",
        "category",
        "manufacturer",
        "model_name",
        "operational_lifetime",
        "rated_bounds",
        "operational_mode",
    }
