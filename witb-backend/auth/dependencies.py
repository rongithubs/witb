"""Auth dependencies for FastAPI following CLAUDE.md FA-3."""

from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from auth.service import AuthService
from custom_types import SupabaseUserId
from dependencies import get_db


security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> schemas.AuthUser:
    """Get current authenticated user from JWT token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        auth_service = AuthService(db)
        auth_user = auth_service.verify_jwt_token(credentials.credentials)
        return auth_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_from_db(
    auth_user: schemas.AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> schemas.User:
    """Get current user from database, creating if doesn't exist."""
    auth_service = AuthService(db)

    # Get or create user in our database
    user = await auth_service.get_or_create_user(
        supabase_user_id=SupabaseUserId(auth_user.supabase_user_id),
        user_data={
            "email": auth_user.email,
            "phone": auth_user.phone,
        },
    )

    return user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Optional[schemas.User]:
    """Get current user if authenticated, None otherwise."""
    if not credentials:
        return None

    try:
        auth_service = AuthService(db)
        auth_user = auth_service.verify_jwt_token(credentials.credentials)

        user = await auth_service.get_or_create_user(
            supabase_user_id=SupabaseUserId(auth_user.supabase_user_id),
            user_data={
                "email": auth_user.email,
                "phone": auth_user.phone,
            },
        )
        return user
    except (ValueError, HTTPException):
        return None
