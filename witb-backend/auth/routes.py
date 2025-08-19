"""Auth routes following CLAUDE.md O-4 (thin route handlers)."""

from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from auth.dependencies import get_current_user_from_db
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
