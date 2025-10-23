# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test for the Assets API client."""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from frequenz.api.assets.v1 import assets_pb2_grpc

from frequenz.client.assets import AssetsApiClient

from .util import ApiClientTestCaseSpec, get_test_specs, patch_client_class

TESTS_DIR = Path(__file__).parent / "client_test_cases"


@pytest.fixture
async def client() -> AsyncIterator[AssetsApiClient]:
    """Fixture that provides a AssetsApiClient with a mock gRPC stub and channel."""
    with patch_client_class(AssetsApiClient, assets_pb2_grpc.PlatformAssetsStub):
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
