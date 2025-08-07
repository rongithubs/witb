"""Player repository for database operations following CLAUDE.md D-4."""
from typing import Optional, List
from uuid import UUID
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, case

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
        player = result.scalars().first()
        
        # Sort WITB items if player exists
        if player and player.witb_items:
            player.witb_items = self._sort_witb_items(player.witb_items)
        
        return player

    async def get_players_paginated(
        self, 
        offset: int, 
        limit: int,
        tour: Optional[str] = None
    ) -> tuple[List[models.Player], int]:
        """Get paginated players with optional tour filter."""
        # Build base query
        base_query = select(models.Player)
        count_query = select(func.count(models.Player.id))
        
        # Apply tour filter if provided
        if tour:
            base_query = base_query.where(models.Player.tour == tour)
            count_query = count_query.where(models.Player.tour == tour)
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated players
        result = await self.db.execute(
            base_query
            .options(selectinload(models.Player.witb_items))
            .order_by(models.Player.ranking.nulls_last())
            .offset(offset)
            .limit(limit)
        )
        players = result.scalars().all()
        
        # Sort WITB items for each player from longest to shortest clubs
        for player in players:
            player.witb_items = self._sort_witb_items(player.witb_items)
        
        return players, total

    def _sort_witb_items(self, witb_items):
        """Sort WITB items from longest to shortest clubs following proper golf bag organization."""
        
        # Define club order from longest to shortest
        club_order = {
            'Driver': 1,
            'Mini Driver': 2,
            '3-Wood': 3,
            '5-Wood': 4,
            '7-Wood': 5,
            '9-Wood': 6,
            'Hybrid': 7,
            'Iron': 8,
            'Wedge': 9,
            'Putter': 10,
            'Ball': 11,
            'Grip': 12,
        }
        
        def sort_key(item):
            # Primary sort by club category
            primary = club_order.get(item.category, 99)
            
            # Secondary sort within same category
            if item.category == 'Iron':
                # For irons, try to extract iron number from model/loft
                model_text = f"{item.model} {item.loft or ''}".upper()
                if 'PW' in model_text or 'PITCHING' in model_text:
                    return (primary, 10)  # PW after 9 iron
                # Try to find iron number
                match = re.search(r'\b([4-9])\b', model_text)
                if match:
                    return (primary, int(match.group(1)))
                # Handle ranges like "5-PW"
                range_match = re.search(r'(\d+)-', model_text)
                if range_match:
                    return (primary, int(range_match.group(1)))
                return (primary, 99)
            
            elif item.category == 'Wedge':
                # For wedges, sort by loft degree
                if item.loft:
                    match = re.search(r'(\d+)', item.loft)
                    if match:
                        return (primary, int(match.group(1)))
                return (primary, 99)
            
            else:
                # For other categories, maintain original order within category
                return (primary, 0)
        
        return sorted(witb_items, key=sort_key)

    async def search_player_by_name(self, name: str) -> Optional[models.Player]:
        """Search for player by name."""
        result = await self.db.execute(
            select(models.Player).where(models.Player.name.ilike(name.strip()))
        )
        return result.scalars().first()