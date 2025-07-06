"""Player repository for database operations following CLAUDE.md D-4."""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

import models
from custom_types import PlayerId


class PlayerRepository:
    """Repository for player database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_player(self, player_data: dict) -> models.Player:
        """Create a new player."""
        new_player = models.Player(**player_data)
        self.db.add(new_player)
        try:
            await self.db.commit()
            await self.db.refresh(new_player)
            return new_player
        except IntegrityError:
            await self.db.rollback()
            raise

    async def get_player_by_id(self, player_id: PlayerId) -> Optional[models.Player]:
        """Get player by ID with WITB items."""
        result = await self.db.execute(
            select(models.Player)
            .where(models.Player.id == player_id)
            .options(selectinload(models.Player.witb_items))
        )
        return result.scalars().first()

    async def get_players_paginated(
        self, 
        offset: int, 
        limit: int
    ) -> tuple[List[models.Player], int]:
        """Get paginated players with total count."""
        # Get total count
        total_result = await self.db.execute(select(func.count(models.Player.id)))
        total = total_result.scalar()
        
        # Get paginated players
        result = await self.db.execute(
            select(models.Player)
            .options(selectinload(models.Player.witb_items))
            .order_by(models.Player.ranking.nulls_last())
            .offset(offset)
            .limit(limit)
        )
        players = result.scalars().all()
        
        return players, total

    async def search_player_by_name(self, name: str) -> Optional[models.Player]:
        """Search for player by name."""
        result = await self.db.execute(
            select(models.Player).where(models.Player.name.ilike(name.strip()))
        )
        return result.scalars().first()