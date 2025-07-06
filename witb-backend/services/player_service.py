"""Player service for business logic following CLAUDE.md O-4."""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from exceptions import PlayerNotFoundError, InvalidPlayerIdError, PlayerAlreadyExistsError

import schemas
import models
from repositories.player_repository import PlayerRepository
from repositories.witb_repository import WITBRepository
from brand_urls import get_brand_url
from custom_types import PlayerId


class PlayerService:
    """Service for player business logic."""
    
    def __init__(self, db: AsyncSession):
        self.player_repo = PlayerRepository(db)
        self.witb_repo = WITBRepository(db)
        self.db = db

    def _enrich_witb_items_with_urls(self, items: List[models.WITBItem]) -> List[models.WITBItem]:
        """Add brand URLs to WITB items that don't have specific product URLs."""
        for item in items:
            if not item.product_url and item.brand:
                item.product_url = get_brand_url(item.brand)
        return items

    async def create_player(self, player_data: schemas.PlayerCreate) -> schemas.Player:
        """Create a new player."""
        try:
            new_player = await self.player_repo.create_player(player_data.model_dump())
            return schemas.Player.model_validate(new_player)
        except IntegrityError:
            raise PlayerAlreadyExistsError(player_data.name)

    async def get_player_by_id(self, player_id: str) -> schemas.Player:
        """Get player by ID with enriched WITB items."""
        try:
            player_uuid = UUID(player_id)
        except ValueError:
            raise InvalidPlayerIdError(player_id)
        
        player = await self.player_repo.get_player_by_id(PlayerId(player_uuid))
        if not player:
            raise PlayerNotFoundError(player_id)
        
        # Enrich WITB items with brand URLs
        self._enrich_witb_items_with_urls(player.witb_items)
        
        return schemas.Player.model_validate(player)

    async def get_players_paginated(
        self, 
        page: int, 
        per_page: int
    ) -> schemas.PaginatedPlayersResponse:
        """Get paginated players with enriched WITB items."""
        offset = (page - 1) * per_page
        
        players, total = await self.player_repo.get_players_paginated(offset, per_page)
        
        # Enrich WITB items with brand URLs
        for player in players:
            self._enrich_witb_items_with_urls(player.witb_items)
        
        # Calculate total pages
        total_pages = (total + per_page - 1) // per_page
        
        return schemas.PaginatedPlayersResponse(
            items=[schemas.Player.model_validate(p) for p in players],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )

    async def search_player_exists(self, name: str) -> bool:
        """Check if player exists by name."""
        player = await self.player_repo.search_player_by_name(name)
        return bool(player)

    async def add_witb_item(
        self, 
        player_id: str, 
        item_data: schemas.WITBItemCreate
    ) -> schemas.WITBItem:
        """Add WITB item to player."""
        try:
            player_uuid = UUID(player_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid player ID format")
        
        # Verify player exists
        player = await self.player_repo.get_player_by_id(PlayerId(player_uuid))
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")

        try:
            db_item = await self.witb_repo.create_witb_item(
                PlayerId(player_uuid), 
                item_data.model_dump()
            )
            return schemas.WITBItem.model_validate(db_item)
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail=f"Error: {str(e)}")