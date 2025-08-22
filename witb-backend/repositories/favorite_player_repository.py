"""Favorite player repository for database operations following CLAUDE.md D-4."""

from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from custom_types import UserId, PlayerId, FavoritePlayerId


class FavoritePlayerRepository:
    """Repository for favorite player database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_favorite_player(
        self, user_id: UserId, player_id: PlayerId
    ) -> models.FavoritePlayer:
        """Add player to user's favorites."""
        favorite = models.FavoritePlayer(user_id=user_id, player_id=player_id)
        self.db.add(favorite)
        try:
            await self.db.commit()
            await self.db.refresh(favorite)
            return favorite
        except IntegrityError:
            await self.db.rollback()
            raise

    async def remove_favorite_player(
        self, user_id: UserId, player_id: PlayerId
    ) -> bool:
        """Remove player from user's favorites. Returns True if removed, False if not found."""
        result = await self.db.execute(
            select(models.FavoritePlayer).where(
                and_(
                    models.FavoritePlayer.user_id == user_id,
                    models.FavoritePlayer.player_id == player_id,
                )
            )
        )
        favorites = result.scalars().all()

        if favorites:
            # Remove all duplicate favorites (in case there are any)
            for favorite in favorites:
                await self.db.delete(favorite)
            await self.db.commit()
            return True
        return False

    async def get_user_favorites(self, user_id: UserId) -> list[models.FavoritePlayer]:
        """Get user's favorite players with player data loaded."""
        result = await self.db.execute(
            select(models.FavoritePlayer)
            .where(models.FavoritePlayer.user_id == user_id)
            .options(selectinload(models.FavoritePlayer.player))
            .order_by(models.FavoritePlayer.created_at.desc())
        )
        return list(result.scalars().all())

    async def is_favorite(self, user_id: UserId, player_id: PlayerId) -> bool:
        """Check if player is in user's favorites."""
        result = await self.db.execute(
            select(models.FavoritePlayer.id).where(
                and_(
                    models.FavoritePlayer.user_id == user_id,
                    models.FavoritePlayer.player_id == player_id,
                )
            )
        )
        return result.scalar_one_or_none() is not None
