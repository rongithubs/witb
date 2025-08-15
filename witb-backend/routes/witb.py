"""WITB routes following CLAUDE.md O-4 (thin route handlers)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from dependencies import get_db
from services.witb_service import WitbService

router = APIRouter(prefix="/witb", tags=["witb"])


@router.get("/leaderboard", response_model=schemas.LeaderboardResponse)
async def get_club_leaderboard(
    category: str | None = Query(None, description="Filter by club category"),
    limit: int = Query(10, ge=1, le=50, description="Limit results per category"),
    db: AsyncSession = Depends(get_db),
):
    """Get club usage leaderboard grouped by category."""
    service = WitbService(db)
    return await service.get_club_usage_leaderboard(
        category_filter=category, limit=limit
    )
