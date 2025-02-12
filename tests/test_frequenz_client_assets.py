# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for the frequenz.client.assets package."""
import pytest

from frequenz.client.assets import delete_me


def test_frequenz_client_assets_succeeds() -> None:  # TODO(cookiecutter): Remove
    """Test that the delete_me function succeeds."""
    assert delete_me() is True


def test_frequenz_client_assets_fails() -> None:  # TODO(cookiecutter): Remove
    """Test that the delete_me function fails."""
    with pytest.raises(RuntimeError, match="This function should be removed!"):
        delete_me(blow_up=True)
