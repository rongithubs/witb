"""Unit tests for FavoritePlayerRepository following CLAUDE.md T-1."""

import pytest
import asyncio
from uuid import uuid4
from sqlalchemy.exc import IntegrityError

import models
from custom_types import UserId, PlayerId
from repositories.favorite_player_repository import FavoritePlayerRepository


class TestFavoritePlayerRepository:
    """Unit tests for FavoritePlayerRepository."""

    @pytest.mark.asyncio
    async def test_add_favorite_player_success(self, db_session):
        """Test adding player to favorites succeeds."""
        # Arrange
        repo = FavoritePlayerRepository(db_session)
        user_id = UserId(uuid4())
        player_id = PlayerId(uuid4())

        # Create user and player first
        user = models.User(
            id=user_id, supabase_user_id=uuid4(), email="test@example.com"
        )
        player = models.Player(id=player_id, name="Test Player", country="USA")
        db_session.add(user)
        db_session.add(player)
        await db_session.commit()

        # Act
        favorite = await repo.add_favorite_player(user_id, player_id)

        # Assert
        assert favorite.user_id == user_id
        assert favorite.player_id == player_id
        assert favorite.id is not None
        assert favorite.created_at is not None

    @pytest.mark.asyncio
    async def test_add_favorite_player_duplicate_raises_integrity_error(
        self, db_session
    ):
        """Test adding duplicate favorite raises IntegrityError."""
        # Arrange
        repo = FavoritePlayerRepository(db_session)
        user_id = UserId(uuid4())
        player_id = PlayerId(uuid4())

        # Create user and player
        user = models.User(
            id=user_id, supabase_user_id=uuid4(), email="test@example.com"
        )
        player = models.Player(id=player_id, name="Test Player", country="USA")
        db_session.add(user)
        db_session.add(player)
        await db_session.commit()

        # Add favorite once
        await repo.add_favorite_player(user_id, player_id)

        # Act & Assert - Should raise IntegrityError on duplicate
        with pytest.raises(IntegrityError):
            await repo.add_favorite_player(user_id, player_id)

    @pytest.mark.asyncio
    async def test_remove_favorite_player_success(self, db_session):
        """Test removing favorite player returns True when exists."""
        # Arrange
        repo = FavoritePlayerRepository(db_session)
        user_id = UserId(uuid4())
        player_id = PlayerId(uuid4())

        # Create user, player, and favorite
        user = models.User(
            id=user_id, supabase_user_id=uuid4(), email="test@example.com"
        )
        player = models.Player(id=player_id, name="Test Player", country="USA")
        favorite = models.FavoritePlayer(user_id=user_id, player_id=player_id)
        db_session.add_all([user, player, favorite])
        await db_session.commit()

        # Act
        result = await repo.remove_favorite_player(user_id, player_id)

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_remove_favorite_player_not_found(self, db_session):
        """Test removing non-existent favorite returns False."""
        # Arrange
        repo = FavoritePlayerRepository(db_session)
        user_id = UserId(uuid4())
        player_id = PlayerId(uuid4())

        # Act
        result = await repo.remove_favorite_player(user_id, player_id)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_get_user_favorites_returns_ordered_list(self, db_session):
        """Test getting user favorites returns list ordered by created_at desc."""
        # Arrange
        repo = FavoritePlayerRepository(db_session)
        user_id = UserId(uuid4())
        player1_id = PlayerId(uuid4())
        player2_id = PlayerId(uuid4())

        # Create user and players
        user = models.User(
            id=user_id, supabase_user_id=uuid4(), email="test@example.com"
        )
        player1 = models.Player(id=player1_id, name="Player One", country="USA")
        player2 = models.Player(id=player2_id, name="Player Two", country="USA")
        db_session.add_all([user, player1, player2])
        await db_session.commit()

        # Add favorites (player1 first, then player2 with slight delay)
        await repo.add_favorite_player(user_id, player1_id)
        await asyncio.sleep(0.001)  # Ensure different timestamps
        await repo.add_favorite_player(user_id, player2_id)

        # Act
        favorites = await repo.get_user_favorites(user_id)

        # Assert
        assert len(favorites) == 2
        # Should be ordered by created_at desc (player2 first)
        assert favorites[0].player_id == player2_id
        assert favorites[1].player_id == player1_id
        # Should have player data loaded
        assert favorites[0].player.name == "Player Two"
        assert favorites[1].player.name == "Player One"

    @pytest.mark.asyncio
    async def test_get_user_favorites_empty_list(self, db_session):
        """Test getting favorites for user with no favorites returns empty list."""
        # Arrange
        repo = FavoritePlayerRepository(db_session)
        user_id = UserId(uuid4())

        # Act
        favorites = await repo.get_user_favorites(user_id)

        # Assert
        assert favorites == []

    @pytest.mark.asyncio
    async def test_is_favorite_returns_true_when_exists(self, db_session):
        """Test is_favorite returns True when player is favorited."""
        # Arrange
        repo = FavoritePlayerRepository(db_session)
        user_id = UserId(uuid4())
        player_id = PlayerId(uuid4())

        # Create user, player, and favorite
        user = models.User(
            id=user_id, supabase_user_id=uuid4(), email="test@example.com"
        )
        player = models.Player(id=player_id, name="Test Player", country="USA")
        favorite = models.FavoritePlayer(user_id=user_id, player_id=player_id)
        db_session.add_all([user, player, favorite])
        await db_session.commit()

        # Act
        result = await repo.is_favorite(user_id, player_id)

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_is_favorite_returns_false_when_not_exists(self, db_session):
        """Test is_favorite returns False when player is not favorited."""
        # Arrange
        repo = FavoritePlayerRepository(db_session)
        user_id = UserId(uuid4())
        player_id = PlayerId(uuid4())

        # Act
        result = await repo.is_favorite(user_id, player_id)

        # Assert
        assert result is False
