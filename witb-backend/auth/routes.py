"""Auth routes following CLAUDE.md O-4 (thin route handlers)."""

from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from auth.dependencies import get_current_user_from_db
from auth.service import AuthService
from custom_types import UserId, PlayerId
from dependencies import get_db


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/me", response_model=schemas.User)
async def get_current_user_info(
    current_user: schemas.User = Depends(get_current_user_from_db),
) -> schemas.User:
    """Get current authenticated user information."""
    return current_user


@router.get("/health")
async def auth_health_check() -> Dict[str, str]:
    """Auth health check endpoint."""
    return {"status": "auth_healthy", "message": "Authentication system is running"}


@router.post("/verify-token")
async def verify_token(
    current_user: schemas.User = Depends(get_current_user_from_db),
) -> Dict[str, Any]:
    """Verify if the provided token is valid."""
    return {
        "valid": True,
        "user_id": str(current_user.id),
        "supabase_user_id": str(current_user.supabase_user_id),
    }


@router.get("/me/favorites", response_model=schemas.UserFavoritesResponse)
async def get_user_favorites(
    current_user: schemas.User = Depends(get_current_user_from_db),
    db: AsyncSession = Depends(get_db),
) -> schemas.UserFavoritesResponse:
    """Get current user's favorite players."""
    service = AuthService(db)
    return await service.get_user_favorites(UserId(current_user.id))


@router.post("/me/favorites", response_model=schemas.FavoritePlayerResponse)
async def add_favorite_player(
    request: schemas.FavoritePlayerRequest,
    current_user: schemas.User = Depends(get_current_user_from_db),
    db: AsyncSession = Depends(get_db),
) -> schemas.FavoritePlayerResponse:
    """Add player to current user's favorites."""
    service = AuthService(db)
    return await service.add_favorite_player(
        UserId(current_user.id), PlayerId(request.player_id)
    )


@router.delete("/me/favorites/{player_id}")
async def remove_favorite_player(
    player_id: str,
    current_user: schemas.User = Depends(get_current_user_from_db),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Remove player from current user's favorites."""
    try:
        from uuid import UUID

        player_uuid = UUID(player_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid player ID format: {player_id}",
        )

    service = AuthService(db)
    removed = await service.remove_favorite_player(
        UserId(current_user.id), PlayerId(player_uuid)
    )

    if removed:
        return {"message": "Player removed from favorites"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found in favorites",
        )
