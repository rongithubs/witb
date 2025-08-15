"""Unit tests for PlayerService following CLAUDE.md testing guidelines."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

import models
import schemas
from services.player_service import PlayerService


class TestPlayerService:
    """Unit tests for PlayerService following CLAUDE.md T-7."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def player_service(self, mock_db):
        """PlayerService instance with mocked dependencies."""
        service = PlayerService(mock_db)
        service.player_repo = AsyncMock()
        service.witb_repo = AsyncMock()
        return service

    def test_enrich_witb_items_with_urls_adds_brand_urls(self, player_service):
        """Test that _enrich_witb_items_with_urls adds brand URLs when missing."""
        # Arrange
        mock_item = MagicMock()
        mock_item.product_url = None
        mock_item.brand = "TaylorMade"
        items = [mock_item]

        # Act
        result = player_service._enrich_witb_items_with_urls(items)

        # Assert
        assert result == items
        assert mock_item.product_url is not None

    def test_enrich_witb_items_with_urls_preserves_existing_urls(self, player_service):
        """Test that existing product URLs are preserved."""
        # Arrange
        existing_url = "https://example.com/product"
        mock_item = MagicMock()
        mock_item.product_url = existing_url
        mock_item.brand = "TaylorMade"
        items = [mock_item]

        # Act
        result = player_service._enrich_witb_items_with_urls(items)

        # Assert
        assert mock_item.product_url == existing_url

    async def test_create_player_success(self, player_service):
        """Test successful player creation."""
        # Arrange
        player_data = schemas.PlayerCreate(
            name="Test Player", country="USA", tour="PGA Tour", age=25, ranking=1
        )
        mock_player = models.Player(
            id=uuid4(),
            name="Test Player",
            country="USA",
            tour="PGA Tour",
            age=25,
            ranking=1,
        )
        player_service.player_repo.create_player.return_value = mock_player

        # Act
        result = await player_service.create_player(player_data)

        # Assert
        assert isinstance(result, schemas.Player)
        assert result.name == "Test Player"
        player_service.player_repo.create_player.assert_called_once()

    async def test_get_player_by_id_invalid_uuid_raises_http_exception(
        self, player_service
    ):
        """Test that invalid UUID raises HTTPException with 400 status."""
        # Arrange
        invalid_id = "not-a-uuid"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await player_service.get_player_by_id(invalid_id)

        # The HTTPException should be raised for invalid UUID
        assert (
            "Invalid player ID format" in str(exc_info.value)
            or exc_info.value.status_code == 400
        )

    async def test_search_player_exists_returns_boolean(self, player_service):
        """Test that search_player_exists returns proper boolean."""
        # Arrange
        test_name = "Test Player"
        player_service.player_repo.search_player_by_name.return_value = models.Player()

        # Act
        result = await player_service.search_player_exists(test_name)

        # Assert
        assert result is True
        player_service.player_repo.search_player_by_name.assert_called_once_with(
            test_name
        )
