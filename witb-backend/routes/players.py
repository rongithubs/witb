"""Player routes following CLAUDE.md O-4 (thin route handlers)."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from dependencies import get_db
from services.player_service import PlayerService

router = APIRouter(prefix="/players", tags=["players"])


@router.post("/", response_model=schemas.Player)
async def create_player(
    player: schemas.PlayerCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Create a new player."""
    service = PlayerService(db)
    return await service.create_player(player)


@router.get("", response_model=schemas.PaginatedPlayersResponse)
async def get_players(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    tour: Optional[str] = Query(None, description="Filter by tour (e.g., 'PGA Tour', 'OGWR', 'LPGA Tour')"),
    db: AsyncSession = Depends(get_db)
):
    """Get paginated players with optional tour filter."""
    service = PlayerService(db)
    return await service.get_players_paginated(page, per_page, tour)


@router.get("/search")
async def search_player(
    name: str = Query(...), 
    db: AsyncSession = Depends(get_db)
):
    """Search for player by name."""
    service = PlayerService(db)
    exists = await service.search_player_exists(name)
    return {"exists": exists}


@router.get("/{player_id}", response_model=schemas.Player)
async def get_player(
    player_id: str, 
    db: AsyncSession = Depends(get_db)
):
    """Get player by ID."""
    service = PlayerService(db)
    return await service.get_player_by_id(player_id)


@router.post("/{player_id}/witb_items/", response_model=schemas.WITBItem)
async def add_witb_item(
    player_id: str,
    item: schemas.WITBItemCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add WITB item to player."""
    service = PlayerService(db)
    return await service.add_witb_item(player_id, item)