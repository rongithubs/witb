"""Unit tests for AuthService favorite player functionality following CLAUDE.md T-1."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from sqlalchemy.exc import IntegrityError

import schemas
import models
from auth.service import AuthService
from custom_types import UserId, PlayerId
from exceptions import PlayerNotFoundError, DatabaseOperationError


class TestAuthServiceFavorites:
    """Unit tests for AuthService favorite player methods."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def mock_favorite_repo(self):
        """Mock FavoritePlayerRepository."""
        return AsyncMock()

    @pytest.fixture
    def mock_player_service(self):
        """Mock PlayerService."""
        return AsyncMock()

    @pytest.fixture
    def auth_service(self, mock_db_session, mock_favorite_repo, mock_player_service):
        """Create AuthService with mocked dependencies."""
        service = AuthService(mock_db_session)
        service.favorite_repo = mock_favorite_repo
        return service

    @pytest.mark.asyncio
    async def test_add_favorite_player_success(
        self, auth_service, mock_favorite_repo, mock_player_service
    ):
        """Test adding favorite player succeeds with valid data."""
        # Arrange
        user_id = UserId(uuid4())
        player_id = PlayerId(uuid4())

        mock_player = MagicMock()
        mock_player.witb_items = []

        mock_favorite = MagicMock()
        mock_favorite.player = mock_player
        mock_favorite.id = uuid4()
        mock_favorite.created_at = "2025-01-01T00:00:00"

        # Mock PlayerService.get_player_by_id (validation)
        with patch("auth.service.PlayerService") as MockPlayerService:
            mock_service_instance = MockPlayerService.return_value
            mock_service_instance.get_player_by_id = AsyncMock(return_value=mock_player)

            mock_favorite_repo.add_favorite_player.return_value = mock_favorite

            # Act
            result = await auth_service.add_favorite_player(user_id, player_id)

            # Assert
            mock_favorite_repo.add_favorite_player.assert_called_once_with(
                user_id, player_id
            )
            assert isinstance(result, schemas.FavoritePlayerResponse)

    @pytest.mark.asyncio
    async def test_add_favorite_player_invalid_player_raises_error(
        self, auth_service, mock_favorite_repo
    ):
        """Test adding favorite with invalid player_id raises PlayerNotFoundError."""
        # Arrange
        user_id = UserId(uuid4())
        player_id = PlayerId(uuid4())

        # Mock PlayerService.get_player_by_id to raise PlayerNotFoundError
        with patch("auth.service.PlayerService") as MockPlayerService:
            mock_service_instance = MockPlayerService.return_value
            mock_service_instance.get_player_by_id = AsyncMock(
                side_effect=PlayerNotFoundError(str(player_id))
            )

            # Act & Assert
            with pytest.raises(PlayerNotFoundError):
                await auth_service.add_favorite_player(user_id, player_id)

            # Should not call repository if player doesn't exist
            mock_favorite_repo.add_favorite_player.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_favorite_player_duplicate_returns_existing(
        self, auth_service, mock_favorite_repo
    ):
        """Test adding duplicate favorite returns existing favorite."""
        # Arrange
        user_id = UserId(uuid4())
        player_id = PlayerId(uuid4())

        mock_player = MagicMock()
        mock_player.witb_items = []

        mock_favorite = MagicMock()
        mock_favorite.player = mock_player
        mock_favorite.player_id = player_id
        mock_favorite.id = uuid4()

        # Mock PlayerService validation
        with patch("auth.service.PlayerService") as MockPlayerService:
            mock_service_instance = MockPlayerService.return_value
            mock_service_instance.get_player_by_id = AsyncMock(return_value=mock_player)

            # Mock repository to raise IntegrityError then return existing
            mock_favorite_repo.add_favorite_player.side_effect = IntegrityError(
                "duplicate", None, None
            )
            mock_favorite_repo.get_user_favorites.return_value = [mock_favorite]

            # Act
            result = await auth_service.add_favorite_player(user_id, player_id)

            # Assert
            assert isinstance(result, schemas.FavoritePlayerResponse)
            mock_favorite_repo.get_user_favorites.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_remove_favorite_player_success(
        self, auth_service, mock_favorite_repo
    ):
        """Test removing favorite player returns True when successful."""
        # Arrange
        user_id = UserId(uuid4())
        player_id = PlayerId(uuid4())

        mock_favorite_repo.remove_favorite_player.return_value = True

        # Act
        result = await auth_service.remove_favorite_player(user_id, player_id)

        # Assert
        assert result is True
        mock_favorite_repo.remove_favorite_player.assert_called_once_with(
            user_id, player_id
        )

    @pytest.mark.asyncio
    async def test_remove_favorite_player_not_found(
        self, auth_service, mock_favorite_repo
    ):
        """Test removing non-existent favorite returns False."""
        # Arrange
        user_id = UserId(uuid4())
        player_id = PlayerId(uuid4())

        mock_favorite_repo.remove_favorite_player.return_value = False

        # Act
        result = await auth_service.remove_favorite_player(user_id, player_id)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_get_user_favorites_success(self, auth_service, mock_favorite_repo):
        """Test getting user favorites returns enriched data."""
        # Arrange
        user_id = UserId(uuid4())

        mock_player1 = MagicMock()
        mock_player1.witb_items = []
        mock_player2 = MagicMock()
        mock_player2.witb_items = []

        mock_fav1 = MagicMock()
        mock_fav1.player = mock_player1
        mock_fav1.id = uuid4()

        mock_fav2 = MagicMock()
        mock_fav2.player = mock_player2
        mock_fav2.id = uuid4()

        mock_favorite_repo.get_user_favorites.return_value = [mock_fav1, mock_fav2]

        # Act
        with patch("auth.service.PlayerService") as MockPlayerService:
            mock_service_instance = MockPlayerService.return_value

            result = await auth_service.get_user_favorites(user_id)

            # Assert
            assert isinstance(result, schemas.UserFavoritesResponse)
            assert result.total == 2
            assert len(result.favorites) == 2
            mock_favorite_repo.get_user_favorites.assert_called_once_with(user_id)

            # Should enrich WITB items for both players
            assert mock_service_instance._enrich_witb_items_with_urls.call_count == 2

    @pytest.mark.asyncio
    async def test_get_user_favorites_empty_list(
        self, auth_service, mock_favorite_repo
    ):
        """Test getting favorites for user with none returns empty response."""
        # Arrange
        user_id = UserId(uuid4())
        mock_favorite_repo.get_user_favorites.return_value = []

        # Act
        result = await auth_service.get_user_favorites(user_id)

        # Assert
        assert isinstance(result, schemas.UserFavoritesResponse)
        assert result.total == 0
        assert result.favorites == []
