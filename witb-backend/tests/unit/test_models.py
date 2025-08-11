"""Unit tests for database models following CLAUDE.md T-1."""

from datetime import datetime
from uuid import uuid4
import pytest

import models


class TestPlayer:
    """Unit tests for Player model."""

    def test_player_has_last_updated_field(self):
        """Test that Player model has last_updated field."""
        player = models.Player(name="Test Player", country="USA", tour="PGA Tour")

        # Should have last_updated field
        assert hasattr(player, "last_updated")

        # Should be able to set last_updated
        test_datetime = datetime(2025, 1, 15, 12, 0, 0)
        player.last_updated = test_datetime
        assert player.last_updated == test_datetime


class TestWITBItem:
    """Unit tests for WITBItem model."""

    def test_witb_item_has_source_url_field(self):
        """Test that WITBItem model has source_url field."""
        player_id = uuid4()
        witb_item = models.WITBItem(
            player_id=player_id,
            category="Driver",
            brand="TaylorMade",
            model="Stealth 2",
            source_url="https://www.pgaclubtracker.com/players/test-player-witb",
        )

        # Should have source_url field
        assert hasattr(witb_item, "source_url")
        assert (
            witb_item.source_url
            == "https://www.pgaclubtracker.com/players/test-player-witb"
        )

    def test_witb_item_source_url_optional(self):
        """Test that source_url field is optional."""
        player_id = uuid4()
        witb_item = models.WITBItem(
            player_id=player_id,
            category="Driver",
            brand="TaylorMade",
            model="Stealth 2",
        )

        # source_url should be optional
        assert witb_item.source_url is None
