"""Unit tests for WITB sync service following CLAUDE.md T-1."""

from datetime import datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

import models
from custom_types import PlayerId
from services.scraper_service import EquipmentItem, WITBData
from services.witb_sync_service import SyncAction, WITBSyncService


class TestWITBSyncService:
    """Unit tests for WITB synchronization service."""

    def test_should_update_with_newer_data(self):
        """Test that sync identifies when scraped data is newer."""
        sync_service = WITBSyncService(Mock())

        # Existing data is older
        existing_date = datetime(2025, 1, 1)
        scraped_date = datetime(2025, 1, 15)

        should_update = sync_service._should_update_data(existing_date, scraped_date)
        assert should_update is True

    def test_should_not_update_with_older_data(self):
        """Test that sync skips when scraped data is older."""
        sync_service = WITBSyncService(Mock())

        # Existing data is newer
        existing_date = datetime(2025, 1, 15)
        scraped_date = datetime(2025, 1, 1)

        should_update = sync_service._should_update_data(existing_date, scraped_date)
        assert should_update is False

    def test_should_update_when_no_existing_data(self):
        """Test that sync updates when no existing last_updated date."""
        sync_service = WITBSyncService(Mock())

        should_update = sync_service._should_update_data(None, datetime(2025, 1, 15))
        assert should_update is True

    def test_should_not_update_when_no_scraped_date(self):
        """Test that sync skips when scraped data has no date."""
        sync_service = WITBSyncService(Mock())

        should_update = sync_service._should_update_data(datetime(2025, 1, 1), None)
        assert should_update is False

    def test_convert_scraped_to_witb_items(self):
        """Test conversion from scraped data to WITBItem models."""
        sync_service = WITBSyncService(Mock())
        player_id = PlayerId(uuid4())
        source_url = "https://example.com/player-witb"

        scraped_equipment = [
            EquipmentItem(
                category="Driver",
                brand="TaylorMade",
                model="Stealth 2",
                loft="9°",
                shaft="Fujikura Ventus",
            ),
            EquipmentItem(category="Putter", brand="Scotty Cameron", model="Newport 2"),
        ]

        result = sync_service._convert_to_witb_items(
            scraped_equipment, player_id, source_url
        )

        assert len(result) == 2

        # First item
        assert result[0].category == "Driver"
        assert result[0].brand == "TaylorMade"
        assert result[0].model == "Stealth 2"
        assert result[0].loft == "9°"
        assert result[0].shaft == "Fujikura Ventus"
        assert result[0].player_id == player_id
        assert result[0].source_url == source_url

        # Second item with None values
        assert result[1].category == "Putter"
        assert result[1].brand == "Scotty Cameron"
        assert result[1].model == "Newport 2"
        assert result[1].loft is None
        assert result[1].shaft is None

    @pytest.mark.asyncio
    async def test_sync_player_equipment_updates_newer_data(self):
        """Test that sync updates when scraped data is newer."""
        mock_player_repo = AsyncMock()
        mock_witb_repo = AsyncMock()

        sync_service = WITBSyncService(Mock())
        sync_service.player_repo = mock_player_repo
        sync_service.witb_repo = mock_witb_repo

        # Mock existing player with older data
        player_id = PlayerId(uuid4())
        existing_player = models.Player(
            id=player_id, name="Test Player", last_updated=datetime(2025, 1, 1)
        )
        mock_player_repo.get_player_by_id.return_value = existing_player

        # Mock scraped data with newer date
        scraped_data = WITBData(
            last_updated=datetime(2025, 1, 15),
            equipment=[EquipmentItem("Driver", "TaylorMade", "Stealth 2")],
            source_url="https://example.com",
        )

        result = await sync_service.sync_player_equipment(player_id, scraped_data)

        assert result.action == SyncAction.UPDATED
        assert result.items_count == 1
        assert result.message is not None

        # Verify repos were called
        mock_player_repo.update_player.assert_called_once()
        mock_witb_repo.replace_player_equipment.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_player_equipment_skips_older_data(self):
        """Test that sync skips when scraped data is older."""
        mock_player_repo = AsyncMock()
        sync_service = WITBSyncService(Mock())
        sync_service.player_repo = mock_player_repo

        # Mock existing player with newer data
        player_id = PlayerId(uuid4())
        existing_player = models.Player(
            id=player_id, name="Test Player", last_updated=datetime(2025, 1, 15)
        )
        mock_player_repo.get_player_by_id.return_value = existing_player

        # Mock scraped data with older date
        scraped_data = WITBData(
            last_updated=datetime(2025, 1, 1),
            equipment=[],
            source_url="https://example.com",
        )

        result = await sync_service.sync_player_equipment(player_id, scraped_data)

        assert result.action == SyncAction.SKIPPED
        assert result.message.startswith("Existing data is newer")

        # Verify no updates were made
        mock_player_repo.update_player.assert_not_called()

    @pytest.mark.asyncio
    async def test_sync_player_equipment_handles_missing_player(self):
        """Test that sync handles when player is not found."""
        mock_player_repo = AsyncMock()
        sync_service = WITBSyncService(Mock())
        sync_service.player_repo = mock_player_repo

        # Mock player not found
        mock_player_repo.get_player_by_id.return_value = None

        scraped_data = WITBData(
            last_updated=datetime(2025, 1, 15),
            equipment=[],
            source_url="https://example.com",
        )

        result = await sync_service.sync_player_equipment(
            PlayerId(uuid4()), scraped_data
        )

        assert result.action == SyncAction.ERROR
        assert "Player not found" in result.message
